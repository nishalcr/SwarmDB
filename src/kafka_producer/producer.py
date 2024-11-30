from kafka import KafkaProducer
import json
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import os
import time

CONFIG_PATH = "config.json"
producer = None
WATCHER_PATH = "" 

class AnyFileEventHandler(FileSystemEventHandler):

    def __init__(self, target_files, folder_path, callback):
        super().__init__()
        self.target_files = set(target_files)
        self.folder_path = folder_path
        self.callback = callback

    def on_created(self, event):
        file_name = os.path.basename(event.src_path)
        if file_name in self.target_files:
            print(f"File '{file_name}' has been created.")
            self.callback(file_name)

    def on_modified(self, event):
        file_name = os.path.basename(event.src_path)
        if file_name in self.target_files:
            print(f"File '{file_name}' has been modified.")
            self.callback(file_name)


def wait_for_any_file(folder_path, target_files, callback, timeout=None):

    event_handler = AnyFileEventHandler(target_files, folder_path, callback)
    observer = Observer()
    observer.schedule(event_handler, folder_path, recursive=False)

    try:
        observer.start()
        print(f"Waiting for any of the files: {', '.join(target_files)} in folder '{folder_path}'...")
        start_time = time.time()

        while True:
            time.sleep(1)
            if timeout and (time.time() - start_time) > timeout:
                print(f"Timeout reached while waiting for files: {', '.join(target_files)}.")
                break

    except KeyboardInterrupt:
        print("File watcher interrupted.")
    finally:
        observer.stop()
        observer.join()

def on_file_found(file_name):
    print(f"Callback triggered for file: {file_name}")
    base_name = os.path.splitext(file_name)[0]
    print(os.listdir(WATCHER_PATH))
    load_json(producer, base_name, file_name)
    producer.flush()
    print(f"Completed loadin file: {file_name}")


def read_config():
    with open(CONFIG_PATH) as config_file:
        config = json.load(config_file)
        KAFKA_BROKER = config["KAFKA_PRODUCER"]["KAFKA_HOST"]
        topics = config["KAFKA_PRODUCER"]["topic_list"]
        src_file_path = config["KAFKA_PRODUCER"]["src_file_path"]
        print("Config file read successfully")
    return KAFKA_BROKER, topics, src_file_path

def load_json(producer, topic_name, json_file):
    file_path = WATCHER_PATH + "/" + json_file
    print(file_path)
    with open(file_path, 'r') as file:
        data = json.load(file)
        for record in data:
            producer.send(topic_name, record)
            print(f"Produced record to topic '{topic_name}': {record}")


KAFKA_BROKER, TOPICS, WATCHER_PATH = read_config()

files_to_wait_for = []
for i in range(len(TOPICS)):
    files_to_wait_for.append(TOPICS[i]+".json")
print(files_to_wait_for)

print("files currently in path")
print(os.listdir(WATCHER_PATH))
wait_timeout = 60
producer = KafkaProducer(
    bootstrap_servers=KAFKA_BROKER,
    value_serializer=lambda v: json.dumps(v).encode('utf-8')
)

wait_for_any_file(WATCHER_PATH, files_to_wait_for, on_file_found, wait_timeout)
#producer.flush()
#print("Completed moving all records")