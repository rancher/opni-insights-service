## Validation scripts for Insights Service

Validation tests are run in a similar way to integration tests.

## Test Environment Setup:

Setup a Kubernetes cluster and save the Kubeconfig to the `.kube/config` file.

### Install Opni:

Run the command: 
```
bash ./opni-insights-service/tests/sonobuoy/shell_scripts/install_opni.sh
```
#### Install Log Adapter:

Clone the Opni repo locally: https://github.com/rancher/opni

In the Opni repo, open the folder: `opni/deploy/examples/logAdapters`

Locate the log adapter appropriate for your cluster type, and install it using the following command:
```
kubectl apply -f {log/adapter/file/path}
```

##### Deploy Elasticdump-bash Pod

Run the command:
```
kubectl apply -f opni-insights-service/tests/sonobuoy/elasticdump-bash.yaml
```

###### Execute Elasticdump

Run the following command to obtain the es-client password:
```
kubectl get secret -n opni opni-es-password -o json | jq '.data | map_values(@base64d)' > es-password.json
sed -i -e '3d' es-password.json
sed -i -e '1d' es-password.json
sed -i -e 's/  "password": "//g' es-password.json
sed -i -e 's/"//g' es-password.json
```

Run the following command to access the Elasticdump-bash Pod:
```
kubectl exec -it elasticdump-bash -- /bin/bash
```

Run the following command to execute Elasticdump (be sure to replace the es-client password):
```
NODE_TLS_REJECT_UNAUTHORIZED=0 elasticdump --noRefresh --fileSize=1gb --retryAttempts 10 --retryDelay 2500 --fsCompress --limit 10000 --input=https://admin:ES-CLIENT-PASSWORD@opni-es-client.opni.svc.cluster.local:9200/logs --output "example.json" --type=data
```

## Run Sonobuoy Tests:

Run the command: 
```
bash ./opni-insights-service/tests/sonobuoy/shell_scripts/sonobuoy_run.sh
```

Unzip the test results tar.gz file to reveiw the test results.

## To run the Sonobuoy tests manually after Opni is already installed:

Run the command: 
```
sonobuoy run \
--kubeconfig ~/.kube/config \
--namespace "opni-sono" \
--plugin https://raw.githubusercontent.com/jameson-mcghee/opni-insights-service/insights-int-tests-jrm/opni-insights-service/tests/sonobuoy/opnisono-plugin.yaml
```

Periodically run the following command until the tests are complete:
```
sonobuoy status -n opni-sono
```

Run the following command and a tar file with the test results will be generated in the current directory:
```
sonobuoy retrieve -n opni-sono
```

Unzip the test results tar.gz file to reveiw the test results.

## Helpful docs:

Opni Advanced Installation Docs: https://opni.io/deployment/advanced/

PyTest Docs: https://docs.pytest.org/en/6.2.x/