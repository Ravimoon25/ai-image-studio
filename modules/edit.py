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

def outpaint_image(api_key, image, prompt, direction="up", pixels=64):
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

def create_smart_mask(image, mask_type, custom_coords=None):
    """Create intelligent masks for different editing scenarios"""
    width, height = image.size
    mask = Image.new('L', (width, height), 0)
    draw = ImageDraw.Draw(mask)
    
    if mask_type == "object_center":
        # Smart object detection area (center focus)
        center_x, center_y = width // 2, height // 2
        radius = min(width, height) // 5
        draw.ellipse([center_x - radius, center_y - radius, 
                     center_x + radius, center_y + radius], fill=255)
    
    elif mask_type == "portrait_face":
        # Face area for portraits
        face_width = width // 4
        face_height = height // 3
        x1 = (width - face_width) // 2
        y1 = height // 6
        draw.ellipse([x1, y1, x1 + face_width, y1 + face_height], fill=255)
    
    elif mask_type == "background_edges":
        # Edge areas for background replacement
        border_size = min(width, height) // 20
        # Top, bottom, left, right borders
        draw.rectangle([0, 0, width, border_size], fill=255)  # Top
        draw.rectangle([0, height-border_size, width, height], fill=255)  # Bottom
        draw.rectangle([0, 0, border_size, height], fill=255)  # Left
        draw.rectangle([width-border_size, 0, width, height], fill=255)  # Right
    
    elif mask_type == "clothing_area":
        # Lower body area for clothing changes
        y_start = height // 3
        draw.rectangle([width//6, y_start, 5*width//6, 5*height//6], fill=255)
    
    elif mask_type == "sky_area":
        # Top area for sky replacement
        draw.rectangle([0, 0, width, height//3], fill=255)
    
    elif mask_type == "ground_area":
        # Bottom area for ground/floor changes
        draw.rectangle([0, 2*height//3, width, height], fill=255)
    
    elif mask_type == "left_object":
        # Left side object area
        draw.ellipse([width//10, height//4, 2*width//5, 3*height//4], fill=255)
    
    elif mask_type == "right_object":
        # Right side object area
        draw.ellipse([3*width//5, height//4, 9*width//10, 3*height//4], fill=255)
    
    elif mask_type == "custom_area" and custom_coords:
        # Custom rectangular area
        x1, y1, x2, y2 = custom_coords
        draw.rectangle([x1, y1, x2, y2], fill=255)
    
    return mask

def show_edit_interface(api_key):
    """Show the professional edit interface"""
    
    st.write("✏️ **Professional AI Image Editing**")
    st.write("🎯 **Smart area selection for precise editing**")
    
    # Image upload
    uploaded_file = st.file_uploader(
        "Upload image to edit:",
        type=['png', 'jpg', 'jpeg'],
        help="Upload the image you want to edit"
    )
    
    if uploaded_file is not None:
        original_image = Image.open(uploaded_file)
        
        # Store image in session state for consistency
        if 'current_image' not in st.session_state:
            st.session_state.current_image = original_image
        
        # Main editing tools
        edit_tool = st.selectbox(
            "Choose editing tool:",
            [
                "🗑️ Remove Background",
                "🎨 Smart Inpainting",
                "🖼️ Outpainting"
            ],
            help="Select the editing operation"
        )
        
        st.markdown("---")
        
        if edit_tool == "🗑️ Remove Background":
            show_background_removal(api_key, original_image)
        elif edit_tool == "🎨 Smart Inpainting":
            show_smart_inpainting(api_key, original_image)
        elif edit_tool == "🖼️ Outpainting":
            show_outpainting(api_key, original_image)

def show_background_removal(api_key, image):
    """Show background removal interface"""
    st.subheader("🗑️ Remove Background")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.write("**📷 Original Image**")
        st.image(image, caption=f"Size: {image.size[0]}x{image.size[1]}")
    
    if st.button("🗑️ Remove Background", type="primary", use_container_width=True):
        with st.spinner("🗑️ Removing background..."):
            result = remove_background(api_key, image)
            if result:
                show_result(result, "Background removed!", "no_background.png", col2)

def show_smart_inpainting(api_key, image):
    """Show smart inpainting with preset intelligent areas"""
    st.subheader("🎨 Smart Inpainting")
    st.write("🎯 **Choose what type of edit you want to make**")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.write("**📷 Original Image**")
        st.image(image, caption=f"Size: {image.size[0]}x{image.size[1]}")
    
    # Smart editing categories
    st.subheader("🎯 What do you want to edit?")
    
    edit_category = st.selectbox(
        "Editing goal:",
        [
            "👤 Change face/head area",
            "👕 Change clothing/outfit", 
            "🏠 Add object in center",
            "🌅 Change sky/background",
            "🌱 Change ground/floor",
            "⬅️ Add object on left",
            "➡️ Add object on right",
            "🔧 Custom area"
        ],
        help="Choose the type of edit you want to make"
    )
    
    # Map selections to mask types
    mask_mapping = {
        "👤 Change face/head area": "portrait_face",
        "👕 Change clothing/outfit": "clothing_area",
        "🏠 Add object in center": "object_center", 
        "🌅 Change sky/background": "sky_area",
        "🌱 Change ground/floor": "ground_area",
        "⬅️ Add object on left": "left_object",
        "➡️ Add object on right": "right_object",
        "🔧 Custom area": "custom_area"
    }
    
    mask_type = mask_mapping[edit_category]
    
    # Custom area coordinates if needed
    custom_coords = None
    if mask_type == "custom_area":
        st.write("**Define custom area (as % of image):**")
        col_x1, col_y1, col_x2, col_y2 = st.columns(4)
        
        with col_x1:
            x1_pct = st.slider("Left %", 0, 100, 20, key="x1")
        with col_y1:
            y1_pct = st.slider("Top %", 0, 100, 20, key="y1") 
        with col_x2:
            x2_pct = st.slider("Right %", 0, 100, 80, key="x2")
        with col_y2:
            y2_pct = st.slider("Bottom %", 0, 100, 80, key="y2")
        
        # Convert percentages to pixel coordinates
        custom_coords = (
            int(image.size[0] * x1_pct / 100),
            int(image.size[1] * y1_pct / 100),
            int(image.size[0] * x2_pct / 100),
            int(image.size[1] * y2_pct / 100)
        )
    
    # Create and show mask preview
    mask = create_smart_mask(image, mask_type, custom_coords)
    
    # Show mask preview
    st.write("**🎯 Preview - Red area will be edited:**")
    mask_preview = Image.new('RGBA', image.size, (0, 0, 0, 0))
    mask_preview.paste((255, 0, 0, 128), mask=mask)
    preview_combined = Image.alpha_composite(image.convert('RGBA'), mask_preview)
    st.image(preview_combined, width=500)
    
    # Editing prompt with suggestions
    st.subheader("📝 What should appear in the red area?")
    
    # Context-aware suggestions
    suggestion_mapping = {
        "portrait_face": ["smiling expression", "different hairstyle", "sunglasses", "hat"],
        "clothing_area": ["red dress", "business suit", "casual t-shirt", "winter coat"],
        "object_center": ["beautiful flowers", "cute dog", "vintage car", "modern sculpture"],
        "sky_area": ["blue sky with clouds", "sunset colors", "starry night", "dramatic storm clouds"],
        "ground_area": ["green grass", "sandy beach", "wooden floor", "stone pathway"],
        "left_object": ["person standing", "tree", "lamp post", "decorative plant"],
        "right_object": ["person sitting", "flower vase", "modern chair", "artwork"],
        "custom_area": ["beautiful landscape", "modern architecture", "artistic pattern", "natural texture"]
    }
    
    suggestions = suggestion_mapping.get(mask_type, [])
    
    if suggestions:
        st.write("**💡 Quick suggestions:**")
        suggestion_cols = st.columns(min(4, len(suggestions)))
        selected_suggestion = None
        
        for i, suggestion in enumerate(suggestions):
            with suggestion_cols[i % 4]:
                if st.button(f"💡 {suggestion}", key=f"sug_{i}"):
                    selected_suggestion = suggestion
    
    # Main prompt input
    prompt = st.text_area(
        "Describe what should appear in the selected area:",
        value=selected_suggestion or "",
        placeholder="be specific: a person wearing a blue jacket, beautiful sunset sky, modern furniture...",
        help="The more specific you are, the better the results",
        height=80
    )
    
    # Apply inpainting
    if st.button("🎨 Apply Smart Inpainting", type="primary", use_container_width=True):
        if prompt.strip():
            with st.spinner("🎨 Applying smart inpainting..."):
                result = inpaint_image(api_key, image, mask, prompt)
                if result:
                    show_result(result, f"Edited: {edit_category}", "smart_inpainted.png", col2)
        else:
            st.warning("Please describe what should appear in the selected area.")

def show_outpainting(api_key, image):
    """Show outpainting interface"""
    st.subheader("🖼️ Outpainting - Extend Image")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.write("**📷 Original Image**")
        st.image(image, caption=f"Size: {image.size[0]}x{image.size[1]}")
    
    col_dir, col_size = st.columns(2)
    
    with col_dir:
        direction = st.selectbox(
            "Extension direction:",
            ["up", "down", "left", "right", "all"],
            format_func=lambda x: {
                "up": "⬆️ Upward",
                "down": "⬇️ Downward",
                "left": "⬅️ Leftward", 
                "right": "➡️ Rightward",
                "all": "🔄 All directions"
            }[x]
        )
    
    with col_size:
        pixels = st.selectbox(
            "Extension size:",
            [32, 64, 96, 128],
            format_func=lambda x: f"{x} pixels",
            index=1
        )
    
    # Extension suggestions
    extension_suggestions = [
        "continue the landscape", "more sky with clouds", "extend the ocean",
        "more forest area", "continue the building", "expand the scene naturally"
    ]
    
    st.write("**💡 Extension ideas:**")
    ext_cols = st.columns(3)
    selected_ext = None
    
    for i, suggestion in enumerate(extension_suggestions):
        with ext_cols[i % 3]:
            if st.button(f"💡 {suggestion}", key=f"ext_{i}"):
                selected_ext = suggestion
    
    prompt = st.text_area(
        "What should appear in the extended area:",
        value=selected_ext or "",
        placeholder="continue the landscape, more ocean waves, sky with clouds...",
        help="Describe what should be generated in the new expanded areas"
    )
    
    if st.button("🖼️ Extend Image", type="primary", use_container_width=True):
        if prompt.strip():
            with st.spinner("🖼️ Extending image..."):
                result = outpaint_image(api_key, image, prompt, direction, pixels)
                if result:
                    original_size = f"{image.size[0]}×{image.size[1]}"
                    new_size = f"{result.size[0]}×{result.size[1]}"
                    show_result(result, f"Extended from {original_size} to {new_size}", "outpainted.png", col2)
        else:
            st.warning("Please describe what should appear in the extended area.")

def show_result(result_image, caption, filename, column):
    """Helper function to display results"""
    with column:
        st.subheader("✨ Result")
        st.image(result_image, caption=caption)
        
        buf = io.BytesIO()
        result_image.save(buf, format="PNG")
        st.download_button(
            "📥 Download Result",
            data=buf.getvalue(),
            file_name=filename,
            mime="image/png",
            use_container_width=True
        )
