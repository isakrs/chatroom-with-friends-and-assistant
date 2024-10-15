# Chatroom With Friends and Assistant - Hackathon Project: MQTT-Based Chatroom with GPT Integration

## Project Overview

This project demonstrates a **Pub/Sub architecture** using MQTT (Message Queuing Telemetry Transport) protocol for real-time communication between different components of a web-based application. The system includes:

1. **Publisher (Main Branch)**: A chatbot interface where users can ask questions, powered by OpenAI's GPT-4 API.
2. **Subscriber (Subscribe Branch)**: A separate interface that listens for and displays the conversation happening in the chatroom in real-time using MQTT.

Both branches are built using **Streamlit** to create user-friendly web interfaces, and they communicate using **MQTT** to publish and subscribe to messages under a common topic. The two branches are:

- **Main Branch**: Where users can interact with the GPT-powered assistant.
- **Subscribe Branch**: Displays the real-time conversation happening on the main branch.

## Key Features

1. **MQTT Integration**:

   - Real-time message publishing and subscribing using MQTT.
   - Demonstrates a simple Pub/Sub communication system.
   - Uses `test.mosquitto.org` as the broker for public message transmission.

2. **GPT-4 Integration**:

   - OpenAI’s GPT-4 API provides intelligent responses to user queries.
   - GPT acts as a digital assistant for Yara International ASA's production planning system, offering realistic data and operational advice.

3. **Real-Time UI**:
   - **Main branch UI**: Users can ask questions and see responses directly on the same page.
   - **Subscriber branch UI**: Observers can view the conversation in real-time, including both user questions and GPT responses.

## How It Works

### Main Branch (Publisher)

- Users interact with a chatbot via a simple text input.
- Each question triggers a request to the GPT-4 API, and the response is displayed in the UI.
- Both the question and the response are **published** to an MQTT topic (`hackaton-test`), making them available to subscribers.

### Subscribe Branch (Subscriber)

- This branch runs an MQTT **subscriber** that listens for messages published on the `hackaton-test` topic.
- Messages are displayed in real-time using Streamlit's UI, updating every second to ensure that all incoming messages are shown promptly.

## Links to Project Components

- **Main Branch (Publisher)**: [Chat with GPT](https://chatroom-with-friends-and-assistant.streamlit.app/)
- **Subscribe Branch (Subscriber)**: [Real-time MQTT Message Viewer](https://chatroom-with-friends-and-assistant-subscribe.streamlit.app/)

## How to Run Locally

### Prerequisites

- Install Python 3.8+
- Install required packages:
  ```bash
  pip install -r requirements.txt
  ```

### Running the Main Branch (Publisher)

1. Set up `.env` with your OpenAI API key and URL.
2. Run the app:
   ```bash
   streamlit run main.py
   ```

### Running the Subscribe Branch (Subscriber)

1. Run the app:
   ```bash
   streamlit run app.py
   ```

## Future Improvements

- **Scalability**: Move from a public MQTT broker to a more secure, private broker.
- **Enhanced UI**: Improve the UI design for better user experience.
- **New Features**: Add multi-topic support for more complex pub/sub scenarios.

This project showcases the integration of a Pub/Sub architecture in a real-time chat application using MQTT, coupled with an advanced GPT assistant to handle user inquiries efficiently.
