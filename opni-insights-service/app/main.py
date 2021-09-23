import logging
import os

# Third Party
from elasticsearch import Elasticsearch
from elasticsearch.helpers import scan
from fastapi import FastAPI
from kubernetes import client, config

app = FastAPI()
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(message)s")

ES_ENDPOINT = os.environ["ES_ENDPOINT"]
ES_USERNAME = os.environ["ES_USERNAME"]
ES_PASSWORD = os.environ["ES_PASSWORD"]
es_instance = Elasticsearch(
    [ES_ENDPOINT],
    port=9200,
    http_compress=True,
    http_auth=(ES_USERNAME, ES_PASSWORD),
    verify_certs=False,
    use_ssl=True,
)
config.load_incluster_config()
configuration = client.Configuration()
core_api_instance = client.CoreV1Api()
app_api_instance = client.AppsV1Api()


def get_pod_breakdown(start_ts, end_ts):
    # Get the breakdown of normal, suspicious and anomolous logs by pod.
    pod_breakdown_dict = {"Pods": []}
    # Try accessing the list of all pods through the Kubernetesa API. If unsuccessful, return the pod_breakdown_dict object in its bare bone structure.
    try:
        all_pods = core_api_instance.list_pod_for_all_namespaces(watch=False)
        all_pods_items = all_pods.items
    except Exception as e:
        logging.error(f"Unable to obtain pod data. {e}")
        return pod_breakdown_dict
    for pod_spec in all_pods_items:
        try:
            pod_metadata = pod_spec.metadata
            pod_name = pod_metadata.name
            pod_dict = {
                "Name": pod_name,
                "Insights": {"Normal": 0, "Suspicious": 0, "Anomaly": 0},
            }
            # For each namespace and insight, query Elasticsearch for the number of log messages that fall under the particular insight.
            for insight in pod_dict["Insights"]:
                query_body = {
                    "query": {
                        "bool": {
                            "must": [
                                {"match": {"kubernetes.pod_name": pod_name}},
                                {"match": {"anomaly_level": insight}},
                            ],
                            "filter": [
                                {
                                    "range": {
                                        "timestamp": {"gte": start_ts, "lte": end_ts}
                                    }
                                }
                            ],
                        }
                    }
                }
                pod_dict["Insights"][insight] = es_instance.count(
                    index="logs", body=query_body
                )["count"]
            pod_breakdown_dict["Pods"].append(pod_dict)
        except Exception as e:
            logging.error(f"Unable to access pod data. {e}")
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


def get_workload_breakdown(start_ts, end_ts):
    # Get the breakdown of normal, suspicious and anomolous logs by workload.
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
            query_body = {
                "query": {
                    "bool": {
                        "must": [
                            {"match": {"kubernetes.pod_name": pod_name}},
                            {"match": {"anomaly_level": anomaly_level}},
                        ],
                        "filter": [
                            {"range": {"timestamp": {"gte": start_ts, "lte": end_ts}}}
                        ],
                    }
                }
            }
            try:
                workload_breakdown_dict[kind][workload_name][
                    anomaly_level
                ] += es_instance.count(index="logs", body=query_body)["count"]
            except Exception as e:
                logging.error(f"Unable to query Elasticsearch. {e}")
                continue
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


def get_namespace_breakdown(start_ts, end_ts):
    # Get the breakdown of normal, suspicious and anomolous logs by namespace.
    namespace_breakdown_dict = {"Namespaces": []}
    # Try accessing the list of all pods through the Kubernetes API. If unsuccessful, return the namespace_breakdown_dict object in its bare bone structure.
    try:
        all_namespaces = core_api_instance.list_namespace()
        all_namespace_items = all_namespaces.items
    except Exception as e:
        logging.error("Unable to obtain namespace data.")
        return namespace_breakdown_dict
    for namespace_obj in all_namespace_items:
        try:
            namespace_name = namespace_obj.metadata.name
            namespace_dict = {
                "Name": namespace_name,
                "Insights": {"Normal": 0, "Suspicious": 0, "Anomaly": 0},
            }
            # For each namespace and insight, query Elasticsearch for the number of log messages that fall under the particular insight.
            for insight in namespace_dict["Insights"]:
                query_body = {
                    "query": {
                        "bool": {
                            "must": [
                                {
                                    "match": {
                                        "kubernetes.namespace_name": namespace_name
                                    }
                                },
                                {"match": {"anomaly_level": insight}},
                            ],
                            "filter": [
                                {
                                    "range": {
                                        "timestamp": {"gte": start_ts, "lte": end_ts}
                                    }
                                }
                            ],
                        }
                    }
                }
                namespace_dict["Insights"][insight] = es_instance.count(
                    index="logs", body=query_body
                )["count"]
            namespace_breakdown_dict["Namespaces"].append(namespace_dict)
        except Exception as e:
            logging.error(f"Unable to access namespace data. {e}")
            return namespace_breakdown_dict
    return namespace_breakdown_dict


def get_overall_breakdown(start_ts, end_ts):
    # Get the overall breakdown of normal, suspicious and anomolous logs within start_ts and end_ts.
    overall_breakdown_dict = {"Normal": 0, "Suspicious": 0, "Anomaly": 0}
    for anomaly_level in overall_breakdown_dict:
        query_body = {
            "query": {
                "bool": {
                    "must": [
                        {"match": {"anomaly_level": anomaly_level}},
                    ],
                    "filter": [
                        {"range": {"timestamp": {"gte": start_ts, "lte": end_ts}}}
                    ],
                }
            }
        }
        try:
            overall_breakdown_dict[anomaly_level] = es_instance.count(
                index="logs", body=query_body
            )["count"]
        except Exception as e:
            logging.error(f"Unable to access Elasticsearch data. {e}")
            return overall_breakdown_dict
    return overall_breakdown_dict


def get_logs(start_ts, end_ts):
    """
    Get all logs marked as Suspicious or Anomolous and additional attributes such as the timestamp, anomaly_level,
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
        logs_within_time_interval = scan(es_instance, index="logs", query=query_body)
        for each_result in logs_within_time_interval:
            logs_dict["Logs"].append(each_result["_source"])
    except Exception as e:
        logging.error(f"Unable to access logs data. {e}")
        return logs_dict

    return logs_dict


@app.get("/pod")
async def index_pod(start_ts: int, end_ts: int):
    # This function handles get requests for fetching pod breakdown insights.
    logging.info(
        f"Received request to obtain pod insights between {start_ts} and {end_ts}"
    )
    try:
        result = get_pod_breakdown(start_ts, end_ts)
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
        result = get_namespace_breakdown(start_ts, end_ts)
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
        result = get_workload_breakdown(start_ts, end_ts)
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
        result = get_overall_breakdown(start_ts, end_ts)
        return result
    except Exception as e:
        # Bad Request
        logging.error(e)


@app.get("/logs")
async def index_logs(start_ts: int, end_ts: int):
    # This function handles get requests for fetching suspicious and anomalous logs between start_ts and end_ts
    logging.info(f"Received request to obtain all logs between {start_ts} and {end_ts}")
    try:
        result = get_logs(start_ts, end_ts)
        return result
    except Exception as e:
        # Bad Request
        logging.error(e)
