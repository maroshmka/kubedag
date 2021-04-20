#!/usr/bin/env bash

set -ex

# todo - cleanup all ? careful
kubectl delete cronjob tutorial-dummy-first-task || true
kubectl delete configmap kubedag-graph || true
kubectl delete serviceaccount sa-runner || true
kubectl delete role cfg-reader || true
kubectl delete rolebinding read-cfg || true

python3 -m kubedag.deploy

# needed to see images in minikube
eval $(minikube docker-env)
echo "building runner docker image"
docker build -t kubedag-runner -f runner.Dockerfile .
docker build -t mydags -f mydags.Dockerfile .


echo "testing a job"
kubectl create job --from=cronjob/tutorial-dummy-first-task test-hmka
kubectl get pods
