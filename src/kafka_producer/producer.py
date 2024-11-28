from kafka import KafkaProducer
import json

KAFKA_BROKER = "localhost:9092"

def load_json(producer, topic_name, json_file):
    with open(json_file, 'r') as file:
        data = json.load(file)
        for record in data:
            producer.send(topic_name, record)
            print(f"Produced record to topic '{topic_name}': {record}")

producer = KafkaProducer(
    bootstrap_servers=KAFKA_BROKER,
    value_serializer=lambda v: json.dumps(v).encode('utf-8')  # Serialize data as JSON
)

topics = [
    'Devices_Dim',
    'logs_collections',
    'Maint_Device_Data',
    'Motion_Detect_Data',
    'Temp_Hum_Sensor_Data'
]
TOPIC_NAME = 'Temp_Hum_Sensor_Data'
JSON_FILE = "../../test/data/Temp_Hum_Sensor_Data.json"
load_json(producer, TOPIC_NAME, JSON_FILE)
producer.flush()
print("Completed moving all records")