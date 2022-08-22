# Install Strimiz, create a Kafka cluster
Per the tutorial [here](https://strimzi.io/quickstarts/)

```bash
kubectl create namespace kafka
kubectl create -f 'https://strimzi.io/install/latest?namespace=kafka' -n kafka
kubectl apply -f https://strimzi.io/examples/latest/kafka/kafka-persistent-single.yaml -n kafka 
```

```console
#kubectl get -n kafka kafka/my-cluster
# kubectl get -n kafka kafka/my-cluster
NAME         DESIRED KAFKA REPLICAS   DESIRED ZK REPLICAS   READY   WARNINGS
my-cluster   1                        1                     True    
```