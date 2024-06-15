# Quarry
[Quarry](https://quarry.wmcloud.org/) is a web service that allows to perform SQL 
queries against Wikipedia and sister projects databases.

## Setting up a local dev environment ##

# docker-compose
Quarry uses [Docker](https://docs.docker.com/engine/install/) to set up a local
environment. You can set it up by:

1. [Download](https://docs.docker.com/engine/install/) and install Docker and
   [docker-compose](https://docs.docker.com/compose/) (already ships with docker on Windows and Mac)
3. Clone the [Quarry repository](https://github.com/wikimedia/analytics-quarry-web)
4. Run `docker-compose up`

A web server will be setup, available at http://localhost:5000. Change to python
files will trigger an automatic reload of the server, and your modifications
will imediatelly be taken into account.
A worker node is also created to execute your queries in the background (uses the
same image). Finally, redis and two database instances are also started.

To stop, run `docker-compose stop` or hit CTRL-C on the terminal your docker-compose
is running in. After that, to start with code changes, you'll want to `docker-compose down`
to clean up. Also, this creates a docker volume where sqlite versions of query
results are found. That will not be cleaned up unless you run `docker-compose down -v`



# minikube
It is possible to run a quarry system inside [minikube](https://minikube.sigs.k8s.io/docs/)!
At this time, you need to set it up with a cluster version before 1.22, most likely.

First build the containers:
```
eval $(minikube docker-env)
docker build . -t quarry:01
cd docker-replica/
docker build . -t mywiki:01
```

You will need to install minikube (tested on minikube 1.23) and [helm](https://helm.sh) and kubectl on your system. When you are confident those are working, start minikube with:
 - `minikube start --kubernetes-version=v1.23.15`
 - `minikube addons enable ingress`
 - `kubectl create namespace quarry`
 - `helm -n quarry install quarry helm-quarry -f helm-quarry/dev-env.yaml`

The rest of the setup instructions will display on screen as long as the install is successful.

# local databases
Both local setups will create two databases.

One database is your quarry database the other is a wikireplica-like database
named `mywiki`. This (or `mywiki_p`) is the correct thing to enter in the
database field on all local test queries.

The other database is the Quarry internal db. In your local environment, you can query Quarry internal db itself. Use then
"quarry" as database name.

### Updating existing containers ###

If you had already run a dev environment (that is, ran `docker-compose up`) you might want to update
the containers with the new dependencies by running `docker-compose build` before running
`docker-compose up` again.


## Useful commands ##

To pre-compile nunjucks templates:
`nunjucks-precompile quarry/web/static/templates/ > quarry/web/static/templates/compiled.js`

See also commands listed in the mainters documentation:
https://wikitech.wikimedia.org/wiki/Portal:Data_Services/Admin/Quarry

## Comment to Phabricator ##

To have a PR make comments to an associated phabricator ticket have the last line of the commit look like:

Bug: <ticket number>

For example:
Bug: T317566

## git-crypt ##

git-crypt is used to encrypt the config.yaml file. To decrypt ask a maintainer for the decryption key and:
```
git clone https://github.com/toolforge/quarry.git
cd quarry
git-crypt unlock <path to decryption key>
```

## Deploying to production ##
From the quarry-bastion:
`git clone https://github.com/toolforge/quarry.git`
`cd quarry`
`git checkout <branch>` If not deploying main
`git-crypt unlock <path to key>`
`bash deploy.sh`
In horizon point the web proxy at the new cluster.

### Fresh deploy ###
For a completely fresh deploy, and nfs server will need to be setup. Add its hostname to helm-quarry/prod-env.yaml.
And an object store will need to be generated for the tofu state file. Named "tofu-state"
And setup mysql:
`mysql -uquarry -h <trove hostname created in by tofu> -p < schema.sql`

## troubleshooting ##
If ansible doesn't detect a change for quarry helm the following can be run:
`helm -n quarry upgrade --install quarry helm-quarry -f helm-quarry/prod-env.yaml`
