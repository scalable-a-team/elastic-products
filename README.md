# elastic-products
# Usage for starting cluster

# start minikube

minikube start

# install yaml files to helm

helm install elasticsearch-multi-master elastic/elasticsearch -f ./master.yaml

helm install elasticsearch-multi-data elastic/elasticsearch -f ./data.yaml

helm install elasticsearch-multi-client elastic/elasticsearch -f ./client.yaml
