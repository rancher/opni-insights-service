# Opni Insights service

* This repository builds the opni-insights image which sets up an HTTP server. It sets up endpoints for many different insights between any time interval.
    * Breakdown of normal, suspicious and anomalous log message by pod, namespace and workload through the insights_breakdown endpoint
    * Breakdown of normal, suspicious and anomalous log messages by control plane component through the control_plane endpoint.
    * Overall breakdown of normal, suspicious and anomalous log messages through the overall_insights endpoint.
    * Log messages that are marked as Suspicious or Anomaly with additional metadata about each log message through the logs endpoint.
    * Areas of interest based on the number of anomalies per minute through the areas_of_interest endpoint.
    * Peak detection based on the number of anomalies per minute through the peaks endpoint.
### Setup RBAC permissions
```
kubectl apply -f rbac.yaml
```

### Methodology
* To try out the opni-insights-service, you can first port-forward the service.
```
kubectl port-forward svc/opni-insights-service 8000:80
```

* Then, send a get request to the endpoint to fetch insight data on pods, namespaces, workloads, logs or overall insights and specify the starting and ending time intervals to query that data from.

* For example, to fetch the overall breakdown of log messages between the timestamps 1631794584000 and 1631855784000, you can run this command to make a Get request to the workload endpoint:
```
curl --location --request GET 'localhost:8000/overall_insights?start_ts=1631794584000&end_ts=1631855784000' --header 'Content-Type: application/json'
```

* To make a call to either the pod, namespace, overall_insights or logs endpoint, simply replace workload in the curl command above with the respective term.

* The resulting output will look something like this:
```
{
    "Normal": 15913,
    "Suspicious": 1054,
    "Anomaly": 7341
}

```
* To fetch log messages between a starting and ending timestamp, you can run this command to make a Get request to the logs endpoint which will fetch 100 logs.
```
curl --location --request GET 'localhost:8000/logs?start_ts=1631794584000&end_ts=1631855784000' --header 'Content-Type: application/json'
```
In addition to returning 100 log messages as part of the current page, it will also return a scroll_id which can be used to access subsequent pages of log messages.

* To fetch log messages between a starting and ending timestamp and with a specified scroll_id, you can run this command to make a Get request to the logs endpoint which will fetch the next 100 logs from the reference of the scroll_id.
```
curl --location --request GET 'localhost:8000/logs?start_ts=1631794584000&end_ts=1631855784000&scroll_id=SCROLL_ID' --header 'Content-Type: application/json'
```




## Contributing
We use `pre-commit` for formatting auto-linting and checking import. Please refer to [installation](https://pre-commit.com/#installation) to install the pre-commit or run `pip install pre-commit`. Then you can activate it for this repo. Once it's activated, it will lint and format the code when you make a git commit. It makes changes in place. If the code is modified during the reformatting, it needs to be staged manually.

```
# Install
pip install pre-commit

# Install the git commit hook to invoke automatically every time you do "git commit"
pre-commit install

# (Optional)Manually run against all files
pre-commit run --all-files
```
