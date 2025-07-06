import streamlit as st
import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain.schema import HumanMessage, AIMessage

# Load environment variables
load_dotenv()

# Initialize the ChatOpenAI model
@st.cache_resource
def init_llm():
    return ChatOpenAI(
        
        model="gpt-4o-mini",
        temperature=0.1,
        max_tokens=200  # Increased for better context explanations
    )

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Streamlit UI
st.title("🤖 Simple Chatbot")
st.write("Ask me anything and I'll give you a short, simple answer!")

# Display chat history
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Chat input
if prompt := st.chat_input("What would you like to know?"):
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": prompt})
    
    # Display user message
    with st.chat_message("user"):
        st.markdown(prompt)
    
    # Get bot response
    with st.chat_message("assistant"):
        try:
            llm = init_llm()
            
            # Create a system message to ensure short responses and context awareness
            system_prompt = "You are a helpful assistant. Always give short, simple, and direct answers. Keep responses under 100 words. Pay attention to the conversation history to maintain context."
            
            # Prepare messages for the model including recent chat history
            messages = [HumanMessage(content=system_prompt)]
            
            # Add recent chat history (last 10 messages) to provide context
            recent_messages = st.session_state.messages[-10:] if len(st.session_state.messages) > 10 else st.session_state.messages
            
            for msg in recent_messages:
                if msg["role"] == "user":
                    messages.append(HumanMessage(content=msg["content"]))
                else:
                    messages.append(AIMessage(content=msg["content"]))
            
            # Add the current user message
            messages.append(HumanMessage(content=prompt))
            
            # Get response from the model
            response = llm.invoke(messages)
            bot_response = response.content
            
            # Display response
            st.markdown(bot_response)
            
            # Add assistant response to chat history
            st.session_state.messages.append({"role": "assistant", "content": bot_response})
            
        except Exception as e:
            error_msg = f"Error: {str(e)}"
            st.error(error_msg)
            st.session_state.messages.append({"role": "assistant", "content": error_msg})

# Sidebar with clear chat button
with st.sidebar:
    st.header("Chat Controls")
    if st.button("Clear Chat History"):
        st.session_state.messages = []
        st.rerun()
    
    st.markdown("---")
    st.markdown("**Instructions:**")
    st.markdown("1. Make sure you have your OpenAI API key in a `.env` file")
    st.markdown("2. The format should be: `OPENAI_API_KEY=your_api_key_here`")
    st.markdown("3. Install required packages: `pip install streamlit langchain-openai python-dotenv`")
