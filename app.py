from dotenv import load_dotenv
import json
import os
import paho.mqtt.client as mqtt
import requests
import streamlit as st
import queue
import threading

### MQTT Configuration ###
BROKER = "test.mosquitto.org"
PORT = 1883
TOPIC = "hackaton-test"
CLIENT_ID = f'streamlit_client_{os.getpid()}'

# Function to initialize MQTT client and start the loop
def init_mqtt(q):
    # Initialize MQTT client with unique client ID and MQTTv5 protocol
    client = mqtt.Client(client_id=CLIENT_ID, protocol=mqtt.MQTTv5)

    # Callback function for when the client connects to the broker
    def on_connect(client, userdata, flags, reasonCode, properties=None):
        if reasonCode == 0:
            print("Connected to MQTT broker successfully!")
            client.subscribe(TOPIC)
            print(f"Subscribed to topic '{TOPIC}'")
        else:
            print(f"Connection failed with reason code {reasonCode}")

    # Callback function for when a message is received
    def on_message(client, userdata, msg):
        try:
            message = msg.payload.decode()
            print(f"Received message: {message}")
            message_dict = json.loads(message)
            q.put(message_dict)
        except Exception as e:
            print(f"Error processing message: {e}")

    # Attach the callbacks
    client.on_connect = on_connect
    client.on_message = on_message

    # Connect to the broker with MQTTv5 properties
    connect_properties = mqtt.Properties(mqtt.PacketTypes.CONNECT)
    # Example: Set session expiry interval to 1 hour (3600 seconds)
    connect_properties.SessionExpiryInterval = 3600

    client.connect(BROKER, PORT, keepalive=60, properties=connect_properties)
    client.loop_start()
    return client

### GPT API Code ###
# Load environment variables
load_dotenv()

# Retrieve API key and URL from environment
GPT_API_KEY = os.getenv("API_KEY")
GPT_API_URL = os.getenv("API_URL")

def call_api(data):
    data["model"] = "gpt-4-turbo-2024-04-09"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {GPT_API_KEY}"
    }
    try:
        response = requests.post(GPT_API_URL, headers=headers, json=data)
        print(f"GPT API response status: {response.status_code}")
        return response
    except requests.exceptions.ConnectionError as e:
        print(f"Connection error: {e}")
        return None

def ask_gpt(question, messages):
    print(f"Sending question: '{question}' to GPT API")
    print(f"Current messages: {messages}")

    system_instructions = (
        "You are an expert at Yara International ASA, specializing in production management. "
        "Acting as the global planning hub, you oversee and control all aspects of production. "
        "You can make up numbers for real-time values and other values that you might not have. "
        "Users can request you to plan or halt production, provide status reports, and more. "
        "You generate realistic data and scenarios, always aiming for accuracy. "
        "You operate within a sophisticated backend system that allows for API calls "
        "to adjust production settings and access historical data. "
        "You represent a cutting-edge, digital version of Yara, "
        "and users will look to you for inspiration on how to digitize and modernize Yara’s operations."
    )

    data = {
        "messages": [
            {
                "role": "system",
                "content": system_instructions
            }
        ]
    }
    data["messages"].extend(messages)

    new_message = {"role": "user", "content": question}
    data["messages"].append(new_message)

    # Publish user message to the MQTT topic
    print(f"Publishing user message: '{new_message}' to topic '{TOPIC}'")
    try:
        encoded_message = json.dumps(new_message)
        mqtt_client.publish(TOPIC, encoded_message)
    except Exception as e:
        print(f"Failed to publish user message: {e}")
        return False, None

    print(f"Data sent to GPT API: {data}")
    response = call_api(data)

    # Error handling, no response if response is None or status is not 200
    if response is None or response.status_code != 200:
        print("GPT API call failed.")
        return False, response

    response_body = response.json()
    print(f"GPT API response: {response_body}")

    # Extract assistant's message
    try:
        assistant_content = response_body["choices"][0]["message"]["content"]
        assistant_message = {
            "role": "assistant",
            "content": assistant_content
        }
    except (KeyError, IndexError) as e:
        print(f"Error extracting assistant message: {e}")
        return False, response

    # Publish the GPT response to the MQTT topic
    print(f"Publishing assistant message: '{assistant_message}' to topic '{TOPIC}'")
    try:
        encoded_message = json.dumps(assistant_message)
        mqtt_client.publish(TOPIC, encoded_message)
    except Exception as e:
        print(f"Failed to publish assistant message: {e}")
        return False, response

    return True, response

### Streamlit UI ###
st.set_page_config(page_title="Chat with Global Production Planning Manager", layout="wide")

st.title("Chat with Global Production Planning Manager")

# Initialize session state for messages and queue
if "messages" not in st.session_state:
    st.session_state["messages"] = []

if "queue" not in st.session_state:
    st.session_state["queue"] = queue.Queue()

if "mqtt_client" not in st.session_state:
    st.session_state["mqtt_client"] = init_mqtt(st.session_state["queue"])

mqtt_client = st.session_state["mqtt_client"]
q = st.session_state["queue"]

# Function to process incoming messages from the queue
def process_queue():
    while not q.empty():
        message = q.get()
        print(f"Processing message from queue: {message}")
        # Avoid duplicating user messages since they are already appended
        if message not in st.session_state["messages"]:
            st.session_state["messages"].append(message)
            print(f"Appended message to session_state: {message}")

# Text input within a form to handle submission and reset input box
with st.form(key='input_form', clear_on_submit=True):
    user_input = st.text_input("Ask a question:", key='input_box')
    submit_button = st.form_submit_button(label='Send')

# Handle user input
if submit_button and user_input:
    print(f"User input submitted: '{user_input}'")
    is_success, response = ask_gpt(user_input, st.session_state["messages"])
    if not is_success:
        st.error("Failed to get response from GPT API.")

# Clear chat messages
if st.button("Clear Chat"):
    st.session_state["messages"] = []
    st.experimental_rerun()

# Process any messages in the queue
process_queue()

# Display all messages
print(f"Displaying messages: {st.session_state['messages']}")
for message in st.session_state["messages"]:
    if message["role"] == "user":
        st.markdown(f"**User**: {message['content']}")
    elif message["role"] == "assistant":
        st.markdown(f"**Yara**: {message['content']}")
