1) SETUP and install node explorer 
wget https://github.com/prometheus/node_exporter/releases/latest/download/node_exporter-1.10.2.linux-amd64.tar.gz

tar -xvf node_exporter-1.10.2.linux-amd64.tar.gz
cd node_exporter-1.10.2.linux-amd64
./node_exporter

check localhost:9100/metrics

2) install prometheus
wget https://github.com/prometheus/prometheus/releases/download/v3.10.0/prometheus-3.10.0.linux-amd64.tar.gz

tar -xvf prometheus-3.10.0.linux-amd64.tar.gz
cd prometheus-3.10.0.linux-amd64

3) configure 
nano prometheus.yml

replace with:
global:
  scrape_interval: 5s

scrape_configs:
  - job_name: "node_exporter"
    static_configs:
      - targets: ["localhost:9100"]


4) install grafana
sudo dnf install grafana -y

setuP:
sudo systemctl daemon-reload
sudo systemctl enable grafana-server
sudo systemctl start grafana-server

open:
http://localhost:3000

default cred:
admin
admin

add datasource
http://localhost:9090

u can see dashaboard graph

add id of node explorer 1860 and see the graph


5) install docker or podman

6)set nvidia
podman run --rm --security-opt=label=disable \
  --hooks-dir=/usr/share/containers/oci/hooks.d/ \
  docker.io/nvidia/cuda:12.3.0-base-ubuntu22.04 nvidia-smi

sudo dnf install nvidia-container-toolkit -y

sudo nvidia-ctk cdi generate --output=/etc/cdi/nvidia.yaml

7) run nvidia  dcgm exporter
podman pull docker.io/nvidia/dcgm-exporter:latest

podman run -d \
  --name dcgm-exporter \
  --security-opt=label=disable \
  --device nvidia.com/gpu=all \
  -p 9400:9400 \
  docker.io/nvidia/dcgm-exporter:latest

*) add in prometgeus.yml
 - job_name: "gpu"
    static_configs:
      - targets: ["localhost:9400"] 

add id of gpu in grafana
12239 in import dashboard

8) kafka metrics

pull kafka image

podman run -d \
  --name kafka-exporter \
  -p 9308:9308 \
  docker.io/danielqsj/kafka-exporter \
  --kafka.server=host.containers.internal:9092
  test metrics:
  http://localhost:9308/metrics

  add to prometheus.yml
    

        - job_name: "kafka"
    static_configs:
      - targets: ["localhost:9308"]


      




*) how to restart services
podman start dcgm-exporter
podman start kafka-exporter




climate_platform
cli_env
-dashboard
 -dashboard.py
-kafka
 -kafka/bin ..etc
-mock_weather_api/app.py ..etc
-nlp-service
 -nlp_venv
 -app.py
 -nlp_consumer.py
-spark
 -spark/bin/conf ..etc
 -climate_stream.py  