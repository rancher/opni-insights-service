# Standard Library
import logging
import os

import pandas as pd

# Third Party
from elasticsearch import AsyncElasticsearch
from elasticsearch.helpers import async_scan
from fastapi import FastAPI
from kubernetes import client, config
from real_time_peak_detection import real_time_peak_detection

app = FastAPI()
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(message)s")

ES_ENDPOINT = os.environ["ES_ENDPOINT"]
ES_USERNAME = os.environ["ES_USERNAME"]
ES_PASSWORD = os.environ["ES_PASSWORD"]
es_instance = AsyncElasticsearch(
    [ES_ENDPOINT],
    port=9200,
    http_compress=True,
    http_auth=(ES_USERNAME, ES_PASSWORD),
    verify_certs=False,
    use_ssl=True,
)
WINDOW = int(os.environ["WINDOW"])
THRESHOLD = float(os.environ["THRESHOLD"])
INFLUENCE = float(os.environ["INFLUENCE"])
rtpd_model = real_time_peak_detection(WINDOW, THRESHOLD, INFLUENCE)
minute_ms = 60000
peak_data_dict = dict()

config.load_incluster_config()
configuration = client.Configuration()
core_api_instance = client.CoreV1Api()
app_api_instance = client.AppsV1Api()

def get_all_pod_names(all_pods_items):
    # Get all current pod names from Kubernetes API.
    pod_storage_dict = dict()
    for pod_spec in all_pods_items:
        pod_metadata = pod_spec.metadata
        pod_name = pod_metadata.name
        pod_storage_dict[pod_name] = {
            "Insights": {"Normal": 0, "Suspicious": 0, "Anomaly": 0}
        }

    return pod_storage_dict


async def get_pod_breakdown(start_ts, end_ts):
    # Get the breakdown of normal, suspicious and anomalous logs by pod.
    pod_breakdown_dict = {"Pods": []}
    # Try accessing the list of all pods through the Kubernetesa API. If unsuccessful, return the pod_breakdown_dict object in its bare bone structure.
    try:
        all_pods = core_api_instance.list_pod_for_all_namespaces(watch=False)
        all_pods_items = all_pods.items
    except Exception as e:
        logging.error(f"Unable to obtain pod data. {e}")
        return pod_breakdown_dict

    try:
        pod_storage_dict = get_all_pod_names(all_pods_items)
    except Exception as e:
        logging.error(f"Unable to obtain pod data. {e}")
        return pod_breakdown_dict

    query_body = {
        "size": 0,
        "query": {
            "bool": {
                "must": [{"match": {"is_control_plane_log": "false"}}],
                "filter": [{"range": {"timestamp": {"gte": start_ts, "lte": end_ts}}}],
            }
        },
        "aggs": {
            "pod_name": {
                "terms": {"field": "kubernetes.pod_name.keyword"},
                "aggs": {
                    "anomaly_level": {"terms": {"field": "anomaly_level.keyword"}}
                },
            }
        },
    }

    try:
        pod_level_buckets = (await es_instance.search(index="logs", body=query_body))[
            "aggregations"
        ]["pod_name"]["buckets"]
        logging.info(pod_level_buckets)
        for each_pod_bucket in pod_level_buckets:
            if not each_pod_bucket["key"] in pod_storage_dict:
                if len(each_pod_bucket["key"]) > 0:
                    pod_storage_dict[each_pod_bucket["key"]] = {
                        "Insights": {"Normal": 0, "Suspicious": 0, "Anomaly": 0}
                    }
                else:
                    continue
            anomaly_level_buckets = each_pod_bucket["anomaly_level"]["buckets"]
            for bucket in anomaly_level_buckets:
                pod_storage_dict[each_pod_bucket["key"]]["Insights"][
                    bucket["key"]
                ] = bucket["doc_count"]
        logging.info("made it past here as well")
        for pod_name in pod_storage_dict:
            pod_breakdown_dict["Pods"].append(
                {"Name": pod_name, "Insights": pod_storage_dict[pod_name]}
            )

    except Exception as e:
        logging.error(f"Unable to breakdown pod insights. {e}")
        return pod_breakdown_dict

    return pod_breakdown_dict


