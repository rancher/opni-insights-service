# Standard Library
import json
import time

# Third Party
import requests
from kubernetes import client, config


def test_insights_breakdown_happy_path():

    # This test is to verify that that Insights Service is able to list a breakdown view of Log Insights by component (Insights Breakdown Endpoint)
        # Verify that the Insights Service is able to list Log Insights by:
            # kubelet 
            # kube_proxy
            # kube_scheduler
            # kube_controller_manager
            # etcd
            # k3s_agent
            # k3s_server
            # rke2_agent
            # rke2_server
    
    start_ts = (str(int(time.time()-300)) + '000')  # Current time minus 5 minutes in epoch time format
    end_ts = (str(int(time.time())) + '000') # Current time in epoch time format

    print("Start time: " + start_ts + "\n End time: " + end_ts)

    print('GET Insights Breakdown')
    r = requests.get("http://opni-svc-insights.opni.svc.cluster.local:80/insights_breakdown?start_ts=" 
    + start_ts + "&end_ts=" + end_ts, verify=False)
        
    if len(r.content) != 0:
        print(("Request Content: "), r.content)
        print(("Request Headers: "), r.headers)
        print(("Request Status Code"), r.status_code)
        if r.status_code != 200:
            raise Exception("API returned a non-200 status code")
    
    response = json.loads(r.content)
    print("Request Response: ", response)
    assert response['Namespaces'][0]['Name'] == 'opni-sono'
    assert response['Namespaces'][0]['Insights']['Normal'] >= 0
    assert response['Namespaces'][0]['Insights']['Suspicious'] >= 0
    assert response['Namespaces'][0]['Insights']['Anomaly'] >= 0
    assert response['Control Plane']['Components'][0]['Name'] == 'kubelet'
    assert response['Control Plane']['Components'][0]['Insights']['Normal'] >= 0
    assert response['Control Plane']['Components'][0]['Insights']['Suspicious'] >= 0
    assert response['Control Plane']['Components'][0]['Insights']['Anomaly'] >= 0
    assert response['Control Plane']['Components'][1]['Name'] == 'kube-controller-manager'
    assert response['Control Plane']['Components'][1]['Insights']['Normal'] >= 0
    assert response['Control Plane']['Components'][1]['Insights']['Suspicious'] >= 0
    assert response['Control Plane']['Components'][1]['Insights']['Anomaly'] >= 0
    assert response['Control Plane']['Components'][2]['Name'] == 'kube-apiserver'
    assert response['Control Plane']['Components'][2]['Insights']['Normal'] >= 0
    assert response['Control Plane']['Components'][2]['Insights']['Suspicious'] >= 0
    assert response['Control Plane']['Components'][2]['Insights']['Anomaly'] >= 0
    assert response['Control Plane']['Components'][3]['Name'] == 'kube-proxy'
    assert response['Control Plane']['Components'][3]['Insights']['Normal'] >= 0
    assert response['Control Plane']['Components'][3]['Insights']['Suspicious'] >= 0
    assert response['Control Plane']['Components'][3]['Insights']['Anomaly'] >= 0
    assert response['Control Plane']['Components'][4]['Name'] == 'kube-scheduler'
    assert response['Control Plane']['Components'][4]['Insights']['Normal'] >= 0
    assert response['Control Plane']['Components'][4]['Insights']['Suspicious'] >= 0
    assert response['Control Plane']['Components'][4]['Insights']['Anomaly'] >= 0
    assert response['Control Plane']['Components'][5]['Name'] == 'etcd'
    assert response['Control Plane']['Components'][5]['Insights']['Normal'] >= 0
    assert response['Control Plane']['Components'][5]['Insights']['Suspicious'] >= 0
    assert response['Control Plane']['Components'][5]['Insights']['Anomaly'] >= 0
    assert response['Control Plane']['Components'][6]['Name'] == 'k3s-agent'
    assert response['Control Plane']['Components'][6]['Insights']['Normal'] >= 0
    assert response['Control Plane']['Components'][6]['Insights']['Suspicious'] >= 0
    assert response['Control Plane']['Components'][6]['Insights']['Anomaly'] >= 0
    assert response['Control Plane']['Components'][7]['Name'] == 'k3s-server'
    assert response['Control Plane']['Components'][7]['Insights']['Normal'] >= 0
    assert response['Control Plane']['Components'][7]['Insights']['Suspicious'] >= 0
    assert response['Control Plane']['Components'][7]['Insights']['Anomaly'] >= 0
    assert response['Control Plane']['Components'][8]['Name'] == 'rke2-agent'
    assert response['Control Plane']['Components'][8]['Insights']['Normal'] >= 0
    assert response['Control Plane']['Components'][8]['Insights']['Suspicious'] >= 0
    assert response['Control Plane']['Components'][8]['Insights']['Anomaly'] >= 0
    assert response['Control Plane']['Components'][9]['Name'] == 'rke2-server'
    assert response['Control Plane']['Components'][9]['Insights']['Normal'] >= 0
    assert response['Control Plane']['Components'][9]['Insights']['Suspicious'] >= 0
    assert response['Control Plane']['Components'][9]['Insights']['Anomaly'] >= 0
    

