import streamlit as st
import requests
import io
from PIL import Image

def upscale_image(api_key, image, upscale_type="creative", prompt=""):
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
        "prompt": (None, prompt if prompt else "enhance image quality"),
        "output_format": (None, "png")
    }
    
    try:
        response = requests.post(url, headers=headers, files=files)
        
        if response.status_code == 200:
            # Check if response is actually an image
            content_type = response.headers.get('content-type', '')
            
            if 'image' in content_type:
                try:
                    return Image.open(io.BytesIO(response.content))
                except Exception as img_error:
                    st.error(f"Failed to process image: {str(img_error)}")
                    st.write(f"Content type: {content_type}")
                    st.write(f"Response size: {len(response.content)} bytes")
                    return None
            else:
                # Response might be JSON with error
                try:
                    error_data = response.json()
                    st.error(f"API returned error: {error_data}")
                except:
                    st.error(f"Unexpected response format. Content type: {content_type}")
                    st.write(f"Response content: {response.text[:200]}...")
                return None
        else:
            try:
                error_data = response.json()
                st.error(f"Error {response.status_code}: {error_data}")
            except:
                st.error(f"Error {response.status_code}: {response.text}")
            return None
            
    except requests.exceptions.RequestException as e:
        st.error(f"Request failed: {str(e)}")
        return None
    except Exception as e:
        st.error(f"Unexpected error: {str(e)}")
        return None

def show_upscale_interface(api_key):
    """Show the upscale interface"""
    
    st.subheader("📤 Upload Image")
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
            st.subheader("📷 Original Image")
            st.image(original_image, caption=f"Size: {original_image.size[0]}x{original_image.size[1]}")
        
        # Upscale options
        st.subheader("⚙️ Upscale Settings")
        
        col_type, col_prompt = st.columns([1, 2])
        
        with col_type:
            upscale_type = st.selectbox(
                "Upscale type:",
                ["Conservative", "Creative"],  # Put Conservative first since it works
                help="Conservative: Better for photos (more reliable)\nCreative: Better for artistic images",
                key="upscale_type_select"
            )
        
        with col_prompt:
            prompt = st.text_input(
                "Enhancement prompt (optional):",
                placeholder="high quality, detailed, sharp",
                help="Describe how you want the image enhanced",
                key="upscale_prompt_input"
            )
        
        upscale_key = upscale_type.lower()
        
        # Warning for Creative mode
        if upscale_type == "Creative":
            st.warning("⚠️ Creative upscaling is experimental and may occasionally fail. Try Conservative if you encounter issues.")
        
        # Upscale button
        if st.button("📈 Upscale Image", type="primary", use_container_width=True):
            with st.spinner(f"🚀 {upscale_type} upscaling in progress... This may take a moment."):
                upscaled_image = upscale_image(api_key, original_image, upscale_key, prompt)
                
                if upscaled_image:
                    with col2:
                        st.subheader("✨ Upscaled Image")
                        st.image(upscaled_image, caption=f"Size: {upscaled_image.size[0]}x{upscaled_image.size[1]}")
                        
                        # Show improvement stats
                        original_pixels = original_image.size[0] * original_image.size[1]
                        upscaled_pixels = upscaled_image.size[0] * upscaled_image.size[1]
                        improvement = upscaled_pixels / original_pixels
                        
                        st.success(f"🎉 Image enhanced by {improvement:.1f}x pixels!")
                        
                        # Download section
                        st.markdown("---")
                        
                        download_col1, download_col2 = st.columns([2, 1])
                        
                        with download_col1:
                            filename = st.text_input(
                                "Filename:", 
                                value=f"upscaled_{upscale_type.lower()}",
                                key="upscale_filename"
                            )
                        
                        with download_col2:
                            buf = io.BytesIO()
                            upscaled_image.save(buf, format="PNG")
                            st.download_button(
                                label="📥 Download",
                                data=buf.getvalue(),
                                file_name=f"{filename}.png",
                                mime="image/png",
                                use_container_width=True
                            )
                else:
                    st.error("Failed to upscale image. You can try:")
                    st.write("- Using Conservative mode instead")
                    st.write("- Trying a different image")
                    st.write("- Simplifying the enhancement prompt")
