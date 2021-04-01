#!/usr/bin/env bash

set -ex

kubectl delete cronjob hello || true
kubectl delete configmap kubedag-graph || true

python3 deploy.py

# needed to see images in minikube
eval $(minikube docker-env)
echo "building runner docker image"
docker build -t kubedag-runner -f runner.Dockerfile .
docker build -t mydags -f mydags.Dockerfile .

echo "testing a job"
kubectl create job --from=cronjob/hello test-hmka
kubectl get pods
