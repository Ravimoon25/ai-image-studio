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

def create_coordinate_mask(image, coords_list, brush_size=30):
    """Create mask from coordinate points"""
    mask = Image.new('L', image.size, 0)  # Black background
    draw = ImageDraw.Draw(mask)
    
    for coords in coords_list:
        x, y = coords
        # Draw a circle at each coordinate
        radius = brush_size // 2
        draw.ellipse([x - radius, y - radius, x + radius, y + radius], fill=255)
    
    return mask

def create_area_mask(image, x1_pct, y1_pct, x2_pct, y2_pct, shape="rectangle"):
    """Create mask from area percentages"""
    width, height = image.size
    
    x1 = int(width * x1_pct / 100)
    y1 = int(height * y1_pct / 100) 
    x2 = int(width * x2_pct / 100)
    y2 = int(height * y2_pct / 100)
    
    mask = Image.new('L', image.size, 0)
    draw = ImageDraw.Draw(mask)
    
    if shape == "rectangle":
        draw.rectangle([x1, y1, x2, y2], fill=255)
    elif shape == "ellipse":
        draw.ellipse([x1, y1, x2, y2], fill=255)
    
    return mask

def show_edit_interface(api_key):
    """Show the working edit interface"""
    
    st.write("✏️ **Reliable Image Editing Suite**")
    st.write("🎯 **Multiple masking options that actually work!**")
    
    # Image upload
    uploaded_file = st.file_uploader(
        "Upload image to edit:",
        type=['png', 'jpg', 'jpeg'],
        help="Upload the image you want to edit"
    )
    
    if uploaded_file is not None:
        original_image = Image.open(uploaded_file)
        
        # Main editing tools
        edit_tool = st.selectbox(
            "Choose editing tool:",
            [
                "🗑️ Remove Background",
                "🎨 Area-Based Inpainting",
                "📐 Coordinate Inpainting", 
                "🖼️ Outpainting"
            ],
            help="Select the editing operation"
        )
        
        st.markdown("---")
        
        if edit_tool == "🗑️ Remove Background":
            show_background_removal(api_key, original_image)
        elif edit_tool == "🎨 Area-Based Inpainting":
            show_area_inpainting(api_key, original_image)
        elif edit_tool == "📐 Coordinate Inpainting":
            show_coordinate_inpainting(api_key, original_image)
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

def show_area_inpainting(api_key, image):
    """Show area-based inpainting with sliders"""
    st.subheader("🎨 Area-Based Inpainting")
    st.write("📐 **Define the exact area you want to edit using sliders**")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.write("**📷 Original Image**")
        st.image(image, caption=f"Size: {image.size[0]}x{image.size[1]}")
    
    # Area definition
    st.write("**📐 Define Area to Edit (as % of image):**")
    
    col_x, col_y = st.columns(2)
    
    with col_x:
        x1_pct = st.slider("Left edge %", 0, 100, 20, key="area_x1")
        x2_pct = st.slider("Right edge %", 0, 100, 80, key="area_x2")
        
    with col_y:
        y1_pct = st.slider("Top edge %", 0, 100, 20, key="area_y1")
        y2_pct = st.slider("Bottom edge %", 0, 100, 80, key="area_y2")
    
    # Shape selection
    shape = st.selectbox("Mask shape:", ["rectangle", "ellipse"], key="area_shape")
    
    # Create and show preview
    if st.button("🔍 Preview Mask", key="preview_area_mask"):
        mask = create_area_mask(image, x1_pct, y1_pct, x2_pct, y2_pct, shape)
        
        # Show mask preview
        mask_preview = Image.new('RGBA', image.size, (0, 0, 0, 0))
        mask_preview.paste((255, 0, 0, 128), mask=mask)
        preview_combined = Image.alpha_composite(image.convert('RGBA'), mask_preview)
        
        st.write("**🎯 Preview - Red area will be edited:**")
        st.image(preview_combined, width=400)
        
        # Store mask in session state
        st.session_state.current_mask = mask
        st.success("✅ Mask created! Now enter your prompt and apply inpainting.")
    
    # Prompt
    prompt = st.text_area(
        "What should appear in the selected area:",
        placeholder="beautiful flowers, blue sky, modern building...",
        help="Describe what you want to generate in the selected area",
        key="area_prompt"
    )
    
    # Apply inpainting
    if st.button("🎨 Apply Area Inpainting", type="primary", key="apply_area_inpainting"):
        if prompt.strip() and 'current_mask' in st.session_state:
            with st.spinner("🎨 Applying inpainting..."):
                result = inpaint_image(api_key, image, st.session_state.current_mask, prompt)
                if result:
                    show_result(result, f"Area inpainted: {prompt[:30]}...", "area_inpainted.png", col2)
        elif not prompt.strip():
            st.warning("Please enter a prompt.")
        else:
            st.warning("Please create a mask first by clicking 'Preview Mask'.")

