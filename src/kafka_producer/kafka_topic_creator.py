from kafka.admin import KafkaAdminClient, NewTopic
from kafka import errors
import json


CONFIG_PATH = "config.json"
topic_list = []

def read_config():
    with open(CONFIG_PATH) as config_file:
        config = json.load(config_file)
        KAFKA_BROKER = config["KAFKA_PRODUCER"]["KAFKA_HOST"]
        topics = config["KAFKA_PRODUCER"]["topic_list"]
        print("Config file read successfully")
    return KAFKA_BROKER, topics

#Function to create topic
def create_topic(admin_client, topics):
    print("in create_TOPIC")
    print(topics)
    for topic_name in topics:
        print(topic_name)
        topic_list.append(NewTopic(topic_name, num_partitions=1, replication_factor=1))
        print("****Topic: " + topic_name)
    try:
        admin_client.create_topics(topic_list)
    except errors.TopicAlreadyExistsError:
        print("*Topics exist already*")
    print("Topics list completed")

KAFKA_BROKER, TOPICS = read_config()
admin_client = KafkaAdminClient(
    bootstrap_servers = KAFKA_BROKER, 
    client_id='test'
)
create_topic(admin_client, TOPICS)
    

print("New topic list:")
print(str(admin_client.list_topics()))