import streamlit as st
import paho.mqtt.client as mqtt
import threading
import time

# MQTT settings (Updated for your broker and topic)
MQTT_BROKER = "test.mosquitto.org"
MQTT_PORT = 1883
MQTT_TOPIC = "hackaton-test"

# Shared list to store MQTT messages
mqtt_messages = []

# Function to handle incoming MQTT messages
def on_message(client, userdata, message):
    msg = message.payload.decode("utf-8")
    mqtt_messages.append(f"Topic: {message.topic}, Message: {msg}")

# Function to connect to the MQTT broker
def mqtt_thread():
    client = mqtt.Client()
    client.on_message = on_message
    client.connect(MQTT_BROKER, MQTT_PORT, 60)
    client.subscribe(MQTT_TOPIC)
    client.loop_forever()

# Run the MQTT client in a separate thread
def start_mqtt_thread():
    thread = threading.Thread(target=mqtt_thread)
    thread.daemon = True
    thread.start()

# Streamlit application
def main():
    st.title("MQTT Message Viewer")

    # Start MQTT thread when app starts
    if 'mqtt_started' not in st.session_state:
        start_mqtt_thread()
        st.session_state['mqtt_started'] = True

    # Display MQTT messages
    placeholder = st.empty()
    while True:
        # Update the displayed messages every second
        with placeholder:
            st.write("### Received Messages")
            for msg in mqtt_messages:
                st.write(msg)
        time.sleep(1)

if __name__ == "__main__":
    main()