def show_coordinate_inpainting(api_key, image):
    """Show coordinate-based inpainting"""
    st.subheader("📐 Coordinate Inpainting")
    st.write("🎯 **Click to add points, then paint around them**")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.write("**📷 Original Image**")
        st.image(image, caption=f"Size: {image.size[0]}x{image.size[1]}")
    
    # Initialize coordinates in session state
    if 'mask_coordinates' not in st.session_state:
        st.session_state.mask_coordinates = []
    
    # Coordinate input
    st.write("**📍 Add Points to Paint Around:**")
    
    col_coord, col_brush = st.columns(2)
    
    with col_coord:
        # Manual coordinate input
        x_coord = st.number_input("X coordinate (pixels):", 0, image.size[0], image.size[0]//2, key="x_coord")
        y_coord = st.number_input("Y coordinate (pixels):", 0, image.size[1], image.size[1]//2, key="y_coord")
        
        if st.button("➕ Add Point", key="add_coord"):
            st.session_state.mask_coordinates.append((x_coord, y_coord))
            st.success(f"Added point at ({x_coord}, {y_coord})")
    
    with col_brush:
        brush_size = st.slider("Brush size (pixels):", 10, 100, 40, key="coord_brush")
        
        if st.button("🗑️ Clear All Points", key="clear_coords"):
            st.session_state.mask_coordinates = []
            st.success("Cleared all points")
    
    # Show current points
    if st.session_state.mask_coordinates:
        st.write(f"**Current points:** {len(st.session_state.mask_coordinates)} points added")
        for i, (x, y) in enumerate(st.session_state.mask_coordinates):
            st.write(f"Point {i+1}: ({x}, {y})")
    
    # Create mask preview
    if st.button("🔍 Preview Coordinate Mask", key="preview_coord_mask"):
        if st.session_state.mask_coordinates:
            mask = create_coordinate_mask(image, st.session_state.mask_coordinates, brush_size)
            
            # Show mask preview
            mask_preview = Image.new('RGBA', image.size, (0, 0, 0, 0))
            mask_preview.paste((255, 0, 0, 128), mask=mask)
            preview_combined = Image.alpha_composite(image.convert('RGBA'), mask_preview)
            
            st.write("**🎯 Preview - Red areas will be edited:**")
            st.image(preview_combined, width=400)
            
            # Store mask
            st.session_state.current_coord_mask = mask
            st.success("✅ Coordinate mask created!")
        else:
            st.warning("Please add some points first.")
    
    # Prompt
    prompt = st.text_area(
        "What should appear at the marked points:",
        placeholder="flowers, people, objects, decorations...",
        help="Describe what you want to generate at the marked coordinates",
        key="coord_prompt"
    )
    
    # Apply inpainting
    if st.button("🎨 Apply Coordinate Inpainting", type="primary", key="apply_coord_inpainting"):
        if prompt.strip() and 'current_coord_mask' in st.session_state:
            with st.spinner("🎨 Applying coordinate inpainting..."):
                result = inpaint_image(api_key, image, st.session_state.current_coord_mask, prompt)
                if result:
                    show_result(result, f"Coordinate inpainted: {prompt[:30]}...", "coord_inpainted.png", col2)
        elif not prompt.strip():
            st.warning("Please enter a prompt.")
        else:
            st.warning("Please create a coordinate mask first.")

def show_outpainting(api_key, image):
    """Show outpainting interface"""
    st.subheader("🖼️ Outpainting")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.write("**📷 Original Image**")
        st.image(image, caption=f"Size: {image.size[0]}x{image.size[1]}")
    
    col_dir, col_size = st.columns(2)
    
    with col_dir:
        direction = st.selectbox(
            "Direction:",
            ["up", "down", "left", "right", "all"],
            format_func=lambda x: f"⬆️⬇️⬅️➡️🔄"[["up", "down", "left", "right", "all"].index(x)] + f" {x.title()}"
        )
    
    with col_size:
        pixels = st.selectbox("Extension:", [32, 64, 96, 128], index=1)
    
    prompt = st.text_area(
        "Extension description:",
        placeholder="continue the landscape, more sky, ocean waves...",
        height=60
    )
    
    if st.button("🖼️ Extend Image", type="primary") and prompt.strip():
        with st.spinner("🖼️ Extending..."):
            result = outpaint_image(api_key, image, prompt, direction, pixels)
            if result:
                show_result(result, f"Extended {direction}", "outpainted.png", col2)

def show_result(result_image, caption, filename, column):
    """Helper function to display results"""
    with column:
        st.subheader("✨ Result")
        st.image(result_image, caption=caption)
        
        buf = io.BytesIO()
        result_image.save(buf, format="PNG")
        st.download_button(
            "📥 Download",
            data=buf.getvalue(),
            file_name=filename,
            mime="image/png",
            use_container_width=True
        )
