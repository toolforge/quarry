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

if ! command -v tofu; then
  echo "please install tofu"
  exit 1
fi

python3 -m venv .venv/deploy
source .venv/deploy/bin/activate
pip install ansible==8.1.0 kubernetes==26.1.0

cd tofu 
tofu init
tofu apply # -auto-approve
export KUBECONFIG=$(pwd)/kube.config

cd ../ansible
ansible-playbook quarry.yaml
#kubectl create namespace quarry --dry-run=client -o yaml | kubectl apply -f -
#helm -n quarry upgrade --install quarry helm-quarry -f helm-quarry/prod-env.yaml

