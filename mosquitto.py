import paho.mqtt.client as mqtt

# MQTT broker details
broker = "test.mosquitto.org"
port = 1883
topic = "hackaton-test"

# Callback function for when a message is received
def on_message(client, userdata, msg):
    print(f"Received message: '{msg.payload.decode()}' on topic '{msg.topic}'")

# Callback function for when the client connects to the broker
def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("Connected to MQTT broker successfully!")
        # Subscribe to the topic after connecting
        client.subscribe(topic)
        print(f"Subscribed to topic '{topic}'")
    else:
        print(f"Connection failed with code {rc}")

# Create a new MQTT client instance
client = mqtt.Client()

# Attach the callbacks
client.on_connect = on_connect
client.on_message = on_message

# Connect to the broker
client.connect(broker, port, 60)

# Start the MQTT client loop to listen for incoming messages
client.loop_start()

try:
    while True:
        # Keep the script running to receive messages and also publish
        message = input("Enter message to publish (or 'exit' to quit): ")
        if message.lower() == 'exit':
            break
        # Publish the message to the topic
        client.publish(topic, message)
        print(f"Message '{message}' sent to topic '{topic}'")
except KeyboardInterrupt:
    print("Exiting...")
finally:
    # Stop the loop and disconnect from the broker
    client.loop_stop()
    client.disconnect()
    print("Disconnected from MQTT broker")