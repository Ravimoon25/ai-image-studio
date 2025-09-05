import streamlit as st

# Page config
st.set_page_config(
    page_title="AI Image Studio",
    page_icon="🎨",
    layout="wide"
)

# Get API key from Streamlit secrets
api_key = st.secrets["STABILITY_API_KEY"]

# Sidebar navigation (removed Upscale)
st.sidebar.title("🎨 AI Image Studio")
page = st.sidebar.selectbox(
    "Choose a feature:",
    ["🏠 Home", "✨ Generate", "✏️ Edit", "🎛️ Control"]
)

# Main content based on selected page
if page == "🏠 Home":
    st.title("🎨 AI Image Studio")
    st.write("Your personal AI-powered image creation and editing suite")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.subheader("✨ Generate")
        st.write("Create images from text prompts using the latest AI models")
        
    with col2:
        st.subheader("✏️ Edit")
        st.write("Professional editing with inpainting, background removal, and object manipulation")
        
    with col3:
        st.subheader("🎛️ Control")
        st.write("Precise control over image generation")

elif page == "✨ Generate":
    st.header("✨ Image Generation")
    from modules.generate import show_generation_interface
    show_generation_interface(api_key)

elif page == "✏️ Edit":
    st.header("✏️ Image Editing")
    from modules.edit import show_edit_interface
    show_edit_interface(api_key)

elif page == "🎛️ Control":
    st.header("🎛️ Advanced Control")
    st.write("Control features coming soon...")