def get_next_owner_reference_metadata(all_workload_data, owner_name):
    """
    This function is called by get_workload_name and takes in a list of metadata objects of a particular workload type
    (deployment, statefulset, replicaset or daemonset) and a string for the owner name. It will then go through
    the list of metadata objects, until it comes across the object which matches the owner name and then returns that
    metadata object. If no metadata object is found, return None which will cause the while loop in get_workload_name
    to break.
    """
    for data_idx in range(len(all_workload_data)):
        if all_workload_data[data_idx].metadata.name == owner_name:
            return all_workload_data[data_idx].metadata


def get_workload_name(pod_metadata):
    """
    This function gets the name of the workload by looping through owner references until it reaches a workload which
    does not have an owner reference. When it reaches that workload, it then is able to retrieve the name of that workload.
    """

    owner_name = None
    # While loop that will keep on looping until it comes across an object which does not have an owner reference.
    while pod_metadata and pod_metadata.owner_references:
        owner_references = pod_metadata.owner_references
        if len(owner_references) == 0:
            break
        owner_kind = owner_references[0].kind
        owner_name = owner_references[0].name
        # Depending on the kind of owner_reference, fetch the appropriate breakdown type and obtain the updated pod_metadata.
        if owner_kind == "Deployment":
            all_deployments = (
                app_api_instance.list_deployment_for_all_namespaces().items
            )
            pod_metadata = get_next_owner_reference_metadata(
                all_deployments, owner_name
            )
        elif owner_kind == "StatefulSet":
            all_stateful_sets = (
                app_api_instance.list_stateful_set_for_all_namespaces().items
            )
            pod_metadata = get_next_owner_reference_metadata(
                all_stateful_sets, owner_name
            )
        elif owner_kind == "ReplicaSet":
            all_replica_sets = (
                app_api_instance.list_replica_set_for_all_namespaces().items
            )
            pod_metadata = get_next_owner_reference_metadata(
                all_replica_sets, owner_name
            )
        elif owner_kind == "DaemonSet":
            all_daemon_sets = (
                app_api_instance.list_daemon_set_for_all_namespaces().items
            )
            pod_metadata = get_next_owner_reference_metadata(
                all_daemon_sets, owner_name
            )
        else:
            break

    return owner_name


