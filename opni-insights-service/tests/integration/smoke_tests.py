# Standard Library
import time
import os
import json


import elasticsearch
# Third Party
import requests
# from faker import Faker

# fake = Faker()


def test_insights_breakdown_happy_path():
    
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
    print(response)
    assert response['Namespaces'][0]['Name'] == 'opni-sono'
    # assert response['Namespaces'][0]['Insights'][0]['Normal'] != None
    # assert response['Namespaces'][0]['Insights'][0]['Suspicious'] != None
    # assert response['Namespaces'][0]['Insights'][0]['Anomaly'] != None
    # assert response['Namespaces'][0]['Name'] == 'ingress-nginx'
    # assert response['Namespaces'][0]['Insights'][0]['Normal'] != None
    # assert response['Namespaces'][0]['Insights'][0]['Suspicious'] != None
    # assert response['Namespaces'][0]['Insights'][0]['Anomaly'] != None
    # assert response in r.content


# def test_overall_insights_happy_path():
    
#     start_ts = (str(int(time.time()-300)) + '000')  # Current time minus 5 minutes in epoch time format
#     end_ts = (str(int(time.time())) + '000') # Current time in epoch time format
#     granularity_level = "1d"
#     print("Start time: " + start_ts + "\n End time: " + end_ts + "\n Granularity Level: " + granularity_level)

#     print('GET Overall Insights')
#     r = requests.get("http://opni-svc-insights.opni.svc.cluster.local:80/overall_insights?start_ts=" 
#     + start_ts + "&end_ts=" + end_ts + "&granularity_level=" + granularity_level, verify=False)
        
#     if len(r.content) != 0:
#         print(("Request Content: "), r.content)
#         print(("Request Headers: "), r.headers)
#         print(("Request Status Code"), r.status_code)
#         if r.status_code != 200:
#             raise Exception("API returned a non-200 status code")
    
#     response = json.loads(r.content)
#     assert response['Insights'][0]['Normal'] != None
#     assert response['Insights'][0]['Suspicious'] != None
#     assert response['Insights'][0]['Anomaly'] != None
#     assert response['Insights'][0]['time_start'] != None


# def test_anomalies_breakdown_happy_path():
    
#     # TODO: Run elasticdump command to generate insights data


#     start_ts = str(int(time.time()-300))  # Current time minus 5 minutes in epoch time format
#     end_ts = str(int(time.time())) # Current time in epoch time format
#     print("Start time: " + start_ts + "\n End time: " + end_ts)


#     print('GET Anomalies Breakdown')
#     r = requests.get("http://opni-svc-insights.opni.svc.cluster.local:80/anomalies_breakdown?start_ts=" 
#     + start_ts + "&end_ts=" + end_ts, verify=False)
        
#     if len(r.content) != 0:
#         print(("Request Content: "), r.content)
#         print(("Request Headers: "), r.headers)
#         print(("Request Status Code"), r.status_code)
#         bad_content = '{"detail":"Something wrong with request'
#         content = r.content.decode("utf-8")
#         if bad_content in content:
#             raise Exception("Bad Request sent to API")
#         if r.status_code != 200:
#             raise Exception("Bad Request sent to API")
    
#     # TODO: Add assertions based on the elasticdump content
#     assert r.content != None


# def test_logs_pod_happy_path():
    
#     # TODO: Run elasticdump command to generate insights data


#     start_ts = str(int(time.time()-300))  # Current time minus 5 minutes in epoch time format
#     end_ts = str(int(time.time())) # Current time in epoch time format
#     # TODO: Define anomaly_level, pod_name, namespace_name
#     anomaly_level = "None" # Not sure what this is yet
#     pod_name = "None" # Name of the pod
#     namespace_name = "None" # Name of the namespace
#     print("Start time: " + start_ts + "\n End time: " + end_ts + "\n Anomaly Level: " 
#     + anomaly_level + "\n Pod Name: " + pod_name + "\n Namespace Name: " + namespace_name)


#     print('GET Logs Pod')
#     r = requests.get("http://opni-svc-insights.opni.svc.cluster.local:80/logs_pod?start_ts="+ start_ts + "&end_ts=" 
#     + end_ts + "&anomaly_level=" + anomaly_level + "&pod_name=" + pod_name + "&namespace_name=" + namespace_name, verify=False)
        
#     if len(r.content) != 0:
#         print(("Request Content: "), r.content)
#         print(("Request Headers: "), r.headers)
#         print(("Request Status Code"), r.status_code)
#         bad_content = '{"detail":"Something wrong with request'
#         content = r.content.decode("utf-8")
#         if bad_content in content:
#             raise Exception("Bad Request sent to API")
#         if r.status_code != 200:
#             raise Exception("Bad Request sent to API")
    
#     # TODO: Add assertions based on the elasticdump content
#     assert r.content != None


# def test_logs_namespace_happy_path():
    
