import time
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure

MONGODB_URI = "mongodb://mongo_router:27017"  # Mongo router service URI


def wait_for_mongo_router():
    """Waits for the MongoDB Router to be available before continuing."""
    client = None
    while client is None:
        try:
            print("Waiting for MongoDB Router to be available...")
            client = MongoClient(MONGODB_URI)
            client.admin.command("ping")  # Check if the router is accessible
            print("MongoDB Router is now available!")
        except ConnectionFailure:
            print("MongoDB Router not yet available, retrying...")
            time.sleep(5)  # Wait for 5 seconds before retrying


def initiate_replica_set(client, replica_set_name, members):
    """Initiates a MongoDB replica set."""
    config = {"_id": replica_set_name, "members": members}
    client.admin.command("replSetInitiate", config)
    print(f"Replica set {replica_set_name} initiated.")


def add_shard(client, shard_name):
    """Adds a shard to the MongoDB cluster."""
    client.admin.command("addShard", shard_name)
    print(f"Shard {shard_name} added to the cluster.")


def enable_sharding_for_database(client, database_name):
    """Enables sharding for a specific database."""
    client.admin.command("enableSharding", database_name)
    print(f"Sharding enabled for database {database_name}.")


def shard_collection(client, database_name, collection_name, key):
    """Shards a collection in the specified database."""
    client.admin.command(
        "shardCollection", f"{database_name}.{collection_name}", key=key
    )
    print(f"Collection {collection_name} sharded in database {database_name}.")


def configure_mongo_cluster():
    """Configures the MongoDB Cluster with replica sets and sharding."""

    # Wait for MongoDB Router to be ready
    wait_for_mongo_router()

    # Connect to the MongoDB router
    client = MongoClient(MONGODB_URI)
    print("Connected to MongoDB Router...")

    # Step 1: Initialize Config Servers Replica Set
    print("Initializing config server replica set...")
    initiate_replica_set(
        client,
        "cfg",
        [
            {"_id": 0, "host": "mongo_config_server_1:27017"},
            {"_id": 1, "host": "mongo_config_server_2:27017"},
            {"_id": 2, "host": "mongo_config_server_3:27017"},
        ],
    )
    time.sleep(5)  # Wait for replica set initialization

    # Step 2: Initialize Shard 1 Replica Set
    print("Initializing shard 1 replica set...")
    initiate_replica_set(
        client,
        "shard1",
        [
            {"_id": 0, "host": "mongo_shard_1_rep_1:27017"},
            {"_id": 1, "host": "mongo_shard_1_rep_2:27017"},
            {"_id": 2, "host": "mongo_shard_1_rep_3:27017"},
        ],
    )
    time.sleep(5)

    # Step 3: Initialize Shard 2 Replica Set
    print("Initializing shard 2 replica set...")
    initiate_replica_set(
        client,
        "shard2",
        [
            {"_id": 0, "host": "mongo_shard_2_rep_1:27017"},
            {"_id": 1, "host": "mongo_shard_2_rep_2:27017"},
            {"_id": 2, "host": "mongo_shard_2_rep_3:27017"},
        ],
    )
    time.sleep(5)

    # Step 4: Add Shard 1 and Shard 2 to the MongoDB cluster
    print("Adding shards to the cluster...")
    add_shard(client, "shard1/mongo_shard_1_rep_1:27017")
    add_shard(client, "shard2/mongo_shard_2_rep_1:27017")
    time.sleep(5)

    # Step 5: Enable Sharding for the Database
    print("Enabling sharding for database 'shardedDB'...")
    enable_sharding_for_database(client, "shardedDB")

    # Step 6: Shard a Collection in the Database
    print("Sharding collection 'shardedCollection' in database 'shardedDB'...")
    shard_collection(client, "shardedDB", "shardedCollection", {"_id": "hashed"})
    time.sleep(5)

    # Step 7: Insert Sample Data into the Sharded Collection
    print("Inserting sample data into the sharded collection...")
    db = client["shardedDB"]
    collection = db["shardedCollection"]
    for i in range(1500):
        collection.insert_one({"x": i})
    print("Sample data inserted into the sharded collection.")

    # Step 8: Verify Shard Distribution
    print("Verifying shard distribution...")
    print(
        client["shardedDB"]["shardedCollection"].aggregate(
            [{"$group": {"_id": "$_shard", "count": {"$sum": 1}}}]
        )
    )


if __name__ == "__main__":
    configure_mongo_cluster()