async def get_workload_breakdown(start_ts, end_ts):
    # Get the breakdown of normal, suspicious and anomalous logs by workload.
    workload_breakdown_dict = {
        "ReplicaSet": {},
        "StatefulSet": {},
        "Deployment": {},
        "Job": {},
        "DaemonSet": {},
        "CustomResource": {},
        "Independent": {},
    }
    workload_namespace_dict = dict()
    # Try accessing the list of all pods through the Kubernetes API. If unsuccessful, return the workload_breakdown_dict object in its bare bone structure.
    try:
        all_pods = core_api_instance.list_pod_for_all_namespaces(watch=False)
        all_pods_items = all_pods.items
    except Exception as e:
        logging.error(f"Unable to obtain pod data. {e}")
        return workload_breakdown_dict

    pod_storage_dict = get_all_pod_names(all_pods_items)

    query_body = {
        "size": 0,
        "query": {
            "bool": {
                "must": [{"match": {"is_control_plane_log": "false"}}],
                "filter": [{"range": {"timestamp": {"gte": start_ts, "lte": end_ts}}}],
            }
        },
        "aggs": {
            "pod_name": {
                "terms": {"field": "kubernetes.pod_name.keyword"},
                "aggs": {
                    "anomaly_level": {"terms": {"field": "anomaly_level.keyword"}}
                },
            }
        },
    }

    try:
        pod_level_buckets = (await es_instance.search(index="logs", body=query_body))[
            "aggregations"
        ]["pod_name"]["buckets"]
        for each_pod_bucket in pod_level_buckets:
            if not each_pod_bucket["key"] in pod_storage_dict:
                if len(each_pod_bucket["key"]) > 0:
                    pod_storage_dict[each_pod_bucket["key"]] = {
                        "Insights": {"Normal": 0, "Suspicious": 0, "Anomaly": 0}
                    }
                else:
                    continue
            anomaly_level_buckets = each_pod_bucket["anomaly_level"]["buckets"]
            for bucket in anomaly_level_buckets:
                pod_storage_dict[each_pod_bucket["key"]]["Insights"][
                    bucket["key"]
                ] = bucket["doc_count"]

    except Exception as e:
        logging.error(f"Unable to query data from Elasticsearch. {e}")
        return workload_breakdown_dict

    for pod_spec in all_pods_items:
        # For each pod object. obtain the name, metadata and owner references.
        pod_metadata = pod_spec.metadata
        pod_name = pod_metadata.name
        namespace_name = pod_metadata.namespace
        owner_references = pod_metadata.owner_references
        kind = "CustomResource"
        workload_name = pod_metadata.name
        # Determine the kind of breakdown of the pod and update the workload name as well to the name of the owner reference.
        if owner_references and len(owner_references) > 0:
            if owner_references[0].kind in workload_breakdown_dict:
                kind = owner_references[0].kind
            workload_name = owner_references[0].name
        else:
            kind = "Independent"

        # Get the original name of the workload by calling get_workload_name function. If original_workload_name is not
        # None then set the workload_name to original_workload_name.
        original_workload_name = get_workload_name(pod_metadata)
        if original_workload_name:
            workload_name = original_workload_name
        if not workload_name in workload_namespace_dict:
            workload_namespace_dict[workload_name] = namespace_name
        if not workload_name in workload_breakdown_dict[kind]:
            workload_breakdown_dict[kind][workload_name] = {
                "Normal": 0,
                "Suspicious": 0,
                "Anomaly": 0,
            }
        # Accumulate the insight count for each workload name.
        for anomaly_level in workload_breakdown_dict[kind][workload_name]:
            workload_breakdown_dict[kind][workload_name][
                anomaly_level
            ] += pod_storage_dict[pod_name]["Insights"][anomaly_level]

    # Restructure workload_breakdown_dict to be in finalized format.
    for breakdown_type, breakdown_dict in workload_breakdown_dict.items():
        workload_breakdown_dict[breakdown_type] = []
        for name, insights in breakdown_dict.items():
            workload_breakdown_dict[breakdown_type].append(
                {
                    "Name": name,
                    "Namespace": workload_namespace_dict[name],
                    "Insights": insights,
                }
            )
    return workload_breakdown_dict


