#!/bin/bash
# sonobuoy_run.sh
# assume Opni and log adapters are already installed

sonobuoy run \
--kubeconfig ~/.kube/config \
--namespace "opni-sono" \
--plugin https://raw.githubusercontent.com/jameson-mcghee/opni-insights-service/insights-int-tests-jrm/opni-insights-service/tests/sonobuoy/opnisono-plugin.yaml
sleep 2
for i in {1..5}; do sonobuoy logs -n opni-sono && break || sleep 1; done
for i in {1..60}; do sonobuoy retrieve -n opni-sono && break || sleep 5; done
sonobuoy status -n opni-sono
sonobuoy delete --wait
kubectl delete namespace opni-sono