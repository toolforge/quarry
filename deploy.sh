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

source secrets.sh

python3 -m venv .venv/deploy
source .venv/deploy/bin/activate
pip install ansible==8.1.0 kubernetes==26.1.0
# install helm diff. Needed to keep helm module idempotent
helm plugin install https://github.com/databus23/helm-diff || true
# update kubernetes.core. This path will likely need updated with bastion os upgrades.
ansible-galaxy collection install -U kubernetes.core -p ./.venv/deploy/lib/python3.11/site-packages/ansible_collections

cd tofu
AWS_ACCESS_KEY_ID=${ACCESS_KEY} AWS_SECRET_ACCESS_KEY=${SECRET_KEY} tofu init
AWS_ACCESS_KEY_ID=${ACCESS_KEY} AWS_SECRET_ACCESS_KEY=${SECRET_KEY} tofu apply # -auto-approve
export KUBECONFIG=$(pwd)/kube.config

cd ../ansible
ansible-playbook quarry.yaml
#kubectl create namespace quarry --dry-run=client -o yaml | kubectl apply -f -
#helm -n quarry upgrade --install quarry helm-quarry -f helm-quarry/prod-env.yaml