async def get_namespace_breakdown(start_ts, end_ts):
    # Get the breakdown of normal, suspicious and anomolous logs by namespace.
    namespace_breakdown_dict = {"Namespaces": []}
    namespace_storage_dict = dict()
    # Try accessing the list of all namespaces through the Kubernetes API. If unsuccessful, return the namespace_breakdown_dict object in its bare bone structure.
    try:
        all_namespaces = core_api_instance.list_namespace()
        all_namespace_items = all_namespaces.items
    except Exception as e:
        logging.error("Unable to obtain namespace data.")
        return namespace_breakdown_dict

    for namespace_obj in all_namespace_items:
        try:
            namespace_name = namespace_obj.metadata.name
            namespace_storage_dict[namespace_name] = {
                "Insights": {"Normal": 0, "Suspicious": 0, "Anomaly": 0}
            }
        except Exception as e:
            logging.error("Unable to access namespace data")
            return namespace_breakdown_dict

    query_body = {
        "size": 0,
        "query": {
            "bool": {
                "must": [{"match": {"is_control_plane_log": "false"}}],
                "filter": [{"range": {"timestamp": {"gte": start_ts, "lte": end_ts}}}],
            }
        },
        "aggs": {
            "namespace_name": {
                "terms": {"field": "kubernetes.namespace_name.keyword"},
                "aggs": {
                    "anomaly_level": {"terms": {"field": "anomaly_level.keyword"}}
                },
            }
        },
    }

    try:
        namespace_level_buckets = (
            await es_instance.search(index="logs", body=query_body)
        )["aggregations"]["namespace_name"]["buckets"]
        for each_ns_bucket in namespace_level_buckets:
            if not each_ns_bucket["key"] in namespace_storage_dict:
                if len(each_ns_bucket["key"]) > 0:
                    namespace_storage_dict[each_ns_bucket["key"]] = {
                        "Insights": {"Normal": 0, "Suspicious": 0, "Anomaly": 0}
                    }
            anomaly_level_buckets = each_ns_bucket["anomaly_level"]["buckets"]
            for bucket in anomaly_level_buckets:
                namespace_storage_dict[each_ns_bucket["key"]]["Insights"][
                    bucket["key"]
                ] = bucket["doc_count"]

        for namespace_name in namespace_storage_dict:
            namespace_breakdown_dict["Namespaces"].append(
                {
                    "Name": namespace_name,
                    "Insights": namespace_storage_dict[namespace_name],
                }
            )

    except Exception as e:
        logging.error(f"Unable to access Elasticsearch data. {e}")
        return namespace_breakdown_dict
    return namespace_breakdown_dict


async def get_overall_breakdown(start_ts, end_ts):
    # Get the overall breakdown of normal, suspicious and anomalous logs within start_ts and end_ts.
    overall_breakdown_dict = {"Normal": 0, "Suspicious": 0, "Anomaly": 0}
    query_body = {
        "query": {
            "bool": {
                "filter": [{"range": {"timestamp": {"gte": start_ts, "lte": end_ts}}}],
            }
        },
        "aggs": {"anomaly_level": {"terms": {"field": "anomaly_level.keyword"}}},
    }
    try:
        anomaly_level_buckets = (
            await es_instance.search(index="logs", body=query_body)
        )["aggregations"]["anomaly_level"]["buckets"]
        for each_bucket in anomaly_level_buckets:
            overall_breakdown_dict[each_bucket["key"]] = each_bucket["doc_count"]

    except Exception as e:
        logging.error(f"Unable to access Elasticsearch data. {e}")
        return overall_breakdown_dict
    return overall_breakdown_dict


async def get_logs(start_ts, end_ts):
    """
    Get all logs marked as Suspicious or Anomoly and additional attributes such as the timestamp, anomaly_level,
    whether or not it is a control plane log, pod name and namespace name.
    """
    logs_dict = {"Logs": []}
    query_body = {
        "query": {
            "bool": {
                "filter": [{"range": {"timestamp": {"gte": start_ts, "lte": end_ts}}}],
                "must_not": [{"match": {"anomaly_level": "Normal"}}],
            },
        },
        "_source": [
            "timestamp",
            "log",
            "anomaly_level",
            "is_control_plane_log",
            "kubernetes.pod_name",
            "kubernetes.namespace_name",
        ],
        "sort": [{"timestamp": {"order": "asc"}}],
    }
    try:
        async for each_result in async_scan(
            es_instance, index="logs", query=query_body
        ):
            logs_dict["Logs"].append(each_result["_source"])
    except Exception as e:
        logging.error(f"Unable to access logs data. {e}")
        return logs_dict

    return logs_dict


