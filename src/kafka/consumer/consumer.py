import os
import json
import logging
import sys
from pymongo import MongoClient
from confluent_kafka import Consumer, KafkaException, KafkaError

# Set log level based on environment variable, default to WARNING
log_level = os.environ.get("LOG_LEVEL", "WARNING").upper()
log_levels = {
    "DEBUG": logging.DEBUG,
    "INFO": logging.INFO,
    "WARNING": logging.WARNING,
    "ERROR": logging.ERROR,
    "CRITICAL": logging.CRITICAL,
}
logging.basicConfig(
    format="%(asctime)s - %(levelname)s - %(message)s", level=log_levels.get(log_level, logging.INFO)
)  # Default to INFO if invalid level
logger = logging.getLogger(__name__)


# Load configuration from the config.json file
def load_config(config_file="config.json"):
    """
    Load configuration settings from a JSON file.
    """
    try:
        with open(config_file, "r") as f:
            config = json.load(f)
        logger.info("Configuration loaded successfully.")
        return config
    except Exception as e:
        logger.error(f"Failed to load configuration: {e}")
        raise


# MongoDB setup function to initialize the connection
def get_mongo_client(mongo_config):
    """
    Connect to MongoDB and return the client.
    """
    try:
        client = MongoClient(mongo_config["uri"])
        db = client[mongo_config["database"]]
        logger.info(f"Connected to MongoDB database: {mongo_config['database']}")
        return db
    except Exception as e:
        logger.error(f"Error connecting to MongoDB: {e}")
        raise


# Consumer callback function for processing messages
def process_message(msg, db, topics_to_collection):
    """
    Process the message from Kafka and store it in the relevant MongoDB collection.
    """
    try:
        message_value = msg.value().decode("utf-8")  # Decode message
        logger.info(f"Received message from topic '{msg.topic()}': {message_value}")

        # Convert the message to a Python dictionary
        data = json.loads(message_value)
        logger.debug(f"Decoded message data: {data}")

        # Get the collection name from the topic using the mapping
        topic = msg.topic()
        collection_name = topics_to_collection.get(topic)

        if collection_name:
            collection = db[collection_name]

            # Insert the data into the relevant collection
            logger.info(f"Inserting data into MongoDB collection '{collection_name}'")
            collection.insert_one(data)
            logger.info(f"Inserted message into {collection_name}: {data}")
        else:
            logger.warning(f"Topic '{topic}' not mapped to a MongoDB collection.")

    except Exception as e:
        logger.error(f"Error processing message: {e}")


def create_consumer(kafka_config):
    """
    Create and configure the Kafka consumer.
    """
    try:
        consumer = Consumer(
            {
                "bootstrap.servers": kafka_config["bootstrap_servers"],
                "group.id": kafka_config["group_id"],
                "auto.offset.reset": kafka_config["auto_offset_reset"],
                "enable.auto.commit": kafka_config["enable_auto_commit"],  # Manually commit offsets
            }
        )
        logger.info("Kafka consumer initialized successfully.")
        return consumer
    except Exception as e:
        logger.error(f"Failed to initialize Kafka consumer: {e}")
        raise


# Main function to run the consumer
def main():
    try:
        # Load configuration
        config = load_config()

        # Initialize Kafka consumer
        consumer = create_consumer(config["kafka"])

        # Get MongoDB client
        db = get_mongo_client(config["mongodb"])

        # Get topics to collection mapping
        topics_to_collection = config["topics_to_collection"]

        # Subscribe to topics dynamically from the configuration
        topics = list(topics_to_collection.keys())
        consumer.subscribe(topics)  # Subscribe to all topics listed in config
        logger.info(f"Subscribed to topics: {', '.join(topics)}")

        # Check if no topics are configured
        if not topics:
            logger.warning("No Kafka topics are configured to be subscribed to. Please check the config.")

        # Loop to consume messages from Kafka
        while True:
            try:
                # Poll for a new message
                msg = consumer.poll(timeout=1.0)

                if msg is None:  # No message available within timeout
                    logger.debug("No message received in the current poll.")
                    continue
                if msg.error():  # Handle errors
                    if msg.error().code() == KafkaError._PARTITION_EOF:
                        logger.info(f"End of partition reached: {msg.partition}")
                    else:
                        logger.error(f"Kafka error: {msg.error()}")
                        raise KafkaException(msg.error())

                # Process the message
                process_message(msg, db, topics_to_collection)

                # Commit the offset after processing the message
                logger.debug(f"Committing offset for message from topic '{msg.topic()}'")
                consumer.commit(msg)

            except KeyboardInterrupt:
                logger.info("Shutting down consumer gracefully.")
                break
            except Exception as e:
                logger.error(f"Error consuming messages: {e}")

        # Close the consumer connection
        consumer.close()
        logger.info("Kafka consumer connection closed.")

    except Exception as e:
        logger.critical(f"Application failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
