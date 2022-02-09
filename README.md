# Quarry
[Quarry](https://quarry.wmcloud.org/) is a web service that allows to perform SQL 
queries against Wikipedia and sister projects databases.

## Setting up a local dev environment ##

It is possible to run a fully-functioning quarry system inside [minikube](https://minikube.sigs.k8s.io/docs/)!
At this time, you need to set it up with a cluster version before 1.22, most likely.

You will need to install minikube (tested on minikube 1.23) and [helm](https://helm.sh) and kubectl on your system. When you are confident those are working, start minikube with:
 - `minikube start --kubernetes-version=v1.20.11`
 - `minikube addons enable ingress`
 - `kubectl create namespace quarry`
 - `helm -n quarry install quarry helm-quarry -f helm-quarry/dev-env.yaml`

The rest of the setup instructions will display on screen as long as the install is successful.

Two databases are created.
One database is your quarry database the other is a wikireplica-like database
named `mywiki`. This (or `mywiki_p`) is the correct thing to enter in the
database field on all local test queries.

In your local environment, you can query Quarry internal db itself. Use then
"quarry" as database name.

## Useful commands ##

To pre-compile nunjucks templates:
`nunjucks-precompile quarry/web/static/templates/ > quarry/web/static/templates/compiled.js`

See also commands listed in the mainters documentation:
https://wikitech.wikimedia.org/wiki/Portal:Data_Services/Admin/Quarry
