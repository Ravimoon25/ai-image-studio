import streamlit as st
import requests
import io
from PIL import Image

def generate_image(api_key, prompt, model="stable-image-ultra", width=1024, height=1024):
    """Generate image using Stability AI API"""
    
    url = "https://api.stability.ai/v2beta/stable-image/generate/ultra"
    
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Accept": "image/*"
    }
    
    # Use files parameter for multipart/form-data
    files = {
        "prompt": (None, prompt),
        "width": (None, str(width)),
        "height": (None, str(height)),
        "output_format": (None, "png")
    }
    
    try:
        response = requests.post(url, headers=headers, files=files)
        
        if response.status_code == 200:
            return Image.open(io.BytesIO(response.content))
        else:
            st.error(f"Error: {response.status_code} - {response.text}")
            return None
            
    except Exception as e:
        st.error(f"Request failed: {str(e)}")
        return None

def show_generation_interface(api_key):
    """Show the generation interface"""
    
    st.subheader("Model Selection")
    model_options = {
        "Stable Image Ultra": "stable-image-ultra",
        "Stable Image Core": "stable-image-core", 
        "SDXL 1.0": "sdxl-1.0"
    }
    
    selected_model = st.selectbox(
        "Choose AI model:",
        list(model_options.keys())
    )
    
    # Prompt input
    st.subheader("Prompt")
    prompt = st.text_area(
        "Describe the image you want to generate:",
        height=100,
        placeholder="A serene mountain landscape at sunset with golden light..."
    )
    
    # Image dimensions
    col1, col2 = st.columns(2)
    with col1:
        width = st.selectbox("Width", [512, 768, 1024, 1152, 1344], index=2)
    with col2:
        height = st.selectbox("Height", [512, 768, 1024, 1152, 1344], index=2)
    
    # Generate button
    if st.button("🎨 Generate Image", type="primary"):
        if prompt.strip():
            with st.spinner("Generating your image..."):
                model_key = model_options[selected_model]
                image = generate_image(api_key, prompt, model_key, width, height)
                
                if image:
                    st.success("Image generated successfully!")
                    
                    # Display image
                    st.image(image, caption=f"Generated: {prompt[:50]}...")
                    
                    # Download button
                    buf = io.BytesIO()
                    image.save(buf, format="PNG")
                    st.download_button(
                        label="📥 Download Image",
                        data=buf.getvalue(),
                        file_name=f"generated_{len(prompt)}.png",
                        mime="image/png"
                    )
        else:
            st.warning("Please enter a prompt to generate an image.")
