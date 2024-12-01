import os
import time
import ndjson
import json
from confluent_kafka import Producer
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler


# Load configuration from the config.json file
def load_config(config_file="config.json"):
    with open(config_file, "r") as file:
        return json.load(file)


print("Producer is running")
print("Loading configuration...")
config = load_config()
print("Configuration loaded successfully")
print("Config: ", config)

KAFKA_SERVER = config["kafka_server"]  # Kafka external IP and port
WATCH_FOLDER = config["watch_folder"]

# Kafka Producer Configuration
producer_config = config["producer_config"]
producer = Producer(producer_config)

# Topic prefixes based on the file name
TOPIC_PREFIXES = config["topic_prefixes"]


# Function to send messages to Kafka
def send_to_kafka(file_path, topic):
    print(f"Sending data to Kafka from {file_path} to topic {topic}")
    with open(file_path, "r") as f:
        try:
            # Read and parse the NDJSON file
            data = ndjson.load(f)
            print(f"Read {len(data)} records from {file_path}")
            for record in data:
                # Send each record to the appropriate Kafka topic
                producer.produce(topic, key=None, value=str(record).encode("utf-8"))
                print(f"Sent record to {topic}: {record}")

            # Wait for any outstanding messages to be delivered
            producer.flush()
        except Exception as e:
            print(f"Error reading or sending data from {file_path}: {e}")


# Custom event handler class to handle new file creation
class NewFileHandler(FileSystemEventHandler):
    def on_created(self, event):
        print(f"New file created: {event.src_path}")
        # Only handle new files, not directories
        if event.is_directory:
            return

        # Check if the file is an NDJSON file
        if event.src_path.endswith(".ndjson"):
            filename = os.path.basename(event.src_path)

            print(f"Processing file: {filename}")
            # Determine which topic to use based on the file name
            topic = None
            for prefix, topic_name in TOPIC_PREFIXES.items():
                if filename.startswith(prefix):
                    topic = topic_name
                    break
            print(f"Topic: {topic}")
            if topic is None:
                print(f"Unrecognized file prefix: {filename}")
                return
            # Send the contents of the file to Kafka
            send_to_kafka(event.src_path, topic)
        else:
            print(f"Unrecognized file extension. Only .ndjson files are supported.")


# Initialize and start the observer to watch for new files
def start_watching():
    event_handler = NewFileHandler()
    observer = Observer()
    observer.schedule(event_handler, WATCH_FOLDER, recursive=False)
    observer.start()

    print(f"Watching for new NDJSON files in {WATCH_FOLDER}...")
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()


if __name__ == "__main__":
    start_watching()
