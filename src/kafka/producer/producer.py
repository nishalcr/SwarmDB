import os
import time
import ndjson
import json
from confluent_kafka import Producer
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import logging

log_level = os.environ.get("LOG_LEVEL", "WARNING").upper()
log_levels = {"DEBUG": logging.DEBUG, "INFO": logging.INFO, "WARNING": logging.WARNING, "ERROR": logging.ERROR, "CRITICAL": logging.CRITICAL}
logging.basicConfig(
    format="%(asctime)s - %(levelname)s - %(message)s", level=log_levels.get(log_level, logging.INFO)
)  # Default to INFO if invalid level
logger = logging.getLogger(__name__)


# Load configuration from the config.json file
def load_config(config_file="config.json"):
    with open(config_file, "r") as file:
        return json.load(file)


logger.info("Starting Kafka producer script")
logger.info("Loading configuration from config.json...")
config = load_config()
logger.info("Configuration loaded successfully")
logger.debug(f"Loaded configuration: {config}")

KAFKA_SERVER = config["kafka_server"]  # Kafka external IP and port
WATCH_FOLDER = config["watch_folder"]

# Kafka Producer Configuration
producer_config = config["producer_config"]
producer = Producer(producer_config)

# Topic prefixes based on the file name
TOPIC_PREFIXES = config["topic_prefixes"]


# Function to send messages to Kafka with proper JSON format
def send_to_kafka(file_path, topic):
    logger.info(f"Preparing to send data from {file_path} to Kafka topic '{topic}'")
    with open(file_path, "r") as f:
        try:
            # Read and parse the NDJSON file
            data = ndjson.load(f)
            logger.info(f"Successfully read {len(data)} records from {file_path}")
            for record in data:
                try:
                    # Convert the record to a JSON string
                    json_record = json.dumps(record)

                    # Send the record to Kafka (ensure it's UTF-8 encoded)
                    producer.produce(topic, key=None, value=json_record.encode("utf-8"))
                    logger.debug(f"Sent record to topic '{topic}': {json_record}")

                except Exception as e:
                    logger.error(f"Error sending record to Kafka topic '{topic}': {e}")

            # Wait for any outstanding messages to be delivered
            producer.flush()
            logger.info(f"All records from {file_path} have been sent to Kafka topic '{topic}'")

        except Exception as e:
            logger.error(f"Error reading or sending data from {file_path}: {e}")


# Custom event handler class to handle new file creation
class NewFileHandler(FileSystemEventHandler):
    def on_created(self, event):
        logger.info(f"New file detected: {event.src_path}")
        # Only handle new files, not directories
        if event.is_directory:
            logger.debug(f"Ignoring directory creation event: {event.src_path}")
            return

        # Check if the file is an NDJSON file
        if event.src_path.endswith(".ndjson"):
            filename = os.path.basename(event.src_path)

            logger.info(f"Processing new NDJSON file: {filename}")
            # Determine which topic to use based on the file name
            topic = None
            for prefix, topic_name in TOPIC_PREFIXES.items():
                if filename.startswith(prefix):
                    topic = topic_name
                    break
            logger.debug(f"Determined Kafka topic for file '{filename}': {topic}")
            if topic is None:
                logger.warning(f"Unrecognized file prefix for file '{filename}'. No matching Kafka topic found.")
                return
            # Send the contents of the file to Kafka
            send_to_kafka(event.src_path, topic)
        else:
            logger.warning(f"Unsupported file extension for file '{event.src_path}'. Only .ndjson files are supported.")


# Initialize and start the observer to watch for new files
def start_watching():
    event_handler = NewFileHandler()
    observer = Observer()
    observer.schedule(event_handler, WATCH_FOLDER, recursive=False)
    observer.start()

    logger.info(f"Started watching for new NDJSON files in directory: {WATCH_FOLDER}")
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        logger.info("Stopping file watcher due to keyboard interrupt")
        observer.stop()
    observer.join()
    logger.info("File watcher stopped")


if __name__ == "__main__":
    start_watching()
