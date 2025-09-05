
import streamlit as st
import requests
import io
from PIL import Image, ImageDraw
import numpy as np
from streamlit_drawable_canvas import st_canvas
import cv2

def inpaint_image(api_key, image, mask, prompt):
    """Inpaint image using Stability AI API"""
    
    url = "https://api.stability.ai/v2beta/stable-image/edit/inpaint"
    
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Accept": "image/*"
    }
    
    # Convert images to bytes
    img_byte_arr = io.BytesIO()
    image.save(img_byte_arr, format='PNG')
    img_byte_arr = img_byte_arr.getvalue()
    
    mask_byte_arr = io.BytesIO()
    mask.save(mask_byte_arr, format='PNG')
    mask_byte_arr = mask_byte_arr.getvalue()
    
    files = {
        "image": ("image.png", img_byte_arr, "image/png"),
        "mask": ("mask.png", mask_byte_arr, "image/png"),
        "prompt": (None, prompt),
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

def outpaint_image(api_key, image, prompt, direction="up"):
    """Outpaint image using Stability AI API"""
    
    url = "https://api.stability.ai/v2beta/stable-image/edit/outpaint"
    
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Accept": "image/*"
    }
    
    img_byte_arr = io.BytesIO()
    image.save(img_byte_arr, format='PNG')
    img_byte_arr = img_byte_arr.getvalue()
    
    files = {
        "image": ("image.png", img_byte_arr, "image/png"),
        "prompt": (None, prompt),
        "left": (None, "32" if direction in ["left", "all"] else "0"),
        "right": (None, "32" if direction in ["right", "all"] else "0"),
        "up": (None, "32" if direction in ["up", "all"] else "0"),
        "down": (None, "32" if direction in ["down", "all"] else "0"),
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

def remove_background(api_key, image):
    """Remove background using Stability AI API"""
    
    url = "https://api.stability.ai/v2beta/stable-image/edit/remove-background"
    
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Accept": "image/*"
    }
    
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

def show_edit_interface(api_key):
    """Show the edit interface"""
    
    st.write("✏️ **Professional image editing with AI-powered tools**")
    
    # Edit mode selection
    edit_mode = st.selectbox(
        "Choose editing mode:",
        ["🎨 Inpainting", "🖼️ Outpainting", "🗑️ Remove Background"],
        help="Select the type of editing you want to perform"
    )
    
    # Image upload
    uploaded_file = st.file_uploader(
        "Upload image to edit:",
        type=['png', 'jpg', 'jpeg'],
        help="Upload the image you want to edit"
    )
    
    if uploaded_file is not None:
        original_image = Image.open(uploaded_file)
        
        st.markdown("---")
        
        if edit_mode == "🎨 Inpainting":
            show_inpainting_interface(api_key, original_image)
        elif edit_mode == "🖼️ Outpainting":
            show_outpainting_interface(api_key, original_image)
        elif edit_mode == "🗑️ Remove Background":
            show_background_removal_interface(api_key, original_image)

def show_inpainting_interface(api_key, image):
    """Show inpainting interface with interactive masking"""
    
    st.subheader("🎨 Inpainting - Fill Masked Areas")
    st.write("Draw on the image to mark areas you want to replace, then describe what should appear there.")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.write("**📷 Original Image**")
        st.image(image, caption=f"Size: {image.size[0]}x{image.size[1]}")
    
    # Resize image for canvas if too large
    canvas_width = min(500, image.size[0])
    canvas_height = int((canvas_width / image.size[0]) * image.size[1])
    display_image = image.resize((canvas_width, canvas_height))
    
    st.subheader("🖌️ Draw Mask")
    st.write("Paint over the areas you want to replace:")
    
    # Drawing canvas
    canvas_result = st_canvas(
        fill_color="rgba(255, 255, 255, 0.8)",
        stroke_width=20,
        stroke_color="#FFFFFF",
        background_color="#000000",
        background_image=display_image,
        update_streamlit=True,
        height=canvas_height,
        width=canvas_width,
        drawing_mode="freedraw",
        key="inpaint_canvas",
    )
    
    # Prompt for inpainting
    prompt = st.text_area(
        "What should appear in the masked areas?",
        placeholder="a beautiful flower garden, a modern building, blue sky with clouds...",
        help="Describe what you want to generate in the painted areas"
    )
    
    if st.button("🎨 Apply Inpainting", type="primary") and prompt.strip():
        if canvas_result.image_data is not None:
            # Create mask from canvas
            mask_array = canvas_result.image_data[:, :, 3]  # Alpha channel
            mask_pil = Image.fromarray(mask_array, mode='L')
            
            # Resize mask to original image size
            mask_resized = mask_pil.resize(image.size)
            
            with st.spinner("🎨 Applying inpainting..."):
                result = inpaint_image(api_key, image, mask_resized, prompt)
                
                if result:
                    with col2:
                        st.write("**✨ Inpainted Result**")
                        st.image(result, caption="Inpainting complete!")
                        
                        # Download
                        buf = io.BytesIO()
                        result.save(buf, format="PNG")
                        st.download_button(
                            "📥 Download Result",
                            data=buf.getvalue(),
                            file_name="inpainted_image.png",
                            mime="image/png"
                        )
        else:
            st.warning("Please draw a mask on the image first!")

def show_outpainting_interface(api_key, image):
    """Show outpainting interface"""
    
    st.subheader("🖼️ Outpainting - Extend Image Borders")
    st.write("Expand your image in any direction with AI-generated content.")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.write("**📷 Original Image**")
        st.image(image, caption=f"Size: {image.size[0]}x{image.size[1]}")
    
    # Direction selection
    direction = st.selectbox(
        "Expand in which direction?",
        ["up", "down", "left", "right", "all"],
        help="Choose which direction to expand the image"
    )
    
    # Prompt for outpainting
    prompt = st.text_area(
        "What should appear in the extended areas?",
        placeholder="continue the landscape, more of the same scene, ocean waves...",
        help="Describe what should be generated in the new areas"
    )
    
    if st.button("🖼️ Apply Outpainting", type="primary") and prompt.strip():
        with st.spinner("🖼️ Extending image..."):
            result = outpaint_image(api_key, image, prompt, direction)
            
            if result:
                with col2:
                    st.write("**✨ Extended Image**")
                    st.image(result, caption="Outpainting complete!")
                    
                    # Show size comparison
                    st.write(f"New size: {result.size[0]}x{result.size[1]} (was {image.size[0]}x{image.size[1]})")
                    
                    # Download
                    buf = io.BytesIO()
                    result.save(buf, format="PNG")
                    st.download_button(
                        "📥 Download Result",
                        data=buf.getvalue(),
                        file_name="outpainted_image.png",
                        mime="image/png"
                    )

def show_background_removal_interface(api_key, image):
    """Show background removal interface"""
    
    st.subheader("🗑️ Remove Background")
    st.write("Automatically remove the background from your image.")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.write("**📷 Original Image**")
        st.image(image, caption=f"Size: {image.size[0]}x{image.size[1]}")
    
    if st.button("🗑️ Remove Background", type="primary"):
        with st.spinner("🗑️ Removing background..."):
            result = remove_background(api_key, image)
            
            if result:
                with col2:
                    st.write("**✨ Background Removed**")
                    st.image(result, caption="Background removal complete!")
                    
                    # Download
                    buf = io.BytesIO()
                    result.save(buf, format="PNG")
                    st.download_button(
                        "📥 Download PNG",
                        data=buf.getvalue(),
                        file_name="no_background.png",
                        mime="image/png"
                    )
