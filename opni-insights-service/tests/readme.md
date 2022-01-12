## Validation scripts for Insights Service

Validation tests are run in a similar way to integration tests.

## Test Environment Setup:

Setup a Kubernetes cluster and save the Kubeconfig to the `.kube/config` file.

### Install Opni:

Follow the `Prerequisites` and `Clone the Opni repo` steps of the Advanced Installation instructions in the [Opni documentation](https://opni.io/deployment/advanced/).

In the Opni repo, open the file `./deploy/kustomization.yaml`, and uncomment the line `- patches/insights.yaml # edit this file to configure your Insights server`.

Inside the file, locate the log adapter appropriate for your cluster type, and uncomment that line.

Complete the remaining steps of the Opni Advanced Installation instructions.

#### Deploy Elasticdump-bash Pod

Run the command:
```
kubectl apply -f opni-insights-service/tests/sonobuoy/elasticdump-bash.yaml
```

##### Execute Elasticdump

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

Unzip the test results tar.gz file to review the test results.

## Helpful docs:

Opni Advanced Installation Docs: https://opni.io/deployment/advanced/

PyTest Docs: https://docs.pytest.org/en/6.2.x/

Elasticsearch Docs: https://www.elastic.co/guide/en/elasticsearch/reference/current/index.html

Elasticdump Docs: https://github.com/elasticsearch-dump/elasticsearch-dump