def test_overall_insights_happy_path():
    
    # This test is to verify that the Insights Service is able to list an overall view of Log Insights (Overall Insights Endpoint)

    start_ts = (str(int(time.time()-300)) + '000')  # Current time minus 5 minutes in epoch time format
    end_ts = (str(int(time.time())) + '000') # Current time in epoch time format
    granularity_level = "1d"
    print("Start time: " + start_ts + "\n End time: " + end_ts + "\n Granularity Level: " + granularity_level)

    print('GET Overall Insights')
    r = requests.get("http://opni-svc-insights.opni.svc.cluster.local:80/overall_insights?start_ts=" 
    + start_ts + "&end_ts=" + end_ts + "&granularity_level=" + granularity_level, verify=False)
        
    if len(r.content) != 0:
        print(("Request Content: "), r.content)
        print(("Request Headers: "), r.headers)
        print(("Request Status Code"), r.status_code)
        if r.status_code != 200:
            raise Exception("API returned a non-200 status code")
    
    response = json.loads(r.content)
    assert response['Insights'][0]['Normal'] >= 0
    assert response['Insights'][0]['Suspicious'] >= 0
    assert response['Insights'][0]['Anomaly'] >= 0
    assert str(response['Insights'][0]['time_start']) <= end_ts


def test_anomalies_breakdown_happy_path():
    
    # This test is to verify that the Insights Service is able to determine number Workload vs Control Plane Anomalies (Anomalies Breakdown Endpoint)

    start_ts = (str(int(time.time()-300)) + '000')  # Current time minus 5 minutes in epoch time format
    end_ts = (str(int(time.time())) + '000') # Current time in epoch time format
    print("Start time: " + start_ts + "\n End time: " + end_ts)

    print('GET Anomalies Breakdown')
    r = requests.get("http://opni-svc-insights.opni.svc.cluster.local:80/anomalies_breakdown?start_ts=" 
    + start_ts + "&end_ts=" + end_ts, verify=False)
        
    if len(r.content) != 0:
        print(("Request Content: "), r.content)
        print(("Request Headers: "), r.headers)
        print(("Request Status Code"), r.status_code)
        if r.status_code != 200:
            raise Exception("API returned a non-200 status code")
    
    response = json.loads(r.content)
    print("Request Response: ", response)
    assert response['Workload'] >= 0
    assert response['Control Plane'] >= 0


