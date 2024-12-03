# SwarmDB

**SwarmDB** is a Swarm Intelligence-Based Distributed Database System designed to efficiently manage large-scale IoT data with optimized partitioning, replication, and query processing. The system uses swarm algorithms and a distributed database architecture (including MongoDB Sharding) to handle dynamic workloads, data storage, and real-time data queries.

---

## Table of Contents

1. [Project Overview](#project-overview)
2. [MongoDB Collection Schemas](#mongodb-collection-schemas)
    - [device_metadata Collection Schema](#1-devicemetadata-collection-schema)
    - [sensor_data Collection Schema](#2-sensordata-collection-schema)
    - [sensor_maintenance_data Collection Schema](#3-sensormaintenance-data-collection-schema)
    - [sensor_monitoring_logs Collection Schema](#4-sensormonitoring-logs-collection-schema)
3. [Tools and Technologies](#tools-and-technologies)
4. [Deployment Steps](#deployment-steps)
    - [Clone the Repository](#1-clone-the-repository)
    - [Set Up EC2 Instances](#2-set-up-ec2-instances)
    - [Deploy Kafka and Zookeeper](#3-deploy-kafka-and-zookeeper-on-docker-swarm)
    - [Deploy MongoDB Sharded Cluster](#4-deploy-mongodb-sharded-cluster-on-docker-swarm)
    - [MongoDB Sharding Setup](#5-mongodb-sharding-setup)
    - [Start the Swarm Agents](#6-start-the-swarm-agents)
    - [Deploy Prometheus and Grafana](#7-deploy-prometheus-and-grafana-on-docker-swarm)
    - [Scaling Services in Docker Swarm](#8-scaling-services-in-docker-swarm)
5. [Next Steps After Basic Setup](#next-steps-after-basic-setup)

---

## Project Overview

SwarmDB combines **swarm intelligence** with distributed database principles to provide an adaptive, scalable solution for managing IoT data. The system handles:

- **Kafka** for streaming data
- **MongoDB** as the sharded data storage solution
- **Prometheus & Grafana** for monitoring and visualization
- **Swarm Agents** for intelligent dynamic decision-making (based on ACO/PSO algorithms)

---

## MongoDB Collection Schemas

SwarmDB uses several MongoDB collections to store metadata, sensor data, maintenance records, and logs.

### 1. **device_metadata Collection Schema**

Stores metadata for IoT devices, including device IDs, location, and device type.

```json
{
  "_id": ObjectId,
  "device_id": { 
     "type": String, 
     "description": "Unique identifier for the device" 
  },
  "location": {
     "lat": { 
        "type": Number, 
        "description": "Latitude of the device location" 
     },
     "lon": { 
        "type": Number, 
        "description": "Longitude of the device location" 
     }
  },
  "metadata": {
     "model": { 
        "type": String, 
        "description": "Model name of the device" 
     },
     "type": { 
        "type": String, 
        "description": "Type of device (e.g., motion detector)" 
     }
  },
  "created_at": { 
     "type": Date, 
     "description": "Timestamp when the metadata was recorded" 
  }
}
```

### 2. **sensor_data Collection Schema**

Stores IoT sensor readings, such as temperature, humidity, and battery levels.

```json
{
  "_id": ObjectId,
  "device_id": { 
     "type": String, 
     "description": "Device identifier to associate sensor data" 
  },
  "timestamp": { 
     "type": Date, 
     "description": "Timestamp when the sensor data was recorded" 
  },
  "temperature": { 
     "type": Number, 
     "nullable": true, 
     "description": "Temperature reading (nullable if not available)" 
  },
  "humidity": { 
     "type": Number, 
     "nullable": true, 
     "description": "Humidity reading (nullable if not available)" 
  },
  "motion_detected": { 
     "type": Boolean, 
     "description": "Indicates if motion was detected" 
  },
  "battery_level": { 
     "type": Number, 
     "description": "Battery level percentage of the device" 
  },
  "status": { 
     "type": String, 
     "description": "Current status of the device (e.g., 'active', 'inactive')" 
  },
  "created_at": { 
     "type": Date, 
     "description": "Timestamp when the sensor data was recorded" 
  }
}
```

### 3. **sensor_maintenance_data Collection Schema**

Tracks sensor maintenance activities, such as battery levels and device status.

```json
{
  "_id": ObjectId,
  "device_id": { 
     "type": String, 
     "description": "Device identifier for the sensor requiring maintenance" 
  },
  "timestamp": { 
     "type": Date, 
     "description": "Timestamp when the maintenance data was recorded" 
  },
  "battery_level": { 
     "type": Number, 
     "description": "Battery level percentage of the sensor device" 
  },
  "status": { 
     "type": String, 
     "description": "Current status of the device (e.g., 'active', 'inactive')" 
  },
  "created_at": { 
     "type": Date, 
     "description": "Timestamp when the maintenance data was recorded" 
  }
}
```

### 4. **sensor_monitoring_logs Collection Schema**

Tracks logs related to sensor activities, such as device status and error messages.

```json
{
  "_id": ObjectId,
  "log_id": { 
     "type": Number, 
     "description": "Unique identifier for the log entry" 
  },
  "device_id": { 
     "type": String, 
     "description": "Device identifier associated with the log" 
  },
  "timestamp": { 
     "type": Date, 
     "description": "Timestamp when the log entry was recorded" 
  },
  "log_level": { 
     "type": String, 
     "enum": ["INFO", "WARN", "ERROR"], 
     "description": "Severity level of the log entry" 
  },
  "message": { 
     "type": String, 
     "description": "Log message containing details about the event" 
  },
  "status": { 
     "type": String, 
     "description": "Current status of the device (e.g., 'maintenance', 'active')" 
  },
  "created_at": { 
     "type": Date, 
     "description": "Timestamp when the log entry was created" 
  }
}
```

---

## Tools and Technologies

- **Docker** / **Docker Compose** for containerization
- **Prometheus** / **Grafana** for monitoring and visualization
- **Apache Kafka** for streaming IoT data
- **MongoDB** for distributed data storage
- **Swarm Agents** for intelligent dynamic decision-making
- **ACO/PSO** optimization algorithms

---

## Deployment Steps

### 1. Clone the Repository

Clone the SwarmDB repository from GitHub:

```bash
git clone https://github.com/yourusername/SwarmDB.git
cd SwarmDB
```

### 2. Set Up EC2 Instances

- Launch at least 3 EC2 instances and install Docker on each.
- Initialize Docker Swarm on the manager node and join worker nodes to the cluster.

### 3. Deploy Kafka and Zookeeper on Docker Swarm

- Create a `docker-compose.yml` file to define Kafka and Zookeeper services.
- Deploy Kafka and Zookeeper using `docker stack deploy`.

### 4. Deploy MongoDB Sharded Cluster on Docker Swarm

- Define services for Config Server, Shards, and Mongos Router in a `docker-compose.yml` file.
- Deploy the MongoDB stack and initialize replica sets for sharding.

### 5. **MongoDB Sharding Setup**

Follow these steps to configure MongoDB sharding on your sharded cluster:

#### 5.1 Initiate the Config Server Replica Set

Run the following commands on one of your MongoDB config server containers (e.g., `mongo_config_server_1`):

```javascript
rs.initiate({
  _id: "cfg",
  configsvr: true,
  members: [
     { _id: 0, host: "mongo_config_server_1:27017" },
     { _id: 1, host: "mongo_config_server_2:27017" },
     { _id: 2, host: "mongo_config_server_3:27017" }
  ]
})
```

Verify the replica set status:

```javascript
rs.status()
```

#### 5.2 Initiate Shard 1 Replica Set

Run the following commands on one of your MongoDB shard containers (e.g., `mongo_shard_1_rep_1`):

```javascript
rs.initiate({
  _id: "shard1",
  members: [
     { _id: 0, host: "mongo_shard_1_rep_1:27017" },
     { _id: 1, host: "mongo_shard_1_rep_2:27017" },
     { _id: 2, host: "mongo_shard_1_rep_3:27017" }
  ]
})
```

Verify the replica set status:

```javascript
rs.status()
```

#### 5.3 Initiate Shard 2 Replica Set

Run the following commands on one of your MongoDB shard containers (e.g., `mongo_shard_2_rep_1`):

```javascript
rs.initiate({
  _id: "shard2",
  members: [
     { _id: 0, host: "mongo_shard_2_rep_1:27017" },
     { _id: 1, host: "mongo_shard_2_rep_2:27017" },
     { _id: 2, host: "mongo_shard_2_rep_3:27017" }
  ]
})
```

Verify the replica set status:

```javascript
rs.status()
```

#### 5.4 Add Shards to the Cluster

After initiating the replica sets, add the shards to the sharded cluster from the **mongos router**:

```javascript
sh.addShard("shard1/mongo_shard_1_rep_1:27017")
sh.addShard("shard2/mongo_shard_2_rep_2:27017")
```

Check the status of the shards:

```javascript
sh.status()
```

#### 5.5 Enable Sharding on the Database

Switch to the database you want to shard (e.g., `iot_device_data`):

```javascript
use iot_device_data
sh.enableSharding("iot_device_data")
```

#### 5.6 Shard Collections

Create and shard collections by `device_id`:

```javascript
db.createCollection("sensor_data")
db.createCollection("sensor_maintenance_data")
db.createCollection("sensor_monitoring_logs")

// Shard collections by device_id
sh.shardCollection("iot_device_data.sensor_data", { "device_id": 1 });
sh.shardCollection("iot_device_data.sensor_maintenance_data", { "device_id": 1 });
sh.shardCollection("iot_device_data.sensor_monitoring_logs", { "device_id": 1 });
```

#### 5.7 Insert Sample Data

Insert sample data into the sharded collections:

```javascript
db.sensor_data.insert({ device_id: "sensor_01", temperature: 22.5, battery_level: 90 });
db.sensor_maintenance_data.insert({ device_id: "sensor_01", status: "active" });
db.sensor_monitoring_logs.insert({ device_id: "sensor_01", log_level: "INFO", message: "Sensor active." });
```

#### 5.8 Monitor Shard Distribution

Monitor data distribution across shards:

```javascript
db.sensor_data.getShardDistribution()
```

---

### 6. **Start the Swarm Agents**

Before deploying Prometheus, start the Swarm Agents with the following command:

```bash
docker-compose -f src/swarm_agent/docker-compose.yml up -d
```

---

### 7. Deploy Prometheus and Grafana on Docker Swarm

- Define Prometheus and Grafana services in a `docker-compose.yml` file.
- Configure Prometheus to scrape metrics from Kafka and MongoDB.
- Deploy the monitoring stack and access Grafana at `http://<EC2_PUBLIC_IP>:3000`.

### 8. **Scaling Services in Docker Swarm**

- Use `docker service scale` to adjust the number of replicas for services as needed.

This README provides a comprehensive guide for deploying and managing SwarmDB on AWS EC2 instances using Docker Swarm, MongoDB Sharding, and monitoring tools. Let me know if you need further assistance!

---