#     # TODO: Run elasticdump command to generate insights data


#     start_ts = str(int(time.time()-300))  # Current time minus 5 minutes in epoch time format
#     end_ts = str(int(time.time())) # Current time in epoch time format
#     # TODO: Define anomaly_level and namespace_name
#     anomaly_level = "None" # Not sure what this is yet
#     namespace_name = "None" # Name of the namespace
#     print("Start time: " + start_ts + "\n End time: " + end_ts 
#     + "\n Anomaly Level: " + anomaly_level + "\n Namespace Name: " + namespace_name)


#     print('GET Logs Namespace')
#     r = requests.get("http://opni-svc-insights.opni.svc.cluster.local:80/logs_namespace?start_ts=" + start_ts 
#     + "&end_ts=" + end_ts + "&anomaly_level=" + anomaly_level + "&namespace_name=" + namespace_name, verify=False)
        
#     if len(r.content) != 0:
#         print(("Request Content: "), r.content)
#         print(("Request Headers: "), r.headers)
#         print(("Request Status Code"), r.status_code)
#         bad_content = '{"detail":"Something wrong with request'
#         content = r.content.decode("utf-8")
#         if bad_content in content:
#             raise Exception("Bad Request sent to API")
#         if r.status_code != 200:
#             raise Exception("Bad Request sent to API")
    
#     # TODO: Add assertions based on the elasticdump content
#     assert r.content != None


# def test_logs_workload_happy_path():
    
#     # TODO: Run elasticdump command to generate insights data


#     start_ts = str(int(time.time()-300))  # Current time minus 5 minutes in epoch time format
#     end_ts = str(int(time.time())) # Current time in epoch time format
#     # TODO: Define anomaly_level, pod_name, namespace_name, workload_name, and workload_type
#     anomaly_level = "None" # Not sure what this is yet
#     pod_name = "None" # Name of the pod
#     namespace_name = "None" # Name of the namespace
#     workload_type = "None" # Not sure what this is yet
#     workload_name = "None" # Name of the workload
#     print("Start time: " + start_ts + "\n End time: " + end_ts + "\n Anomaly Level: " + anomaly_level 
#     + "\n Namespace Name: " + namespace_name + "\n Pod Name: " + pod_name + "\n Workload Type: " 
#     + workload_type + "\n Workload Name: " + workload_name)


#     print('GET Logs Workload')
#     r = requests.get("http://opni-svc-insights.opni.svc.cluster.local:80/logs_workload?start_ts="+ start_ts + "&end_ts=" 
#     + end_ts + "&anomaly_level=" + anomaly_level + "&pod_name=" + pod_name + "&namespace_name=" + namespace_name + 
#     "&workload_type=" + workload_type + "&workload_name=" + workload_name, verify=False)
        
#     if len(r.content) != 0:
#         print(("Request Content: "), r.content)
#         print(("Request Headers: "), r.headers)
#         print(("Request Status Code"), r.status_code)
#         bad_content = '{"detail":"Something wrong with request'
#         content = r.content.decode("utf-8")
#         if bad_content in content:
#             raise Exception("Bad Request sent to API")
#         if r.status_code != 200:
#             raise Exception("Bad Request sent to API")
    
#     # TODO: Add assertions based on the elasticdump content
#     assert r.content != None


# def test_logs_namespace_happy_path():
    
#     # TODO: Run elasticdump command to generate insights data


#     start_ts = str(int(time.time()-300))  # Current time minus 5 minutes in epoch time format
#     end_ts = str(int(time.time())) # Current time in epoch time format
#     # TODO: Define anomaly_level and control_plane_component
#     anomaly_level = "None" # Not sure what this is yet
#     control_plane_component = "None" # Name of the namespace
#     print("Start time: " + start_ts + "\n End time: " + end_ts + "\n Anomaly Level: " 
#     + anomaly_level + "\n Control Plane Component: " + control_plane_component)


#     print('GET Logs Control Plane Component')
#     r = requests.get("http://opni-svc-insights.opni.svc.cluster.local:80/logs_control_plane?start_ts="+ start_ts + "&end_ts=" 
#     + end_ts + "&anomaly_level=" + anomaly_level + "&control_plane_component=" + control_plane_component, verify=False)
        
#     if len(r.content) != 0:
#         print(("Request Content: "), r.content)
#         print(("Request Headers: "), r.headers)
#         print(("Request Status Code"), r.status_code)
#         bad_content = '{"detail":"Something wrong with request'
#         content = r.content.decode("utf-8")
#         if bad_content in content:
#             raise Exception("Bad Request sent to API")
#         if r.status_code != 200:
#             raise Exception("Bad Request sent to API")
    
#     # TODO: Add assertions based on the elasticdump content
#     assert r.content != None


def wait_for_seconds(seconds):
    start_time = time.time()
    while time.time() - start_time < seconds:
        continue