def test_logs_pod_happy_path():

    # This test is to verify that the Insights Service is able to list Log Insights by pod and anomaly level (Logs Pod Endpoint)

    config.load_incluster_config()

    v1 = client.CoreV1Api()
    print("Listing pods with their IPs:")
    ret = v1.list_namespaced_pod('ingress-nginx')
    pod_names = []
    for i in ret.items:
        print(i.metadata.namespace, i.metadata.name)
        pod_names.append(i.metadata.name)

    start_ts = (str(int(time.time()-86400)) + '000')  # Current time minus 5 minutes in epoch time format
    end_ts = (str(int(time.time())) + '000') # Current time in epoch time format
    anomaly_level = "Normal" # Anomaly level can be Normal, Suspicious or Anomaly
    pod_name = pod_names[0] # Name of the pod
    namespace_name = "ingress-nginx" # Name of the namespace
    print("Start time: " + start_ts + "\n End time: " + end_ts + "\n Anomaly Level: " 
    + anomaly_level + "\n Pod Name: " + pod_name + "\n Namespace Name: " + namespace_name)

    print('GET Logs Pod')
    r = requests.get("http://opni-svc-insights.opni.svc.cluster.local:80/logs_pod?start_ts="+ start_ts + "&end_ts=" 
    + end_ts + "&anomaly_level=" + anomaly_level + "&pod_name=" + pod_name + "&namespace_name=" + namespace_name, verify=False)
        
    if len(r.content) != 0:
        print(("Request Content: "), r.content)
        print(("Request Headers: "), r.headers)
        print(("Request Status Code"), r.status_code)
        if r.status_code != 200:
            raise Exception("API returned a non-200 status code")
    
    response = json.loads(r.content)
    print("Request Response: ", response)
    assert response['Logs'][0]['log'] != None

    if response['Logs'][0]['is_control_plane_log'] == True:
        assert response['Logs'][0]['is_control_plane_log'] == True
    if response['Logs'][0]['is_control_plane_log'] == False:
        assert response['Logs'][0]['is_control_plane_log'] == False
    else:
        raise Exception("Log Pods: is_control_plane_log is not true or false")

    assert response['Logs'][0]['kubernetes.pod_name'] == pod_name
    assert response['Logs'][0]['kubernetes.namespace_name'] == namespace_name
    assert response['Logs'][0]['anomaly_level'] == anomaly_level
    assert str(response['Logs'][0]['timestamp']) <= end_ts

    log_count = sum(1 for log in response['Logs'] if log.get('log'))
    assert response['total_logs_count'] == log_count
    assert response['scroll_id'] != None


def test_logs_namespace_happy_path():

    # This test is to verify that the Insights Service is able to list Log Insights by namespace and anomaly level (Logs Namespace Endpoint)

    start_ts = (str(int(time.time()-86400)) + '000')  # Current time minus 5 minutes in epoch time format
    end_ts = (str(int(time.time())) + '000') # Current time in epoch time format
    anomaly_level = "Normal" # Anomaly level can be Normal, Suspicious or Anomaly
    namespace_name = "ingress-nginx" # Name of the namespace
    print("Start time: " + start_ts + "\n End time: " + end_ts 
    + "\n Anomaly Level: " + anomaly_level + "\n Namespace Name: " + namespace_name)


    print('GET Logs Namespace')
    r = requests.get("http://opni-svc-insights.opni.svc.cluster.local:80/logs_namespace?start_ts=" + start_ts 
    + "&end_ts=" + end_ts + "&anomaly_level=" + anomaly_level + "&namespace_name=" + namespace_name, verify=False)
        
    if len(r.content) != 0:
        print(("Request Content: "), r.content)
        print(("Request Headers: "), r.headers)
        print(("Request Status Code"), r.status_code)
        if r.status_code != 200:
            raise Exception("API returned a non-200 status code")
    
    response = json.loads(r.content)
    print("Request Response: ", response)
    assert response['Logs'][0]['log'] != None

    if response['Logs'][0]['is_control_plane_log'] == True:
        assert response['Logs'][0]['is_control_plane_log'] == True
    if response['Logs'][0]['is_control_plane_log'] == False:
        assert response['Logs'][0]['is_control_plane_log'] == False
    else:
        raise Exception("Log Pods: is_control_plane_log is not true or false")

    assert response['Logs'][0]['kubernetes.pod_name'] != None
    assert response['Logs'][0]['kubernetes.namespace_name'] == namespace_name
    assert response['Logs'][0]['anomaly_level'] == anomaly_level
    assert str(response['Logs'][0]['timestamp']) <= end_ts

    log_count = sum(1 for log in response['Logs'] if log.get('log'))
    assert response['total_logs_count'] == log_count
    assert response['scroll_id'] != None