async def get_control_plane_components_breakdown(start_ts, end_ts):
    # Get the breakdown of normal, suspicious and anomolous logs by kubernetes control plane component.
    kubernetes_components_breakdown_dict = {"Components": []}
    kubernetes_components_storage_dict = dict()

    kubernetes_components = [
        "kubelet",
        "kube-controller-manager",
        "kube-apiserver",
        "kube-proxy",
        "kube-scheduler",
        "etcd",
        "k3s-agent",
        "k3s-server",
        "rke2-agent",
        "rke2-server",
    ]
    for component in kubernetes_components:
        kubernetes_components_storage_dict[component] = {
            "Insights": {"Normal": 0, "Suspicious": 0, "Anomaly": 0}
        }

    query_body = {
        "size": 0,
        "query": {
            "bool": {
                "filter": [{"range": {"timestamp": {"gte": start_ts, "lte": end_ts}}}],
                "must": [{"match": {"is_control_plane_log": "true"}}],
            }
        },
        "aggs": {
            "component_name": {
                "terms": {"field": "kubernetes_component.keyword"},
                "aggs": {
                    "anomaly_level": {"terms": {"field": "anomaly_level.keyword"}}
                },
            }
        },
    }

    try:
        component_level_buckets = (
            await es_instance.search(index="logs", body=query_body)
        )["aggregations"]["component_name"]["buckets"]
        for each_component_bucket in component_level_buckets:
            anomaly_level_buckets = each_component_bucket["anomaly_level"]["buckets"]
            for bucket in anomaly_level_buckets:
                kubernetes_components_storage_dict[each_component_bucket["key"]][
                    "Insights"
                ][bucket["key"]] = bucket["doc_count"]

        for component_name in kubernetes_components_storage_dict:
            kubernetes_components_breakdown_dict["Components"].append(
                {
                    "Name": component_name,
                    "Insights": kubernetes_components_storage_dict[component_name],
                }
            )

    except Exception as e:
        logging.error(f"Unable to access Elasticsearch data. {e}")
        return kubernetes_components_breakdown_dict

    return kubernetes_components_breakdown_dict


async def get_peaks(start_ts, end_ts):
    return


@app.get("/pod")
async def index_pod(start_ts: int, end_ts: int):
    # This function handles get requests for fetching pod breakdown insights.
    logging.info(
        f"Received request to obtain pod insights between {start_ts} and {end_ts}"
    )
    try:
        result = await get_pod_breakdown(start_ts, end_ts)
        return result
    except Exception as e:
        # Bad Request
        logging.error(e)


@app.get("/namespace")
async def index_namespace(start_ts: int, end_ts: int):
    # This function handles get requests for fetching namespace breakdown insights.
    logging.info(
        f"Received request to obtain namespace insights between {start_ts} and {end_ts}"
    )
    try:
        result = await get_namespace_breakdown(start_ts, end_ts)
        return result
    except Exception as e:
        # Bad Request
        logging.error(e)


@app.get("/workload")
async def index_workload(start_ts: int, end_ts: int):
    # This function handles get requests for fetching workload breakdown insights.
    logging.info(
        f"Received request to obtain workload insights between {start_ts} and {end_ts}"
    )
    try:
        result = await get_workload_breakdown(start_ts, end_ts)
        return result
    except Exception as e:
        # Bad Request
        logging.error(e)


@app.get("/overall_insights")
async def index_overall_breakdown(start_ts: int, end_ts: int):
    # This function handles get requests for fetching workload breakdown insights.
    logging.info(
        f"Received request to obtain all insights between {start_ts} and {end_ts}"
    )
    try:
        result = await get_overall_breakdown(start_ts, end_ts)
        return result
    except Exception as e:
        # Bad Request
        logging.error(e)


@app.get("/logs")
async def index_logs(start_ts: int, end_ts: int):
    # This function handles get requests for fetching suspicious and anomalous logs between start_ts and end_ts
    logging.info(
        f"Received request to obtain all suspicious and anomalous logs between {start_ts} and {end_ts}"
    )
    try:
        result = await get_logs(start_ts, end_ts)
        return result
    except Exception as e:
        # Bad Request
        logging.error(e)


