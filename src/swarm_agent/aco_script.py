import requests
import time
import random
import docker
from prometheus_client import Gauge

# Configuration
PROMETHEUS_URL = "http://prometheus:9090"  # Replace with your Prometheus URL
METRIC_QUERY = 'rate(http_requests_total[1m])'  # Query for HTTP request rate (example)
TRAFFIC_THRESHOLD = 1000  # Example traffic threshold for scaling
NODES = ['node1', 'node2', 'node3', 'node4']  # List of available nodes for replica creation

# Docker client setup
client = docker.from_env()

# Prometheus metrics - example custom metrics (for scaling decisions)
request_count = Gauge('http_requests_total', 'Total HTTP requests made')

# Function to query Prometheus for metrics
def get_prometheus_data(query):
    url = f"{PROMETHEUS_URL}/api/v1/query"
    response = requests.get(url, params={'query': query})
    
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Failed to fetch data from Prometheus: {response.status_code}")
        return None

# Function to check if the traffic exceeds the threshold
def check_threshold(traffic):
    return traffic > TRAFFIC_THRESHOLD

# Simple ACO Algorithm to select a node for scaling
def aco_algorithm(available_nodes, traffic_data):
    # Basic ACO-like approach: select the node with highest traffic and replicate on a different node
    busy_node = max(traffic_data, key=traffic_data.get)  # Find node with max traffic
    available_nodes.remove(busy_node)  # Remove busy node from the available nodes
    replica_node = random.choice(available_nodes)  # Choose a random node to replicate the busy node
    return replica_node

# Function to create a new Docker instance on a selected node
def create_docker_instance(replica_node, container_type="http-server"):
    # Use Docker SDK to create a new container on the selected node (node)
    image = "python:3.9-slim"  # Default image (replace with your custom image if needed)
    
    print(f"Creating new {container_type} instance on {replica_node}")
    
    # Example of creating a new container (adjust parameters as needed)
    container = client.containers.run(image, detach=True, command="python -m http.server 8080", 
                                      environment={'NODE_TYPE': container_type},
                                      networks=["mongo-cluster"])  # Attach to your network
    
    print(f"Started container {container.id} on {replica_node}")
    return container

# Function to update metrics and perform scaling decisions
def monitor_and_scale():
    while True:
        # Fetch metrics from Prometheus (request rate)
        metrics_data = get_prometheus_data(METRIC_QUERY)
        
        if metrics_data and "data" in metrics_data:
            # Example: Collect traffic data (here assuming data is for 4 nodes)
            traffic_data = {node: random.randint(500, 1500) for node in NODES}  # Simulated data
            for node in traffic_data:
                print(f"Traffic on {node}: {traffic_data[node]} requests per minute")
            
            # Check if any node exceeds the threshold
            if any(check_threshold(traffic) for traffic in traffic_data.values()):
                print("Threshold exceeded! Scaling required.")
                
                # Use ACO algorithm to decide which node to replicate
                replica_node = aco_algorithm(NODES.copy(), traffic_data)
                print(f"Scaling decision: Create replica on {replica_node}")
                
                # Create a new Docker instance on the selected node
                create_docker_instance(replica_node)
            else:
                print("Traffic is under control. No scaling required.")
        
        # Wait for the next check (e.g., every 60 seconds)
        time.sleep(60)

# Start monitoring and scaling
if __name__ == "__main__":
    monitor_and_scale()
