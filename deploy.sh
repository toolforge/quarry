#!/bin/bash

set -e

if ! command -v kubectl ; then
  echo "please install kubectl"
  exit 1
fi

if ! command -v helm ; then
  echo "please install helm"
  exit 1
fi

if ! command -v terraform ; then
  echo "please install terraform"
  exit 1
fi

cd terraform
terraform init
terraform apply # -auto-approve
export KUBECONFIG=$(pwd)/kube.config

cd ../
kubectl create namespace quarry --dry-run=client -o yaml | kubectl apply -f -
helm -n quarry upgrade --install quarry helm-quarry -f helm-quarry/prod-env.yaml