def tests_logs_workload_happy_path():
    
    # This test is to verify that the Insights Service is able to list Log Insights by workload and anomaly level (Logs Workload Endpoint)

    config.load_incluster_config()

    v1 = client.CoreV1Api()
    print("Listing pods with their IPs:")
    ret = v1.list_namespaced_pod('ingress-nginx')
    pod_names = []
    for i in ret.items:
        print(i.metadata.namespace, i.metadata.name)
        pod_names.append(i.metadata.name)
    
    start_ts = (str(int(time.time()-86400)) + '000')  # Current time minus 5 minutes in epoch time format
    end_ts = (str(int(time.time())) + '000') # Current time in epoch time format
    anomaly_level = "Normal" # Anomaly level can be Normal, Suspicious or Anomaly
    pod_name = pod_names[0] # Name of the pod
    namespace_name = "ingress-nginx" # Name of the namespace
    workload_type = "DaemonSet" # workload type can be Deployment, StatefulSet, ReplicSet, DaemonSet, Job, CronJob, Pod
    workload_name = "nginx-ingress-controller" # Name of the workload
    print("Start time: " + start_ts + "\n End time: " + end_ts + "\n Anomaly Level: " + anomaly_level 
    + "\n Namespace Name: " + namespace_name + "\n Pod Name: " + pod_name + "\n Workload Type: " 
    + workload_type + "\n Workload Name: " + workload_name)

    print('GET Logs Workload')
    r = requests.get("http://opni-svc-insights.opni.svc.cluster.local:80/logs_workload?start_ts="+ start_ts + "&end_ts=" 
    + end_ts + "&anomaly_level=" + anomaly_level + "&pod_name=" + pod_name + "&namespace_name=" + namespace_name + 
    "&workload_type=" + workload_type + "&workload_name=" + workload_name, verify=False)
        
    if len(r.content) != 0:
        print(("Request Content: "), r.content)
        print(("Request Headers: "), r.headers)
        print(("Request Status Code"), r.status_code)
        if r.status_code != 200:
            raise Exception("API returned a non-200 status code")
    
    response = json.loads(r.content)
    print("Request Response: ", response)
    assert response['Logs'][0]['log'] != None

    if response['Logs'][0]['is_control_plane_log'] == True:
        assert response['Logs'][0]['is_control_plane_log'] == True
    if response['Logs'][0]['is_control_plane_log'] == False:
        assert response['Logs'][0]['is_control_plane_log'] == False
    else:
        raise Exception("Log Pods: is_control_plane_log is not true or false")

    assert response['Logs'][0]['kubernetes.pod_name'] != None
    assert response['Logs'][0]['kubernetes.namespace_name'] == namespace_name
    assert response['Logs'][0]['anomaly_level'] == anomaly_level
    assert str(response['Logs'][0]['timestamp']) <= end_ts

    log_count = sum(1 for log in response['Logs'] if log.get('log'))
    assert response['total_logs_count'] >= log_count
    assert response['scroll_id'] != None


def test_logs_namespace_happy_path():
    
    # This test is to verify that the Insights Service is able to list Log Insights by control plane component and anomaly level (Logs Control Plane Endpoint)

    start_ts = (str(int(time.time()-86400)) + '000')  # Current time minus 5 minutes in epoch time format
    end_ts = (str(int(time.time())) + '000') # Current time in epoch time format
    anomaly_level = "Normal" # Anomaly level can be Normal, Suspicious or Anomaly
    # Control plane component can be "kubelet", "kube-controller-manager", "kube-apiserver", 
    # "kube-proxy", "kube-scheduler", "etcd", "k3s-agent", "k3s-server", "rke2-agent", and "rke2-server"
    control_plane_component = "kubelet" 
    print("Start time: " + start_ts + "\n End time: " + end_ts + "\n Anomaly Level: " 
    + anomaly_level + "\n Control Plane Component: " + control_plane_component)

    print('GET Logs Control Plane Component')
    r = requests.get("http://opni-svc-insights.opni.svc.cluster.local:80/logs_control_plane?start_ts="+ start_ts + "&end_ts=" 
    + end_ts + "&anomaly_level=" + anomaly_level + "&control_plane_component=" + control_plane_component, verify=False)
        
    if len(r.content) != 0:
        print(("Request Content: "), r.content)
        print(("Request Headers: "), r.headers)
        print(("Request Status Code"), r.status_code)
        if r.status_code != 200:
            raise Exception("API returned a non-200 status code")
    
    response = json.loads(r.content)
    print("Request Response: ", response)
    assert response['Logs'][0]['log'] != None
    assert response['Logs'][0]['is_control_plane_log'] == True
    assert response['Logs'][0]['kubernetes_component'] == control_plane_component
    assert response['Logs'][0]['anomaly_level'] == anomaly_level
    assert str(response['Logs'][0]['timestamp']) <= end_ts
    assert response['total_logs_count'] >= 0
    assert response['scroll_id'] != None


def wait_for_seconds(seconds):
    start_time = time.time()
    while time.time() - start_time < seconds:
        continue
