import json
import os
from pymongo import MongoClient

# MongoDB connection details
MONGO_URI = "mongodb://52.71.233.218:27027/"  # Replace with your MongoDB URI
DB_NAME = "iot_device_data"  # Replace with your database name

# COLLECTION_NAME = "sensor_data"
# INPUT_FILE = "/Users/nishalcr/Documents/Nishal/MS/Sem_3/CSE_512_DDS/Project/SwarmDB/data/sensor_data_500K.ndjson"

# COLLECTION_NAME = "sensor_maintenance_data"
# INPUT_FILE = "/Users/nishalcr/Documents/Nishal/MS/Sem_3/CSE_512_DDS/Project/SwarmDB/data/sensor_maintenance_data_500K.ndjson"


COLLECTION_NAME = "sensor_monitoring_logs"
INPUT_FILE = "/Users/nishalcr/Documents/Nishal/MS/Sem_3/CSE_512_DDS/Project/SwarmDB/data/sensor_monitoring_logs_500K.ndjson"

# Batch size for bulk insert
BATCH_SIZE = 500  # Adjust based on your system's capability and the data size


def get_mongo_client(uri):
    """
    Connect to MongoDB and return the client.
    """
    client = MongoClient(uri)
    db = client[DB_NAME]
    return db[COLLECTION_NAME]  # Return the specified collection


def bulk_insert_to_mongo(collection, data_batch):
    """
    Insert a batch of data (multiple JSON objects) into MongoDB collection.

    :param collection: MongoDB collection to insert into.
    :param data_batch: List of data (dictionaries) to be inserted.
    """
    try:
        # Bulk insert the batch of data into the MongoDB collection
        if data_batch:
            collection.insert_many(data_batch)
            # print(f"Inserted {len(data_batch)} records into MongoDB")
    except Exception as e:
        print(f"Error during bulk insert into MongoDB: {e}")


def process_ndjson(input_file, collection):
    """
    Reads an NDJSON file line by line, parses each line and inserts into MongoDB in bulk.

    :param input_file: Path to the input NDJSON file.
    :param collection: MongoDB collection where records will be inserted.
    """
    data_batch = []
    line_number = 1

    with open(input_file, "r") as infile:
        for line in infile:
            try:
                # Parse the NDJSON line (each line is a valid JSON object)
                data = json.loads(line.strip())
                data_batch.append(data)
                line_number += 1

                # Perform bulk insert when the batch size is reached
                if len(data_batch) >= BATCH_SIZE:
                    bulk_insert_to_mongo(collection, data_batch)
                    data_batch = []  # Reset the batch after insertion
                
                print(f"total records inserted: {line_number}")
            except json.JSONDecodeError as e:
                print(f"Skipping invalid JSON line at line {line_number}: {e}")
                continue

        # Insert any remaining records after the loop
        if data_batch:
            bulk_insert_to_mongo(collection, data_batch)


if __name__ == "__main__":

    # Get MongoDB collection
    collection = get_mongo_client(MONGO_URI)

    # Process NDJSON file and insert each line to MongoDB
    process_ndjson(INPUT_FILE, collection)
