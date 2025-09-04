import streamlit as st
import os

# Page config
st.set_page_config(
    page_title="AI Image Studio",
    page_icon="🎨",
    layout="wide"
)

# Safe API key handling
def get_api_key():
    # First try Streamlit secrets (for deployment)
    try:
        return st.secrets["STABILITY_API_KEY"]
    except:
        # Fallback to user input
        return st.sidebar.text_input("Enter Stability AI API Key:", type="password")

# Title
st.title("🎨 AI Image Studio")
st.write("Your personal AI-powered image creation and editing suite")

# Get API key
api_key = get_api_key()

if api_key:
    st.success("API Key loaded! Ready to build features.")
else:
    st.warning("Please enter your API key to continue.")
