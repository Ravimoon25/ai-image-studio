
import streamlit as st
import requests
import io
from PIL import Image

def upscale_image(api_key, image, upscale_type="creative"):
    """Upscale image using Stability AI API"""
    
    if upscale_type == "creative":
        url = "https://api.stability.ai/v2beta/stable-image/upscale/creative"
    else:
        url = "https://api.stability.ai/v2beta/stable-image/upscale/conservative"
    
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Accept": "image/*"
    }
    
    # Convert PIL image to bytes
    img_byte_arr = io.BytesIO()
    image.save(img_byte_arr, format='PNG')
    img_byte_arr = img_byte_arr.getvalue()
    
    files = {
        "image": ("image.png", img_byte_arr, "image/png"),
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

def show_upscale_interface(api_key):
    """Show the upscale interface"""
    
    st.subheader("Upload Image")
    uploaded_file = st.file_uploader(
        "Choose an image to upscale:",
        type=['png', 'jpg', 'jpeg'],
        help="Upload an image to enhance its resolution and quality"
    )
    
    if uploaded_file is not None:
        # Display original image
        original_image = Image.open(uploaded_file)
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("Original Image")
            st.image(original_image, caption=f"Size: {original_image.size[0]}x{original_image.size[1]}")
        
        # Upscale options
        st.subheader("Upscale Settings")
        upscale_type = st.selectbox(
            "Choose upscale type:",
            ["Creative", "Conservative"],
            help="Creative: Better for artistic images, Conservative: Better for photos"
        )
        
        upscale_key = upscale_type.lower()
        
        # Upscale button
        if st.button("📈 Upscale Image", type="primary"):
            with st.spinner("Upscaling your image... This may take a moment."):
                upscaled_image = upscale_image(api_key, original_image, upscale_key)
                
                if upscaled_image:
                    with col2:
                        st.subheader("Upscaled Image")
                        st.image(upscaled_image, caption=f"Size: {upscaled_image.size[0]}x{upscaled_image.size[1]}")
                        
                        # Download button
                        buf = io.BytesIO()
                        upscaled_image.save(buf, format="PNG")
                        st.download_button(
                            label="📥 Download Upscaled Image",
                            data=buf.getvalue(),
                            file_name=f"upscaled_{upscale_type.lower()}.png",
                            mime="image/png"
                        )
                        
                        # Show improvement stats
                        original_pixels = original_image.size[0] * original_image.size[1]
                        upscaled_pixels = upscaled_image.size[0] * upscaled_image.size[1]
                        improvement = upscaled_pixels / original_pixels
                        
                        st.success(f"✨ Image enhanced by {improvement:.1f}x pixels!")
