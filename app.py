from dotenv import load_dotenv
import json
import os
import paho.mqtt.client as mqtt
import requests
import streamlit as st

### MQTT Configuration ###
broker = "test.mosquitto.org"
port = 1883
topic = "hackaton-test"

# Create a new MQTT client instance
client = mqtt.Client()

# Callback function for when the client connects to the broker
def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("Connected to MQTT broker successfully!")
        client.subscribe(topic)
    else:
        print(f"Connection failed with code {rc}")

# Callback function for when a message is received
def on_message(client, userdata, msg):
    print(f"Received message: '{msg.payload.decode()}' on topic '{msg.topic}'")
    message = msg.payload.decode()
    print(f"Message in on_message: {message}")
    print("type of message: ", type(message))

    message_dict = json.loads(message)
    print(f"Message in on_message after json.loads: {message_dict}")
    print("type of message: ", type(message_dict))
    
    # Save the message history
    if "messages" not in st.session_state:
        st.session_state["messages"] = []
    st.session_state["messages"].append(message_dict)

    # Display the message in the Streamlit app
    if message_dict["role"] == "user":
        st.write(f"**User**: {message_dict['content']}")
    elif message_dict["role"] == "assistant":
        st.write(f"**Yara**: {message_dict['content']}")


# Attach the callbacks
client.on_connect = on_connect
client.on_message = on_message

# Connect to the broker and start the loop
client.connect(broker, port, 60)
client.loop_start()

### GPT API Code ###
# Load environment variables
load_dotenv()

# Retrieve API key and URL from environment
gpt_api_key = os.getenv("API_KEY")
gpt_api_url = os.getenv("API_URL")

def call_api(data):
    data["model"] = "gpt-4-turbo-2024-04-09"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {gpt_api_key}"
    }
    try:
        response = requests.post(gpt_api_url, headers=headers, json=data)
        return response
    except requests.exceptions.ConnectionError as e:
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
    data["messages"].append(messages)

    new_message = {"role": "user", "content": question}
    data["messages"].append(new_message)

    # Publish user message to the MQTT topic
    print(f"Publishing message: '{new_message}' to topic '{topic}'")
    encoded_message = json.dumps(new_message)
    client.publish(topic, encoded_message)
    

    print(f"Data: {data}")
    response = call_api(data)

    # Error handling, no response if response is None or status is not 200
    if response is None or response.status_code != 200:
        return False, response

    response_body = response.json()

    # Append assistant answer to data
    new_message = {
        "role": "assistant",
        "content": response_body["choices"][0]["message"]["content"]
    }

    # Publish the GPT response to the MQTT topic
    encoded_message = json.dumps(new_message)
    client.publish(topic, encoded_message)

    return True, response

### Streamlit UI ###
st.title(f"Chat with Global Production Planning Manager")

# Textbox for user input
user_input = st.text_input("Ask a question:")

# History of all API interactions
if "messages" not in st.session_state:
    st.session_state["messages"] = []

# Handle user input
if st.button("Send"):
    if user_input:
        print(f"User input: '{user_input}'")
        print(f"Current messages: {st.session_state['messages']}")
        is_success, response = ask_gpt(user_input, st.session_state["messages"])

# Clear chat messages
if st.button("Clear Chat"):
    st.session_state["messages"] = []
    st.rerun()
