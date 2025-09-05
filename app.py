import streamlit as st

# Page config
st.set_page_config(
    page_title="AI Image Studio",
    page_icon="🎨",
    layout="wide"
)

# Safe API key handling with better error handling
try:
    api_key = st.secrets["STABILITY_API_KEY"]
    if not api_key:
        raise KeyError("API key is empty")
except KeyError:
    st.error("⚠️ API Key not found in Streamlit secrets!")
    st.write("**To fix this:**")
    st.write("1. Go to your app → Click 'Manage app' (bottom right)")
    st.write("2. Go to 'Secrets' tab")
    st.write("3. Add: `STABILITY_API_KEY = \"your-api-key-here\"`")
    st.write("4. Save and the app will restart")
    st.stop()
except Exception as e:
    st.error(f"Error loading API key: {str(e)}")
    st.stop()

# Rest of your app code stays the same...
# Sidebar navigation
st.sidebar.title("🎨 AI Image Studio")
page = st.sidebar.selectbox(
    "Choose a feature:",
    ["🏠 Home", "✨ Generate", "📈 Upscale", "✏️ Edit", "🎛️ Control"]
)


# Sidebar navigation
st.sidebar.title("🎨 AI Image Studio")
page = st.sidebar.selectbox(
    "Choose a feature:",
    ["🏠 Home", "✨ Generate", "📈 Upscale", "✏️ Edit", "🎛️ Control"]
)

# Main content based on selected page
if page == "🏠 Home":
    st.title("🎨 AI Image Studio")
    st.write("Your personal AI-powered image creation and editing suite")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.subheader("✨ Generate")
        st.write("Create images from text prompts using the latest AI models")
        
    with col2:
        st.subheader("📈 Upscale")
        st.write("Enhance image resolution and quality")
        
    with col3:
        st.subheader("✏️ Edit")
        st.write("Advanced editing with masking and inpainting")
        
    with col4:
        st.subheader("🎛️ Control")
        st.write("Precise control over image generation")

elif page == "✨ Generate":
    st.header("✨ Image Generation")
    from modules.generate import show_generation_interface
    show_generation_interface(api_key)

elif page == "📈 Upscale":
    st.header("📈 Image Upscaling")
    from modules.upscale import show_upscale_interface
    show_upscale_interface(api_key)

elif page == "✏️ Edit":
    st.header("✏️ Image Editing")
    st.write("Edit images with masking tools")
    # We'll build this next

elif page == "🎛️ Control":
    st.header("🎛️ Advanced Control")
    st.write("Precise image control")
    # We'll build this next