@app.get("/areas_of_interest")
async def get_areas_of_interest(start_ts: int, end_ts: int):
    logging.info(
        f"Received request to obtain all areas of interest between {start_ts} and {end_ts}"
    )

    query = {
        "query": {
            "bool": {
                "must": [{"match": {"anomaly_level.keyword": "Anomaly"}}],
                "filter": [{"range": {"timestamp": {"gte": start_ts, "lte": end_ts}}}],
            }
        },
        "aggs": {
            "logs_over_time": {
                "date_histogram": {"field": "timestamp", "calendar_interval": "minute"},
                "aggs": {"total_normal": {"sum": {"field": "anomaly_predicted_count"}}},
            }
        },
    }
    res = await es_instance.search(index="logs", body=query, size=0)
    df = pd.DataFrame(res["aggregations"]["logs_over_time"]["buckets"])
    areas_of_interest = []
    if len(df) > 0:
        # anomaly_predicted_count == 2 for 'Anomaly' labeled log messages
        df["doc_count"] = df["doc_count"] / 2
        df["moving_avg"] = df["doc_count"].rolling(60).mean() * 1.3
        df["AOI"] = df.doc_count.gt(df.moving_avg.shift())
        areas_of_interest_df = df[df.AOI == True]
        areas_of_interest_df["time_diff"] = areas_of_interest_df["key"].diff()
        current_aoi_start = -1
        prev_segment_start = -1
        for index, row in areas_of_interest_df.iterrows():
            if current_aoi_start == -1:
                current_aoi_start = row["key"]
            if not pd.isna(row['time_diff']) and row["time_diff"] != 60000.0:
                areas_of_interest.append(
                    {
                        "start_ts": current_aoi_start,
                        "end_ts": prev_segment_start + 60000,
                    }
                )
                current_aoi_start = row["key"]
            prev_segment_start = row["key"]
        # handle last entry
        areas_of_interest.append(
            {"start_ts": current_aoi_start, "end_ts": prev_segment_start + 60000}
        )

    return areas_of_interest


@app.get("/control_plane")
async def index_control_plane_components(start_ts: int, end_ts: int):
    # This function handles get requests for fetching control plane components breakdown insights.
    logging.info(f"Received request to obtain all logs between {start_ts} and {end_ts}")
    try:
        result = await get_control_plane_components_breakdown(start_ts, end_ts)
        return result
    except Exception as e:
        # Bad Request
        logging.error(e)


@app.get("/peaks")
async def get_peaks(start_ts: int, end_ts: int):
    # This function handles get requests for fetching peaks in number of anomalies predicted within a start and end time interval.
    logging.info(
        f"Received request to obtain all peaks with respect to number of anomalies within {start_ts} and {end_ts}"
    )
    rtpd_model = real_time_peak_detection(WINDOW, THRESHOLD, INFLUENCE)
    peak_timestamps = []
    query = {
        "query": {
            "bool": {
                "must": [{"match": {"anomaly_level.keyword": "Anomaly"}}],
                "filter": [{"range": {"timestamp": {"gte": start_ts, "lte": end_ts}}}],
            }
        },
        "aggs": {
            "logs_over_time": {
                "date_histogram": {"field": "timestamp", "calendar_interval": "minute"},
                "aggs": {"total_normal": {"sum": {"field": "anomaly_predicted_count"}}},
            }
        }
    }
    try:
        res = await es_instance.search(index="logs", body=query, size=0)
        df = pd.DataFrame(res["aggregations"]["logs_over_time"]["buckets"])
        if len(df) > 0:
            # anomaly_predicted_count == 2 for 'Anomaly' labeled log messages
            df["doc_count"] = df["doc_count"] // 2
            for index, row in df.iterrows():
                timestamp, anomaly_count = row["key"], row["doc_count"]
                if rtpd_model.detect_peaks(anomaly_count):
                    peak_timestamps.append(timestamp)
        return peak_timestamps
    except Exception as e:
        logging.error("Unable to obtain peaks")
        return peak_timestamps
