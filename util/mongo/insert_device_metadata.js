const db = connect("mongodb://localhost:27017/iot_device_data");  // Change if needed

db.device_metadata.insertMany([
{"device_id":"motion_01","location":{"lat":37.7749,"lon":-122.4194},"metadata":{"model":"MotionSense V2","type":"motion_detector"}},
{"device_id":"motion_02","location":{"lat":34.0522,"lon":-118.2437},"metadata":{"model":"MotionTracker Pro","type":"motion_detector"}},
{"device_id":"motion_03","location":{"lat":40.7128,"lon":-74.0060},"metadata":{"model":"SecureMove X","type":"motion_detector"}},
{"device_id":"motion_04","location":{"lat":51.5074,"lon":-0.1278},"metadata":{"model":"DetectoMax","type":"motion_detector"}},
{"device_id":"motion_05","location":{"lat":-23.5505,"lon":-46.6333},"metadata":{"model":"MotionSense V2","type":"motion_detector"}},
{"device_id":"motion_06","location":{"lat":-33.8688,"lon":151.2093},"metadata":{"model":"MotionTracker Pro","type":"motion_detector"}},
{"device_id":"motion_07","location":{"lat":35.6895,"lon":139.6917},"metadata":{"model":"MotionSense V2","type":"motion_detector"}},
{"device_id":"motion_08","location":{"lat":48.8566,"lon":2.3522},"metadata":{"model":"SecureMove X","type":"motion_detector"}},
{"device_id":"motion_09","location":{"lat":55.7558,"lon":37.6173},"metadata":{"model":"DetectoMax","type":"motion_detector"}},
{"device_id":"sensor_01","location":{"lat":40.7128,"lon":-74.0060},"metadata":{"model":"EnviroSense 2000","type":"temperature_humidity_sensor"}},
{"device_id":"sensor_02","location":{"lat":37.7749,"lon":-122.4194},"metadata":{"model":"ThermoTrack Pro","type":"temperature_humidity_sensor"}},
{"device_id":"sensor_03","location":{"lat":34.0522,"lon":-118.2437},"metadata":{"model":"HumidiPro X","type":"humidity_sensor"}},
{"device_id":"sensor_04","location":{"lat":-33.8688,"lon":151.2093},"metadata":{"model":"EnviroSense 2000","type":"temperature_humidity_sensor"}},
{"device_id":"sensor_05","location":{"lat":-23.5505,"lon":-46.6333},"metadata":{"model":"ThermoTrack Pro","type":"temperature_humidity_sensor"}},
{"device_id":"sensor_06","location":{"lat":48.8566,"lon":2.3522},"metadata":{"model":"HumidiPro X","type":"humidity_sensor"}},
{"device_id":"sensor_07","location":{"lat":35.6895,"lon":139.6917},"metadata":{"model":"EnviroSense 2000","type":"temperature_humidity_sensor"}},
{"device_id":"sensor_08","location":{"lat":55.7558,"lon":37.6173},"metadata":{"model":"ThermoTrack Pro","type":"temperature_humidity_sensor"}},
{"device_id":"sensor_09","location":{"lat":19.0760,"lon":72.8777},"metadata":{"model":"HumidiPro X","type":"humidity_sensor"}},
]);


print("Records inserted successfully!");