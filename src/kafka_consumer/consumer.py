from kafka import KafkaConsumer
from pymongo import MongoClient
import json

# Kafka configuration
TOPICS = ["iot_data", "system_metrics"]
KAFKA_BROKER = "kafka:9092"

# MongoDB configuration
MONGODB_URI = "mongodb://mongos:27020"
DATABASE_NAME = "iot_system"
COLLECTION_NAME = "iot_logs"

# Initialize Kafka consumer
consumer = KafkaConsumer(
    *TOPICS,
    bootstrap_servers=KAFKA_BROKER,
    value_deserializer=lambda m: json.loads(m.decode('utf-8'))
)

# Initialize MongoDB client
mongo_client = MongoClient(MONGODB_URI)
db = mongo_client[DATABASE_NAME]
collection = db[COLLECTION_NAME]

# Process messages
for message in consumer:
    data = message.value
    collection.insert_one(data)
    print(f"Inserted: {data}")
