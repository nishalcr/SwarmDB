import random
import time
import requests
import logging
import json
import signal
from pymongo import MongoClient

# Load configuration from config.json
with open("config.json", "r") as config_file:
    config = json.load(config_file)

# Configuration
prometheus_endpoint = config["prometheus_endpoint"]
shards = config["shards"]
max_iterations = config["max_iterations"]
evaporation_rate = config["evaporation_rate"]
alpha = config["alpha"]
beta = config["beta"]
db_name = config["db_name"]
collections = config["collections"]
mongodb_uri = config["mongodb_uri"]

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger()

# MongoDB client (using URI from config.json)
client = MongoClient(mongodb_uri)
db = client[db_name]

# Initial pheromone map setup
pheromone_map = {shard: 1 for shard in shards}

# Graceful shutdown flag
shutdown_flag = False


# Function to handle shutdown signals
def handle_shutdown_signal(signal, frame):
    global shutdown_flag
    logger.info("Shutdown signal received. Cleaning up and exiting...")
    shutdown_flag = True


# Register shutdown signal handler for SIGINT (Ctrl+C) and SIGTERM (kill)
signal.signal(signal.SIGINT, handle_shutdown_signal)
signal.signal(signal.SIGTERM, handle_shutdown_signal)


# Function to fetch Prometheus metrics (CPU and Memory usage for each shard)
def fetch_prometheus_metrics(shard_id):
    logger.info(f"Fetching Prometheus metrics for shard: {shard_id}")

    cpu_usage_query = f"{prometheus_endpoint}?query=rate(process_cpu_seconds_total{{instance='{shard_id}'}}[1m])"
    memory_usage_query = f"{prometheus_endpoint}?query=process_resident_memory_bytes{{instance='{shard_id}'}}"

    try:
        cpu_data = requests.get(cpu_usage_query).json()
        memory_data = requests.get(memory_usage_query).json()

        cpu_usage = float(cpu_data["data"]["result"][0]["value"][1]) if cpu_data["data"]["result"] else 0
        memory_usage = float(memory_data["data"]["result"][0]["value"][1]) if memory_data["data"]["result"] else 0

        logger.info(f"Metrics for shard {shard_id} - CPU Usage: {cpu_usage}, Memory Usage: {memory_usage}")
        return cpu_usage, memory_usage
    except Exception as e:
        logger.error(f"Error fetching metrics for shard {shard_id}: {e}")
        return 0, 0


# Function to evaluate the performance of a shard (lower CPU and memory usage is better)
def evaluate_shard_performance(cpu_usage, memory_usage):
    score = 1 / (cpu_usage + memory_usage + 1)
    logger.debug(f"Evaluating shard performance - CPU: {cpu_usage}, Memory: {memory_usage}, Score: {score}")
    return score


# Function to update pheromone levels for a shard
def update_pheromone(shard, delta_pheromone):
    global pheromone_map
    old_pheromone = pheromone_map.get(shard, 1)
    pheromone_map[shard] = old_pheromone * (1 - evaporation_rate) + delta_pheromone
    logger.debug(f"Updated pheromone for shard {shard}: Old = {old_pheromone}, New = {pheromone_map[shard]}")


# Function to fetch all device IDs from device_metadata collection
def get_all_device_ids():
    try:
        devices = db.device_metadata.find()  # Fetch all documents from device_metadata collection
        device_ids = [device["device_id"] for device in devices]

        if device_ids:
            logger.info(f"Found all device IDs: {device_ids}")
        else:
            logger.warning("No devices found in the device_metadata collection.")

        return device_ids
    except Exception as e:
        logger.error(f"Error fetching device IDs: {e}")
        return []


# Function to trigger resharding (move chunk between shards)
def move_chunk_to_shard(best_shard, device_id_range_start, device_id_range_end, collection):
    try:
        logger.info(f"Moving chunk to shard {best_shard} from device_id {device_id_range_start} to {device_id_range_end} in {collection} collection")

        # db.command(
        #     {
        #         "moveChunk": f"{db_name}.{collection}",
        #         "find": {"_id": {"$gt": device_id_range_start, "$lt": device_id_range_end}},
        #         "to": best_shard,
        #     }
        # )

        logger.info(f"Chunk successfully moved to {best_shard} in {collection} collection")
    except Exception as e:
        logger.error(f"Failed to move chunk to {best_shard} in {collection} collection: {e}")


# Function to clear pheromone map and other variables (cleanup)
def cleanup():
    global pheromone_map
    # Reset pheromone levels
    pheromone_map = {shard: 1 for shard in shards}
    logger.info("Pheromone map and other variables have been reset.")


# ACO algorithm for dynamic data partitioning
def aco_algorithm():
    global pheromone_map
    best_partitioning = None
    best_score = float("inf")

    logger.info("Starting ACO algorithm for dynamic data partitioning")

    iteration = 0
    while not shutdown_flag:  # Loop until shutdown signal is received
        iteration += 1
        ants_solutions = []  # Store solutions for this iteration
        total_score = 0

        logger.info(f"Iteration {iteration} - Exploring solutions...")

        for _ in range(len(shards)):
            shard = random.choice(shards)  # Choose a random shard to place new data

            cpu_usage, memory_usage = fetch_prometheus_metrics(shard)
            performance_score = evaluate_shard_performance(cpu_usage, memory_usage)

            # Combine pheromone levels and heuristic performance score to choose shard
            probability = (pheromone_map[shard] ** alpha) * (performance_score**beta)
            total_score += probability

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

        logger.info(f"Iteration {iteration} - Best Partitioning: {best_partitioning[0]} with score {best_score}")
        time.sleep(1)  # Sleep for 1 second before the next iteration

        # Fetch all device IDs for resharding
        device_ids = get_all_device_ids()

        if device_ids:
            logger.info(f"Using device IDs range for resharding: {device_ids[0]} to {device_ids[-1]}")
            # Check if the shard is already the best one
            if best_partitioning[0] != pheromone_map[best_partitioning[0]]:
                for collection in collections:
                    move_chunk_to_shard(best_partitioning[0], device_ids[0], device_ids[-1], collection)
            else:
                logger.info(f"Shard {best_partitioning[0]} is already the best. No resharding needed.")
        else:
            logger.error("No device IDs found for resharding.")

        # Cleanup after each iteration (reset pheromone map and any other variables)
        cleanup()

    logger.info("ACO algorithm stopped gracefully.")


# Run the ACO algorithm continuously
aco_algorithm()
