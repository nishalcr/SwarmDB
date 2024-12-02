import random
import time
import requests

# Configuration
prometheus_endpoint = "http://50.19.127.245:9090/api/v1/query"
shards = ["shard1", "shard2", "shard3"]  # MongoDB shards
max_iterations = 50  # Number of iterations for the ACO
pheromone_map = {shard: 1 for shard in shards}  # Initial pheromone levels for each shard
evaporation_rate = 0.1  # Pheromone evaporation rate
alpha = 1  # Influence of pheromone
beta = 2   # Influence of heuristic value (system metrics)

# Function to fetch Prometheus metrics (CPU and Memory usage for each shard)
def fetch_prometheus_metrics(shard_id):
    # Prometheus query to get CPU usage for the shard
    cpu_usage_query = f"{prometheus_endpoint}?query=rate(process_cpu_seconds_total{{instance='{shard_id}'}}[1m])"
    memory_usage_query = f"{prometheus_endpoint}?query=process_resident_memory_bytes{{instance='{shard_id}'}}"
    
    cpu_data = requests.get(cpu_usage_query).json()
    memory_data = requests.get(memory_usage_query).json()
    
    cpu_usage = float(cpu_data['data']['result'][0]['value'][1]) if cpu_data['data']['result'] else 0
    memory_usage = float(memory_data['data']['result'][0]['value'][1]) if memory_data['data']['result'] else 0
    return cpu_usage, memory_usage

# Function to evaluate the performance of a shard (lower CPU and memory usage is better)
def evaluate_shard_performance(cpu_usage, memory_usage):
    return 1 / (cpu_usage + memory_usage + 1)  # Lower usage = higher score

# Function to update pheromone levels for a shard
def update_pheromone(shard, delta_pheromone):
    pheromone_map[shard] = pheromone_map.get(shard, 1) * (1 - evaporation_rate) + delta_pheromone

# ACO algorithm for dynamic data partitioning
def aco_algorithm():
    global pheromone_map
    best_partitioning = None
    best_score = float('inf')
    
    for iteration in range(max_iterations):
        ants_solutions = []  # Store solutions for this iteration
        total_score = 0
        
        for _ in range(len(shards)):  # Each ant explores a possible solution
            shard = random.choice(shards)  # Choose a random shard to place new data
            
            # Fetch metrics (CPU and memory usage) for this shard
            cpu_usage, memory_usage = fetch_prometheus_metrics(shard)
            performance_score = evaluate_shard_performance(cpu_usage, memory_usage)
            
            # Combine pheromone levels and heuristic performance score to choose shard
            probability = (pheromone_map[shard] ** alpha) * (performance_score ** beta)
            total_score += probability
            
            # Track the best partitioning based on the highest probability
            ants_solutions.append((shard, performance_score, probability))
        
        # Update pheromone based on ant solution
        for solution in ants_solutions:
            shard, performance_score, probability = solution
            delta_pheromone = probability / total_score  # Normalize pheromone contribution
            update_pheromone(shard, delta_pheromone)
        
        # Track the best solution found
        if ants_solutions:
            best_partitioning = min(ants_solutions, key=lambda x: x[1])
            best_score = best_partitioning[1]
        
        print(f"Iteration {iteration+1}/{max_iterations} - Best Partitioning: {best_partitioning[0]} with score {best_score}")
        
        time.sleep(1)  # Simulate time between iterations
    
    print(f"Best Partitioning Strategy: {best_partitioning[0]}")

# Run the ACO algorithm to optimize data partitioning
aco_algorithm()
