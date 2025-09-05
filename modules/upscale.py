import streamlit as st
import requests
import io
from PIL import Image
import time

def upscale_image_conservative(api_key, image, prompt=""):
    """Conservative upscale - synchronous"""
    url = "https://api.stability.ai/v2beta/stable-image/upscale/conservative"
    
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Accept": "image/*"
    }
    
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
            return Image.open(io.BytesIO(response.content))
        else:
            st.error(f"Error: {response.status_code} - {response.text}")
            return None
            
    except Exception as e:
        st.error(f"Request failed: {str(e)}")
        return None

def upscale_image_creative(api_key, image, prompt=""):
    """Creative upscale - asynchronous with polling"""
    
    # Step 1: Start the upscale job
    url = "https://api.stability.ai/v2beta/stable-image/upscale/creative"
    
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Accept": "application/json"  # Accept JSON for job ID
    }
    
    img_byte_arr = io.BytesIO()
    image.save(img_byte_arr, format='PNG')
    img_byte_arr = img_byte_arr.getvalue()
    
    files = {
        "image": ("image.png", img_byte_arr, "image/png"),
        "prompt": (None, prompt if prompt else "enhance image quality"),
        "output_format": (None, "png")
    }
    
    try:
        # Start the job
        response = requests.post(url, headers=headers, files=files)
        
        if response.status_code == 200:
            result = response.json()
            job_id = result.get('id')
            
            if job_id:
                st.info(f"🎨 Creative upscaling started! Job ID: {job_id}")
                
                # Step 2: Poll for result
                return poll_for_result(api_key, job_id)
            else:
                st.error("No job ID returned")
                return None
        else:
            st.error(f"Error: {response.status_code} - {response.text}")
            return None
            
    except Exception as e:
        st.error(f"Request failed: {str(e)}")
        return None

def poll_for_result(api_key, job_id, max_attempts=30):
    """Poll for the creative upscale result"""
    
    url = f"https://api.stability.ai/v2beta/stable-image/upscale/creative/result/{job_id}"
    
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Accept": "image/*"
    }
    
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    for attempt in range(max_attempts):
        try:
            response = requests.get(url, headers=headers)
            
            if response.status_code == 200:
                # Check if it's an image
                content_type = response.headers.get('content-type', '')
                if 'image' in content_type:
                    progress_bar.progress(100)
                    status_text.success("✅ Creative upscaling completed!")
                    return Image.open(io.BytesIO(response.content))
                else:
                    # Still processing
                    progress = min(90, (attempt / max_attempts) * 90)
                    progress_bar.progress(int(progress))
                    status_text.info(f"🔄 Processing... ({attempt + 1}/{max_attempts})")
                    time.sleep(2)
            
            elif response.status_code == 202:
                # Still processing
                progress = min(90, (attempt / max_attempts) * 90)
                progress_bar.progress(int(progress))
                status_text.info(f"🔄 Processing... ({attempt + 1}/{max_attempts})")
                time.sleep(2)
            
            else:
                st.error(f"Error checking result: {response.status_code} - {response.text}")
                return None
                
        except Exception as e:
            st.error(f"Error polling result: {str(e)}")
            return None
    
    st.error("⏰ Creative upscaling timed out. The job may still be processing.")
    return None

def upscale_image(api_key, image, upscale_type="conservative", prompt=""):
    """Main upscale function"""
    
    if upscale_type == "creative":
        return upscale_image_creative(api_key, image, prompt)
    else:
        return upscale_image_conservative(api_key, image, prompt)

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
                ["Conservative", "Creative"],
                help="Conservative: Fast, reliable\nCreative: Higher quality, takes longer",
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
        
        # Info about processing time
        if upscale_type == "Creative":
            st.info("ℹ️ Creative upscaling takes longer (30-60 seconds) but produces higher quality results.")
        
        # Upscale button
        if st.button("📈 Upscale Image", type="primary", use_container_width=True):
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
