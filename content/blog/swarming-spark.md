---
title: "Swarming Spark"
date: 2015-04-30
slug: ""
description: ""
keywords: []
draft: false
tags: []
math: false
toc: false
---

[Spark](https://spark.apache.org/) is a useful bunch of stuff for processing large amounts of data, offering a friendly and fast functional interface over map-reduce on a cluster of machines, with some extra bits like cacheable datasets. It’s relatively easy to get running too (although with a list of gotchas), with scripts to start a stand-alone cluster on EC2, or pretty simple tutorials for running on mesos, and their deployment guides give a good overview of the raw process.

But there are a bunch of new cluster management services popping up that rely on [docker](https://www.docker.com/): [ECS](http://aws.amazon.com/ecs/) (on EC2), [GCE](https://cloud.google.com/container-engine/) (on google), [Mesos](http://mesos.apache.org/) now takes docker containers, and Azure. Elastic beanstalk had some support. Docker is clearly the new hotness for packaging something like Spark, but the Docker container does not contain enough information on it’s own to get a cluster system like Spark running. For that you need to allow the workers to discover the master, allow the driver to access the master from outside, replicate workers, etc, etc. All this can be done, but there’s no standard for it. Each container cluster manager has a slightly different approach. You can find docker containers for Spark, but they tend not to be extremely portable which seems a bit broken.

So the itch I want to scratch is ‘Can we build docker containers for Spark that easily run on more than one cluster manager, say GCE (which implements [kubernetes](http://kubernetes.io/)) and ECS?. Also, how good are the cross-provider service layers like kubernetes and [swarm](https://docs.docker.com/swarm/?’ There seem to be 3 levels of difficulty here. The first is getting the master and workers all running. The second is getting them to find and talk to each other. The third is allowing a driver (which in spark is also part of the akka cluster) to talk to them all.

Getting them running is easy. Spark comes with sensible shell scripts to start each, and wrapping them in docker is no problem. For Kubernetes (GCS), we can just run the master as a pod, and the workers under a replication controller (and hence N pods). For ECS the story is almost identical, and the json configuration even looks very similar.

Getting them to talk to each other is a bit more tricky. Background: Docker doesn’t come with any built-in discovery mechanisms. You can link containers together on a single host, but not across multiple hosts (without external help). They used to suggest the ambassador pattern for this, but now docker is working on swarm. Kubernetes allows you to describe ‘services’ which can be found via environment variables or optionally DNS. [Flannel](https://github.com/coreos/flannel) tries to follow kubernetes. [Weave](http://weave.works/) kind of sits around docker and creates a complete network around containers, but is not what GCE or ECS use natively, so I’ll ignore it here.

So, once we have the master up, it has an address. In Kubernetes we can create a service to expose the master as a fixed entity (binding to it based on name), and then the workers can know it’s IP address and port through environment variables, so you need to make sure you start the worker in a shell so it can do the variable substitution. But here we run into a little difficulty in that Akka is picky about what hostname actors are bound to. So it’s actually best to configure the workers to find the master through `KUBE_DNS`, which our service has exposed as spark-master, so the startup script actually needs to configure `/etc/resolv.conf`. ECS doesn’t by default support anything outside docker so this would require manual labour – I suppose for that we would have to implement the ambassador pattern for this?. This is looking less easy!

But there’s a light at the end of the tunnel here. Kubernetes will also run on EC2 (bypassing ECS), so we can take the same configuration we used on GCE and spin it up on Amazon! Well, with the small wrinkle that the external address of our master service is just the public IP of the host host the container is running on, rather than one allocated to the service itself as in GCE. Indeed if you add ‘createExternalLoadBalancer’ to our service descriptor ECS complains, so our master service json file needs to be slightly different between GCE and ECS.

What about Swarm? It’s a bit of a newbie here, but it promises to extend the `–link` mechanism of docker across hosts that are clustered in a swarm (perhaps started with `docker-machine –swarm`). And guess what, it does! In fact, this was the easiest way to get things going. I can even get rid of the `resolv.conf` hack. Here’s how:

Docker-compose works nicely to configure how our application will be structured, so a short `docker-compose.yaml` file shows the master and how it’s used by the worker:

```Dockerfile
master:
image: snufkin/spark-master
hostname: spark-master
ports:
- "8080"
- "4040"
- "7077:7077"
expose:
- "7077"
worker:
image: snufkin/spark-worker
ports:
- "8081"
links:
- master:spark-master
```

We use `docker-machine` to start our machines on google compute engine or EC2. A simple shell script does for this.

```bash
docker-machine create -d virtualbox local
eval "$(docker-machine env local)"
export SWARMID=`docker run swarm create`
echo $SWARMID
docker-machine create -d amazonec2 --amazonec2-access-key $AWSKEY --amazonec2-region $REGION --amazonec2-secret-key $AWSSECKEY --amazonec2-vpc-id $VPCID --swarm --swarm-master --swarm-discovery token://$SWARMID swarm-master
# would be nice to use gnu parallel here, but fails when faced with the google oauth calls if you're using the google driver
for i in $(seq 1 $NUMNODES); do
docker-machine create -d amazonec2 --amazonec2-access-key $AWSKEY --amazonec2-region $REGION --amazonec2-secret-key $AWSSECKEY --amazonec2-vpc-id $VPCID --swarm --swarm-discovery token://$SWARMID swarm-node-$i;
done;
eval $(docker-machine env --swarm swarm-master)
docker info
docker-compose up -d
docker-compose scale worker=3
docker-compose logs
docker ps
```

Then find out the public IP of the host the master is running on, open port 7077 to said host (security groups or network config on the cloud provider), add the host to your `/etc/hosts` as spark-master (to satisfy Akka, which is picky about hostnames), and try something like

```bash
spark$ ./bin/spark-shell --master spark://spark-master:7077
```

See, easy!



(http://web.archive.org/web/20161006223524/http://www.lshift.net/blog/2015/04/30/swarming-spark/)