import streamlit as st
import requests
from dotenv import load_dotenv
import os
import paho.mqtt.client as mqtt

### MQTT Configuration ###
broker = "test.mosquitto.org"
port = 1883
topic = "hackaton-test"

# Create a new MQTT client instance
client = mqtt.Client()

# Connect to the broker
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

def ask_gpt(question, data={}):
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

    if len(data) == 0:
        data = {
            "messages": [
                {"role": "system", "content": system_instructions},
                {"role": "user", "content": f"{question}"}
            ]
        }
    else:
        new_message = {"role": "user", "content": question}
        data["messages"].append(new_message)

    # Publish the user question to the MQTT topic before calling the GPT API
    client.publish(topic, f"User: {question}")
    print(f"Published to MQTT topic '{topic}': User: {question}")

    response = call_api(data)

    # Error handling, no response if response is None or status is not 200
    if response is None or response.status_code != 200:
        return False, "", data, response

    response_body = response.json()

    # Append assistant answer to data
    new_message = {
        "role": "assistant",
        "content": response_body["choices"][0]["message"]["content"]
    }
    data["messages"].append(new_message)
    answer = new_message["content"]

    # Publish the GPT response to the MQTT topic after receiving the answer
    client.publish(topic, f"Yara: {answer}")
    print(f"Published to MQTT topic '{topic}': Yara: {answer}")

    return True, answer, data, response

### Streamlit UI ###
st.title(f"Chat with Global Production Planning Manager")

# Textbox for user input
user_input = st.text_input("Ask a question:")

# History of all API interactions
if "history" not in st.session_state:
    st.session_state["history"] = {}

# Handle user input
if st.button("Send"):
    if user_input:
        is_success, answer, data, response = ask_gpt(user_input, data=st.session_state["history"])

        if is_success:
            st.session_state["history"] = data

            # Display conversation in Streamlit
            for message in reversed(data["messages"]):
                if message["role"] == "user":
                    st.write(f"**You**: {message['content']}")
                elif message["role"] == "assistant":
                    st.write(f"**Yara**: {message['content']}")
        else:
            st.write("**Yara**: Sorry, I couldn't process your request. Please try again.")

# Clear chat history
if st.button("Clear Chat"):
    st.session_state["history"] = {}
    st.rerun()