from pymongo import MongoClient
from pymongo.errors import ConnectionFailure
import time

# MongoDB connection details
config_server_host = "localhost:27019"  # Host for config server
shard1_host = "localhost:27017"  # Host for shard1 primary
root_username = "root"
root_password = "rootPassword"


# Function to initialize the replica set on a node
def initiate_replica_set(client, replica_set_name):
    print(f"Initializing replica set: {replica_set_name}")
    try:
        # Wait until MongoDB is up
        while True:
            try:
                client.admin.command("ping")  # This will succeed if MongoDB is up
                print(f"MongoDB at {client.address[0]} is up and running.")
                break
            except:
                print(f"Waiting for MongoDB at {client.address[0]} to be ready...")
                time.sleep(2)  # Wait before checking again

        # Replica set configuration
        replica_set_config = {
            "_id": replica_set_name,
            "members": [{"_id": 0, "host": f"{client.address[0]}:27017"}],
        }

        # Initiate the replica set
        client.admin.command("replSetInitiate", replica_set_config)
        print(f"Replica set {replica_set_name} initiated successfully.")

        # Wait for replica set status
        time.sleep(5)  # Wait for replica set initialization to propagate
        status = client.admin.command("replSetGetStatus")
        print("Replica Set status:", status)

    except Exception as e:
        print(f"Error initiating replica set {replica_set_name}: {e}")
        return None


# Initialize MongoDB connection to the config server
client = MongoClient(f"mongodb://{root_username}:{root_password}@{config_server_host}")

try:
    # Initiate replica set for the config server
    initiate_replica_set(client, "configReplSet")

    # Initiate replica sets for shard nodes (repeat for each shard)
    client_shard1 = MongoClient(
        f"mongodb://{root_username}:{root_password}@{shard1_host}"
    )
    initiate_replica_set(client_shard1, "shardReplSet1")

    print("MongoDB Cluster initialized successfully!")

except ConnectionFailure:
    print("Failed to connect to MongoDB server.")
except Exception as e:
    print(f"Error initializing MongoDB cluster: {e}")
finally:
    client.close()
