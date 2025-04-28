# app.py
import streamlit as st
from model77777 import process_user_input, agent_triaj  # Import the initial agent and function

# Initialize session state to store messages and agent
if "messages" not in st.session_state:
    st.session_state.messages = []
if "agent" not in st.session_state:
    st.session_state.agent = agent_triaj  # Start with the initial triaj agent

# Set Raiffeisen-themed colors
PRIMARY_COLOR = "#FFD700"   # Raiffeisen yellow
SECONDARY_COLOR = "#000000"  # Black
BACKGROUND_COLOR = "#F2F2F2"
TEXT_COLOR = "#FFFFFF"

# Add custom styling with CSS
st.markdown(f"""
    <style>
    .main-container {{
        background-color: {BACKGROUND_COLOR};
    }}
    .chat-bubble {{
        padding: 10px;
        border-radius: 10px;
        margin: 10px 0;
        max-width: 80%;
        line-height: 1.6;
    }}
    .user-bubble {{
        background-color: {PRIMARY_COLOR};
        color: {SECONDARY_COLOR};
        text-align: left;
    }}
    .agent-bubble {{
        background-color: {SECONDARY_COLOR};
        color: {TEXT_COLOR};
        text-align: left;
    }}
    .header {{
        background-color: {SECONDARY_COLOR};
        padding: 10px;
        color: {TEXT_COLOR};
        font-size: 24px;
        text-align: center;
    }}
    .footer {{
        color: {SECONDARY_COLOR};
        text-align: center;
        padding: 10px 0 20px;
        font-size: 14px;
    }}
    </style>
""", unsafe_allow_html=True)

# Header with Raiffeisen logo and title
st.markdown(f"""
<div class="header">
    <img src="https://upload.wikimedia.org/wikipedia/commons/3/3d/Raiffeisen_Bank_logo.svg" width="150"/>
    <h2>Raiffeisen Bank Chatbot</h2>
</div>
""", unsafe_allow_html=True)

# Streamlit layout
st.write("Welcome! Talk to our Raiffeisen Bank chatbot for any banking inquiries.")

# Display chat messages
for message in st.session_state.messages:
    role = "user-bubble" if message["role"] == "user" else "agent-bubble"
    st.markdown(f'<div class="chat-bubble {role}">{message["content"]}</div>', unsafe_allow_html=True)

# User input section
user_input = st.text_input("Your message:", "")

# Send button and process user input
if st.button("Send") and user_input:
    agent, new_messages = process_user_input(user_input, st.session_state.agent, st.session_state.messages)
    
    # Update session state with new messages and agent
    st.session_state.agent = agent
    st.session_state.messages.extend(new_messages)
    
    # Rerun to display the new message
    st.experimental_rerun()

# Footer
st.markdown(f"""
<div class="footer">
    Raiffeisen Bank © 2024. All rights reserved.
</div>
""", unsafe_allow_html=True)
