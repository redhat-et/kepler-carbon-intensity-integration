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

# Create Kafka topic
```sh
# kubectl -n kafka run kafka-producer -ti --image=quay.io/strimzi/kafka:0.30.0-kafka-3.2.0 --rm=true -- sh
```

In side the Kafka pod, run:

```sh
bin/kafka-topics.sh --bootstrap-server my-cluster-kafka-bootstrap:9092 --create --topic co2-topic --replication-factor 1
```

## Test topic
In the kafka pod, create some messages:

```sh
./bin/kafka-console-producer.sh --broker-list my-cluster-kafka-bootstrap:9092 --topic co2-topic 
```

Receive messages:
```sh
./bin/kafka-console-consumer.sh --bootstrap-server  my-cluster-kafka-bootstrap:9092 --topic co2-topic --from-beginning
```