import streamlit as st
import requests
import io
from PIL import Image

def upscale_image(api_key, image, prompt=""):
    """Upscale image using Stability AI Conservative Upscaler"""
    
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
        "prompt": (None, prompt if prompt else "enhance image quality and resolution"),
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
    
    st.write("📈 **Enhance image resolution and quality**")
    st.write("Upload any image to increase its resolution while maintaining quality.")
    
    uploaded_file = st.file_uploader(
        "Choose an image to upscale:",
        type=['png', 'jpg', 'jpeg'],
        help="Supported formats: PNG, JPG, JPEG"
    )
    
    if uploaded_file is not None:
        # Display original image
        original_image = Image.open(uploaded_file)
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("📷 Original Image")
            st.image(original_image, caption=f"Size: {original_image.size[0]}x{original_image.size[1]} pixels")
            
            # Show file info
            file_size = len(uploaded_file.getvalue()) / 1024  # KB
            st.caption(f"File size: {file_size:.1f} KB")
        
        # Optional enhancement prompt
        st.subheader("🎯 Enhancement Options")
        prompt = st.text_input(
            "Enhancement focus (optional):",
            placeholder="sharp details, high resolution, clear",
            help="Describe what aspects to enhance"
        )
        
        # Upscale button
        if st.button("📈 Upscale Image", type="primary", use_container_width=True):
            with st.spinner("🚀 Enhancing image resolution..."):
                upscaled_image = upscale_image(api_key, original_image, prompt)
                
                if upscaled_image:
                    with col2:
                        st.subheader("✨ Enhanced Image")
                        st.image(upscaled_image, caption=f"Size: {upscaled_image.size[0]}x{upscaled_image.size[1]} pixels")
                        
                        # Calculate improvements
                        original_pixels = original_image.size[0] * original_image.size[1]
                        upscaled_pixels = upscaled_image.size[0] * upscaled_image.size[1]
                        pixel_improvement = upscaled_pixels / original_pixels
                        
                        # Show stats
                        st.success(f"🎉 Resolution enhanced by {pixel_improvement:.1f}x!")
                        
                        col_stats1, col_stats2 = st.columns(2)
                        with col_stats1:
                            st.metric("Width", f"{upscaled_image.size[0]}px", f"+{upscaled_image.size[0] - original_image.size[0]}")
                        with col_stats2:
                            st.metric("Height", f"{upscaled_image.size[1]}px", f"+{upscaled_image.size[1] - original_image.size[1]}")
                        
                        # Download
                        st.markdown("---")
                        buf = io.BytesIO()
                        upscaled_image.save(buf, format="PNG")
                        
                        st.download_button(
                            label="📥 Download Enhanced Image",
                            data=buf.getvalue(),
                            file_name=f"upscaled_{uploaded_file.name.split('.')[0]}.png",
                            mime="image/png",
                            use_container_width=True
                        )
