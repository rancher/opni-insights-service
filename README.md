# Opni Insights service

* This repository builds the opni-insights image which sets up an HTTP server. It sets up endpoints for many different insights between any time interval.
    * Breakdown of normal, suspicious and anomalous log message by pod through the pod endpoint
    * Breakdown of normal, suspicious and anomalous log messages by namespace through the namespace endpoint.
    * Breakdown of normal, suspicious and anomalous log messages by workload through the workload endpoint.
    * Breakdown of normal, suspicious and anomalous log messages by control plane component through the control_plane endpoint.
    * Overall breakdown of normal, suspicious and anomalous log messages through the overall_insights endpoint.
    * Log messages that are marked as Suspicious or Anomaly with additional metadata about each log message through the logs endpoint.
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

* For example, to fetch the breakdown of log messages by workload between the timestamps 1631794584000 and 1631855784000, you can run this command to make a Get request to the workload endpoint:
```
curl --location --request GET 'localhost:8000/workload?start_ts=1631794584000&end_ts=1631855784000' --header 'Content-Type: application/json'
```

* To make a call to either the pod, namespace, overall_insights or logs endpoint, simply replace workload in the curl command above with the respective term.

* The resulting output will look something like this:
```
{"ReplicaSet":[{"Name":"cattle-cluster-agent","Namespace":"cattle-system","Insights":{"Normal":17,"Suspicious":382,"Anomaly":0}},{"Name":"adservice","Namespace":"default","Insights":{"Normal":94047,"Suspicious":1528,"Anomaly":0}},{"Name":"cartservice","Namespace":"default","Insights":{"Normal":169639,"Suspicious":0,"Anomaly":0}},{"Name":"checkoutservice","Namespace":"default","Insights":{"Normal":17577,"Suspicious":0,"Anomaly":0}},{"Name":"currencyservice","Namespace":"default","Insights":{"Normal":851030,"Suspicious":0,"Anomaly":40}},{"Name":"emailservice","Namespace":"default","Insights":{"Normal":36197,"Suspicious":0,"Anomaly":0}},{"Name":"frontend","Namespace":"default","Insights":{"Normal":519563,"Suspicious":0,"Anomaly":3}},{"Name":"loadgenerator","Namespace":"default","Insights":{"Normal":519111,"Suspicious":30536,"Anomaly":0}},{"Name":"paymentservice","Namespace":"default","Insights":{"Normal":11717,"Suspicious":0,"Anomaly":34}},{"Name":"productcatalogservice","Namespace":"default","Insights":{"Normal":0,"Suspicious":0,"Anomaly":0}},{"Name":"recommendationservice","Namespace":"default","Insights":{"Normal":257676,"Suspicious":0,"Anomaly":0}},{"Name":"redis-cart","Namespace":"default","Insights":{"Normal":711,"Suspicious":299,"Anomaly":0}},{"Name":"shippingservice","Namespace":"default","Insights":{"Normal":93100,"Suspicious":0,"Anomaly":0}},{"Name":"ui-service","Namespace":"default","Insights":{"Normal":0,"Suspicious":0,"Anomaly":0}},{"Name":"fleet-agent","Namespace":"fleet-system","Insights":{"Normal":17,"Suspicious":382,"Anomaly":0}},{"Name":"jupyterlab","Namespace":"jlab","Insights":{"Normal":9,"Suspicious":428,"Anomaly":48}},{"Name":"coredns","Namespace":"kube-system","Insights":{"Normal":0,"Suspicious":0,"Anomaly":0}},{"Name":"opni-demo","Namespace":"opni-demo","Insights":{"Normal":7,"Suspicious":27,"Anomaly":0}},{"Name":"minio","Namespace":"opni-demo","Insights":{"Normal":0,"Suspicious":0,"Anomaly":0}},{"Name":"opendistro-es-client","Namespace":"opni-demo","Insights":{"Normal":0,"Suspicious":0,"Anomaly":0}},{"Name":"opendistro-es-kibana","Namespace":"opni-demo","Insights":{"Normal":0,"Suspicious":0,"Anomaly":0}},{"Name":"rancher-logging","Namespace":"opni-demo","Insights":{"Normal":0,"Suspicious":0,"Anomaly":0}},{"Name":"opni-controller-manager","Namespace":"opni-system","Insights":{"Normal":7,"Suspicious":27,"Anomaly":0}}],"StatefulSet":[{"Name":"nats","Namespace":"opni-demo","Insights":{"Normal":0,"Suspicious":0,"Anomaly":0}},{"Name":"opendistro-es-data","Namespace":"opni-demo","Insights":{"Normal":0,"Suspicious":0,"Anomaly":0}},{"Name":"opendistro-es-master","Namespace":"opni-demo","Insights":{"Normal":0,"Suspicious":0,"Anomaly":0}},{"Name":"rancher-logging","Namespace":"opni-demo","Insights":{"Normal":0,"Suspicious":0,"Anomaly":0}}],"Deployment":[],"Job":[],"DaemonSet":[{"Name":"aws-node","Namespace":"kube-system","Insights":{"Normal":0,"Suspicious":0,"Anomaly":0}},{"Name":"kube-proxy","Namespace":"kube-system","Insights":{"Normal":0,"Suspicious":0,"Anomaly":0}},{"Name":"opni-demo","Namespace":"opni-demo","Insights":{"Normal":0,"Suspicious":0,"Anomaly":0}},{"Name":"rancher-logging","Namespace":"opni-demo","Insights":{"Normal":0,"Suspicious":0,"Anomaly":0}}],"CustomResource":[{"Name":"opni-demo","Namespace":"opni-demo","Insights":{"Normal":7,"Suspicious":27,"Anomaly":0}}],"Independent":[{"Name":"development-box","Namespace":"opni-demo","Insights":{"Normal":0,"Suspicious":0,"Anomaly":0}}]}
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
