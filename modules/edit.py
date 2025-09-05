import streamlit as st
import requests
import io
from PIL import Image, ImageDraw
import numpy as np

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

def outpaint_image(api_key, image, prompt, direction="up", pixels=32):
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
        "left": (None, str(pixels) if direction in ["left", "all"] else "0"),
        "right": (None, str(pixels) if direction in ["right", "all"] else "0"),
        "up": (None, str(pixels) if direction in ["up", "all"] else "0"),
        "down": (None, str(pixels) if direction in ["down", "all"] else "0"),
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

def create_simple_mask(image, mask_type, region=None):
    """Create simple masks for inpainting"""
    width, height = image.size
    mask = Image.new('L', (width, height), 0)  # Black background
    draw = ImageDraw.Draw(mask)
    
    if mask_type == "center_circle":
        # Circle in center for adding objects
        center_x, center_y = width // 2, height // 2
        radius = min(width, height) // 6
        draw.ellipse([center_x - radius, center_y - radius, 
                     center_x + radius, center_y + radius], fill=255)
    
    elif mask_type == "center_square":
        # Square in center
        size = min(width, height) // 4
        x1 = (width - size) // 2
        y1 = (height - size) // 2
        draw.rectangle([x1, y1, x1 + size, y1 + size], fill=255)
    
    elif mask_type == "top_half":
        # Top half of image
        draw.rectangle([0, 0, width, height // 2], fill=255)
    
    elif mask_type == "bottom_half":
        # Bottom half of image
        draw.rectangle([0, height // 2, width, height], fill=255)
    
    elif mask_type == "left_side":
        # Left third
        draw.rectangle([0, 0, width // 3, height], fill=255)
    
    elif mask_type == "right_side":
        # Right third
        draw.rectangle([2 * width // 3, 0, width, height], fill=255)
    
    return mask

def show_edit_interface(api_key):
    """Show the inpainting/outpainting focused interface"""
    
    st.write("✏️ **Professional Inpainting & Outpainting Tools**")
    st.write("High-quality editing with precise control!")
    
    # Image upload
    uploaded_file = st.file_uploader(
        "Upload image to edit:",
        type=['png', 'jpg', 'jpeg'],
        help="Upload the image you want to edit"
    )
    
    if uploaded_file is not None:
        original_image = Image.open(uploaded_file)
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.write("**📷 Original Image**")
            st.image(original_image, caption=f"Size: {original_image.size[0]}x{original_image.size[1]}")
        
        # Main editing tools
        edit_tool = st.selectbox(
            "Choose editing tool:",
            [
                "🗑️ Remove Background",
                "🎨 Inpainting - Replace Areas", 
                "➕ Inpainting - Add Objects",
                "🖼️ Outpainting - Extend Image"
            ],
            help="Select the editing operation"
        )
        
        st.markdown("---")
        
        if edit_tool == "🗑️ Remove Background":
            st.subheader("🗑️ Remove Background")
            st.write("✅ **Clean background removal**")
            
            if st.button("🗑️ Remove Background", type="primary", use_container_width=True):
                with st.spinner("🗑️ Removing background..."):
                    result = remove_background(api_key, original_image)
                    if result:
                        show_result(result, "Background removed!", "no_background.png", col2)
        
        elif edit_tool == "🎨 Inpainting - Replace Areas":
            st.subheader("🎨 Inpainting - Replace Areas")
            st.write("✅ **Replace specific parts of your image**")
            
            # Mask selection for replacement
            mask_area = st.selectbox(
                "Select area to replace:",
                [
                    "center_circle", "center_square", "top_half", 
                    "bottom_half", "left_side", "right_side"
                ],
                format_func=lambda x: {
                    "center_circle": "🔵 Center Circle",
                    "center_square": "⬜ Center Square", 
                    "top_half": "⬆️ Top Half",
                    "bottom_half": "⬇️ Bottom Half",
                    "left_side": "⬅️ Left Side",
                    "right_side": "➡️ Right Side"
                }[x]
            )
            
            replacement_prompt = st.text_area(
                "What to put in the selected area:",
                placeholder="beautiful flowers, modern building, blue sky, ocean waves...",
                help="Describe what should replace the selected area"
            )
            
            if st.button("🎨 Replace Area", type="primary", use_container_width=True):
                if replacement_prompt.strip():
                    mask = create_simple_mask(original_image, mask_area)
                    
                    # Show mask preview
                    st.write("**Mask Preview:**")
                    mask_preview = Image.new('RGBA', original_image.size, (0, 0, 0, 0))
                    mask_preview.paste((255, 0, 0, 128), mask=mask)
                    preview_combined = Image.alpha_composite(
                        original_image.convert('RGBA'),
                        mask_preview
                    )
                    st.image(preview_combined, caption="Red area will be replaced", width=300)
                    
                    with st.spinner("🎨 Replacing area..."):
                        result = inpaint_image(api_key, original_image, mask, replacement_prompt)
                        if result:
                            show_result(result, f"Replaced area with: {replacement_prompt[:30]}...", "inpainted.png", col2)
                else:
                    st.warning("Please describe what to put in the selected area.")
        
        elif edit_tool == "➕ Inpainting - Add Objects":
            st.subheader("➕ Inpainting - Add Objects")
            st.write("✅ **Add new objects to your image**")
            
            add_location = st.selectbox(
                "Where to add object:",
                ["center_circle", "center_square", "left_side", "right_side"],
                format_func=lambda x: {
                    "center_circle": "🔵 Center (Circle)",
                    "center_square": "⬜ Center (Square)",
                    "left_side": "⬅️ Left Side", 
                    "right_side": "➡️ Right Side"
                }[x]
            )
            
            # Object categories
            object_category = st.selectbox(
                "Object category:",
                ["👥 People", "🐕 Animals", "🚗 Vehicles", "🌸 Nature", "🏠 Buildings", "📱 Objects"],
                help="Choose the type of object to add"
            )
            
            object_prompt = st.text_area(
                "Describe the object to add:",
                placeholder="a person wearing a red jacket, a golden retriever, a vintage car, blooming roses...",
                help="Be specific about the object you want to add"
            )
            
            if st.button("➕ Add Object", type="primary", use_container_width=True):
                if object_prompt.strip():
                    mask = create_simple_mask(original_image, add_location)
                    
                    # Show where object will be added
                    st.write("**Addition Preview:**")
                    mask_preview = Image.new('RGBA', original_image.size, (0, 0, 0, 0))
                    mask_preview.paste((0, 255, 0, 128), mask=mask)
                    preview_combined = Image.alpha_composite(
                        original_image.convert('RGBA'),
                        mask_preview
                    )
                    st.image(preview_combined, caption="Green area = where object will be added", width=300)
                    
                    with st.spinner("➕ Adding object..."):
                        result = inpaint_image(api_key, original_image, mask, object_prompt)
                        if result:
                            show_result(result, f"Added: {object_prompt[:30]}...", "added_object.png", col2)
                else:
                    st.warning("Please describe the object you want to add.")
        
        elif edit_tool == "🖼️ Outpainting - Extend Image":
            st.subheader("🖼️ Outpainting - Extend Image")
            st.write("✅ **Expand your image in any direction**")
            
            col_dir, col_size = st.columns(2)
            
            with col_dir:
                direction = st.selectbox(
                    "Extend direction:",
                    ["up", "down", "left", "right", "all"],
                    format_func=lambda x: {
                        "up": "⬆️ Upward",
                        "down": "⬇️ Downward", 
                        "left": "⬅️ Leftward",
                        "right": "➡️ Rightward",
                        "all": "🔄 All Directions"
                    }[x]
                )
            
            with col_size:
                extension_size = st.selectbox(
                    "Extension size:",
                    [32, 64, 96, 128],
                    format_func=lambda x: f"{x} pixels",
                    index=1  # Default to 64
                )
            
            extension_prompt = st.text_area(
                "What should appear in the extended area:",
                placeholder="continue the landscape, more ocean, forest continuation, sky with clouds...",
                help="Describe what should be generated in the new expanded areas"
            )
            
            if st.button("🖼️ Extend Image", type="primary", use_container_width=True):
                if extension_prompt.strip():
                    with st.spinner("🖼️ Extending image..."):
                        result = outpaint_image(api_key, original_image, extension_prompt, direction, extension_size)
                        if result:
                            # Show size comparison
                            original_size = f"{original_image.size[0]}×{original_image.size[1]}"
                            new_size = f"{result.size[0]}×{result.size[1]}"
                            show_result(result, f"Extended from {original_size} to {new_size}", "outpainted.png", col2)
                else:
                    st.warning("Please describe what should appear in the extended area.")
        
        # Pro tips
        with st.expander("🎯 Pro Tips for Better Results"):
            st.write("**🎨 Inpainting Tips:**")
            st.write("- Be specific in your descriptions")
            st.write("- Consider lighting and style consistency")
            st.write("- Choose mask areas that make sense contextually")
            st.write("")
            st.write("**🖼️ Outpainting Tips:**")
            st.write("- Describe continuation that matches the existing scene")
            st.write("- Start with smaller extensions (32-64px) for better quality")
            st.write("- Use 'all directions' for dramatic scene expansion")

def show_result(result_image, caption, filename, column):
    """Helper function to display results"""
    with column:
        st.subheader("✨ Result")
        st.image(result_image, caption=caption)
        
        # Download button
        buf = io.BytesIO()
        result_image.save(buf, format="PNG")
        st.download_button(
            "📥 Download Result",
            data=buf.getvalue(),
            file_name=filename,
            mime="image/png",
            use_container_width=True
        )
