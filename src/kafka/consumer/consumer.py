import json
import logging
from confluent_kafka import Consumer, KafkaException, KafkaError
import sys

# Configure logging for the application
logging.basicConfig(
    format="%(asctime)s - %(levelname)s - %(message)s", level=logging.INFO
)
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


# Consumer callback function for processing messages
def process_message(msg):
    """
    Process the message from Kafka.
    """
    try:
        message_value = msg.value().decode("utf-8")  # Decode message
        data = json.loads(message_value)
        logger.info(f"Processed message: {data}")

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
                "enable.auto.commit": kafka_config[
                    "enable_auto_commit"
                ],  # Manually commit offsets
            }
        )
        logger.info("Kafka consumer initialized.")
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

        # Subscribe to topics dynamically from the configuration
        topics = config["topics"]
        consumer.subscribe(
            list(topics.values())
        )  # Subscribe to all topics listed in config

        logger.info(f"Subscribed to topics: {', '.join(topics.values())}")

        # Loop to consume messages from Kafka
        while True:
            try:
                # Poll for a new message
                msg = consumer.poll(timeout=1.0)

                if msg is None:  # No message available within timeout
                    continue
                if msg.error():  # Handle errors
                    if msg.error().code() == KafkaError._PARTITION_EOF:
                        logger.info(f"End of partition reached: {msg.partition}")
                    else:
                        raise KafkaException(msg.error())

                # Process the message
                process_message(msg)

                # Commit the offset after processing the message
                consumer.commit(msg)

            except KeyboardInterrupt:
                logger.info("Shutting down consumer.")
                break
            except Exception as e:
                logger.error(f"Error consuming messages: {e}")

        # Close the consumer connection
        consumer.close()

    except Exception as e:
        logger.critical(f"Application failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
