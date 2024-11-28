from kafka.admin import KafkaAdminClient, NewTopic
from kafka import errors

KAFKA_BROKER = "localhost:9092"
topics = [
    'Devices_Dim',
    'logs_collections',
    'Maint_Device_Data',
    'Motion_Detect_Data',
    'Temp_Hum_Sensor_Data'
]
topic_list = []


#Function to create topic
def create_topic(admin_client, topics):
    for topic_name in topics:
        topic_list.append(NewTopic(topic_name, num_partitions=1, replication_factor=1))
        print("****Topic: " + topic_name)
    try:
        admin_client.create_topics(new_topics=topic_list, validate_only=False)
    except errors.TopicAlreadyExistsError:
        print("*Topics exist already*")
    print("Topics list completed")
    



admin_client = KafkaAdminClient(
    bootstrap_servers = KAFKA_BROKER, 
    client_id='test'
)
create_topic(admin_client, topics)
    

print("New topic list:")
print(str(admin_client.list_topics()))