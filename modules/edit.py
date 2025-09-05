import streamlit as st
import requests
import io
from PIL import Image, ImageDraw
import numpy as np

# Try to import drawable canvas, fallback if not available
try:
    from streamlit_drawable_canvas import st_canvas
    CANVAS_AVAILABLE = True
except ImportError:
    CANVAS_AVAILABLE = False
    st.warning("🔧 Interactive drawing not available. Using preset masks instead.")

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

def create_preset_mask(image, mask_type):
    """Create preset masks for inpainting"""
    width, height = image.size
    mask = Image.new('L', (width, height), 0)  # Black background
    draw = ImageDraw.Draw(mask)
    
    if mask_type == "center_circle":
        center_x, center_y = width // 2, height // 2
        radius = min(width, height) // 6
        draw.ellipse([center_x - radius, center_y - radius, 
                     center_x + radius, center_y + radius], fill=255)
    
    elif mask_type == "center_square":
        size = min(width, height) // 4
        x1 = (width - size) // 2
        y1 = (height - size) // 2
        draw.rectangle([x1, y1, x1 + size, y1 + size], fill=255)
    
    elif mask_type == "top_half":
        draw.rectangle([0, 0, width, height // 2], fill=255)
    
    elif mask_type == "bottom_half":
        draw.rectangle([0, height // 2, width, height], fill=255)
    
    elif mask_type == "left_third":
        draw.rectangle([0, 0, width // 3, height], fill=255)
    
    elif mask_type == "right_third":
        draw.rectangle([2 * width // 3, 0, width, height], fill=255)
    
    elif mask_type == "face_area":
        # Approximate face area (top center)
        face_width = width // 3
        face_height = height // 3
        x1 = (width - face_width) // 2
        y1 = height // 6
        draw.ellipse([x1, y1, x1 + face_width, y1 + face_height], fill=255)
    
    return mask

def show_edit_interface(api_key):
    """Show the edit interface with fallback options"""
    
    st.write("✏️ **AI Image Editing Suite**")
    
    if CANVAS_AVAILABLE:
        st.success("🎨 Interactive drawing enabled!")
    else:
        st.info("🎯 Using preset mask areas (interactive drawing unavailable)")
    
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
                "🎨 Inpainting",
                "🖼️ Outpainting"
            ],
            help="Select the editing operation"
        )
        
        st.markdown("---")
        
        if edit_tool == "🗑️ Remove Background":
            show_background_removal(api_key, original_image)
        elif edit_tool == "🎨 Inpainting":
            if CANVAS_AVAILABLE:
                show_interactive_inpainting(api_key, original_image)
            else:
                show_preset_inpainting(api_key, original_image)
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

def show_interactive_inpainting(api_key, image):
    """Show interactive inpainting with drawable canvas"""
    st.subheader("🎨 Interactive Inpainting")
    st.write("🖌️ **Paint over the areas you want to edit**")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.write("**📷 Original Image**")
        st.image(image, caption=f"Size: {image.size[0]}x{image.size[1]}")
    
    # Resize for canvas
    max_size = 500
    if max(image.size) > max_size:
        ratio = max_size / max(image.size)
        canvas_width = int(image.size[0] * ratio)
        canvas_height = int(image.size[1] * ratio)
        display_image = image.resize((canvas_width, canvas_height))
    else:
        canvas_width, canvas_height = image.size
        display_image = image
    
    # Drawing controls
    col_brush, col_mode = st.columns(2)
    with col_brush:
        brush_size = st.slider("Brush size:", 10, 50, 25)
    with col_mode:
        drawing_mode = st.selectbox("Mode:", ["freedraw", "rect", "circle"], index=0)
    
    # Canvas
    canvas_result = st_canvas(
        fill_color="rgba(255, 255, 255, 0.8)",
        stroke_width=brush_size,
        stroke_color="#FF0000",
        background_color="#000000",
        background_image=display_image,
        update_streamlit=True,
        height=canvas_height,
        width=canvas_width,
        drawing_mode=drawing_mode,
        key="canvas",
    )
    
    # Prompt
    prompt = st.text_area(
        "What should appear in painted areas:",
        placeholder="beautiful flowers, blue sky, person smiling...",
        height=60
    )
    
    # Process
    if st.button("🎨 Apply Inpainting", type="primary") and prompt.strip():
        if canvas_result.image_data is not None:
            mask_array = canvas_result.image_data[:, :, 3]
            if np.any(mask_array > 0):
                mask_pil = Image.fromarray(mask_array, mode='L')
                mask_resized = mask_pil.resize(image.size, Image.NEAREST)
                
                with st.spinner("🎨 Inpainting..."):
                    result = inpaint_image(api_key, image, mask_resized, prompt)
                    if result:
                        show_result(result, f"Inpainted: {prompt[:30]}...", "inpainted.png", col2)
            else:
                st.warning("Please paint some areas first!")

def show_preset_inpainting(api_key, image):
    """Show preset mask inpainting (fallback)"""
    st.subheader("🎨 Preset Area Inpainting")
    st.write("🎯 **Choose a preset area to edit**")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.write("**📷 Original Image**")
        st.image(image, caption=f"Size: {image.size[0]}x{image.size[1]}")
    
    # Preset mask options
    mask_options = {
        "🔵 Center Circle": "center_circle",
        "⬜ Center Square": "center_square", 
        "⬆️ Top Half": "top_half",
        "⬇️ Bottom Half": "bottom_half",
        "⬅️ Left Third": "left_third",
        "➡️ Right Third": "right_third",
        "👤 Face Area": "face_area"
    }
    
    selected_mask = st.selectbox(
        "Select area to edit:",
        list(mask_options.keys()),
        help="Choose which part of the image to modify"
    )
    
    # Show mask preview
    mask_key = mask_options[selected_mask]
    preview_mask = create_preset_mask(image, mask_key)
    
    # Create preview overlay
    mask_preview = Image.new('RGBA', image.size, (0, 0, 0, 0))
    mask_preview.paste((255, 0, 0, 128), mask=preview_mask)
    preview_combined = Image.alpha_composite(image.convert('RGBA'), mask_preview)
    
    st.write("**🎯 Preview (red = will be edited):**")
    st.image(preview_combined, width=400)
    
    # Prompt
    prompt = st.text_area(
        "What should appear in the selected area:",
        placeholder="beautiful flowers, blue sky, modern building...",
        height=60
    )
    
    # Process
    if st.button("🎨 Apply Inpainting", type="primary") and prompt.strip():
        mask = create_preset_mask(image, mask_key)
        with st.spinner("🎨 Inpainting..."):
            result = inpaint_image(api_key, image, mask, prompt)
            if result:
                show_result(result, f"Inpainted: {prompt[:30]}...", "inpainted.png", col2)

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
        "What should appear in extended area:",
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
