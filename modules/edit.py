import streamlit as st
import requests
import io
from PIL import Image, ImageDraw
import numpy as np
from streamlit_drawable_canvas import st_canvas

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

def show_edit_interface(api_key):
    """Show the interactive edit interface"""
    
    st.write("✏️ **Interactive AI Image Editing**")
    st.write("🖌️ **Draw exactly where you want to edit!**")
    
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
                "🎨 Interactive Inpainting",
                "🖼️ Outpainting - Extend Image"
            ],
            help="Select the editing operation"
        )
        
        st.markdown("---")
        
        if edit_tool == "🗑️ Remove Background":
            show_background_removal(api_key, original_image)
        elif edit_tool == "🎨 Interactive Inpainting":
            show_interactive_inpainting(api_key, original_image)
        elif edit_tool == "🖼️ Outpainting - Extend Image":
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
    st.write("🖌️ **Paint over the areas you want to edit, then describe what should appear there**")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.write("**📷 Original Image**")
        st.image(image, caption=f"Size: {image.size[0]}x{image.size[1]}")
    
    # Resize image for canvas if too large
    max_canvas_size = 600
    if image.size[0] > max_canvas_size or image.size[1] > max_canvas_size:
        ratio = min(max_canvas_size / image.size[0], max_canvas_size / image.size[1])
        canvas_width = int(image.size[0] * ratio)
        canvas_height = int(image.size[1] * ratio)
        display_image = image.resize((canvas_width, canvas_height))
    else:
        canvas_width, canvas_height = image.size
        display_image = image
    
    # Drawing tools
    st.subheader("🖌️ Drawing Tools")
    
    col_brush, col_mode = st.columns(2)
    
    with col_brush:
        brush_size = st.slider("Brush size:", 5, 50, 20, help="Size of the brush for painting")
        
    with col_mode:
        drawing_mode = st.selectbox(
            "Drawing mode:",
            ["freedraw", "line", "rect", "circle"],
            index=0,
            help="Choose how to draw the mask"
        )
    
    # Canvas for drawing mask
    st.write("**🎯 Paint the areas you want to edit:**")
    
    canvas_result = st_canvas(
        fill_color="rgba(255, 255, 255, 0.8)",  # Semi-transparent white
        stroke_width=brush_size,
        stroke_color="#FF0000",  # Red brush
        background_color="#000000",  # Black background
        background_image=display_image,
        update_streamlit=True,
        height=canvas_height,
        width=canvas_width,
        drawing_mode=drawing_mode,
        point_display_radius=0,
        key="inpaint_canvas",
    )
    
    # Clear canvas button
    if st.button("🗑️ Clear Mask", help="Clear all painted areas"):
        st.rerun()
    
    # Inpainting prompt
    st.subheader("📝 What to Generate")
    
    # Quick prompt suggestions
    st.write("**💡 Quick Ideas:**")
    prompt_suggestions = [
        "beautiful flowers", "blue sky with clouds", "modern building", 
        "person smiling", "green grass", "ocean waves", "mountain landscape"
    ]
    
    prompt_cols = st.columns(4)
    selected_suggestion = None
    
    for i, suggestion in enumerate(prompt_suggestions):
        with prompt_cols[i % 4]:
            if st.button(f"💡 {suggestion}", key=f"suggestion_{i}"):
                selected_suggestion = suggestion
    
    # Main prompt input
    inpaint_prompt = st.text_area(
        "Describe what should appear in the painted areas:",
        value=selected_suggestion or "",
        placeholder="a beautiful sunset, a person wearing a blue shirt, flowers blooming, modern architecture...",
        help="Be specific about what you want to generate in the painted areas",
        height=80
    )
    
    # Inpaint button
    if st.button("🎨 Apply Inpainting", type="primary", use_container_width=True):
        if canvas_result.image_data is not None and inpaint_prompt.strip():
            # Extract mask from canvas
            mask_array = canvas_result.image_data[:, :, 3]  # Alpha channel
            
            # Check if mask has any painted areas
            if np.any(mask_array > 0):
                # Convert to PIL mask
                mask_pil = Image.fromarray(mask_array, mode='L')
                
                # Resize mask back to original image size
                mask_resized = mask_pil.resize(image.size, Image.NEAREST)
                
                # Show mask preview
                st.write("**🎯 Mask Preview:**")
                mask_preview = Image.new('RGBA', image.size, (0, 0, 0, 0))
                mask_preview.paste((255, 0, 0, 128), mask=mask_resized)
                preview_combined = Image.alpha_composite(
                    image.convert('RGBA'),
                    mask_preview
                )
                st.image(preview_combined, caption="Red areas will be inpainted", width=400)
                
                with st.spinner("🎨 Applying inpainting..."):
                    result = inpaint_image(api_key, image, mask_resized, inpaint_prompt)
                    
                    if result:
                        with col2:
                            show_result(result, f"Inpainted: {inpaint_prompt[:30]}...", "inpainted.png", col2)
            else:
                st.warning("⚠️ Please paint some areas on the image first!")
        elif not inpaint_prompt.strip():
            st.warning("⚠️ Please describe what should appear in the painted areas!")
        else:
            st.warning("⚠️ Please paint some areas on the image first!")

def show_outpainting(api_key, image):
    """Show outpainting interface"""
    st.subheader("🖼️ Outpainting - Extend Image")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.write("**📷 Original Image**")
        st.image(image, caption=f"Size: {image.size[0]}x{image.size[1]}")
    
    # Outpainting controls
    st.subheader("⚙️ Extension Settings")
    
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
            [32, 64, 96, 128, 160],
            format_func=lambda x: f"{x} pixels",
            index=1  # Default to 64
        )
    
    # Extension prompt with suggestions
    st.write("**💡 Extension Ideas:**")
    extension_suggestions = [
        "continue the landscape", "more ocean waves", "extend the sky", 
        "more forest trees", "continue the building", "expand the scene"
    ]
    
    ext_cols = st.columns(3)
    selected_ext_suggestion = None
    
    for i, suggestion in enumerate(extension_suggestions):
        with ext_cols[i % 3]:
            if st.button(f"💡 {suggestion}", key=f"ext_suggestion_{i}"):
                selected_ext_suggestion = suggestion
    
    extension_prompt = st.text_area(
        "What should appear in the extended area:",
        value=selected_ext_suggestion or "",
        placeholder="continue the landscape, more ocean, forest continuation, sky with clouds...",
        help="Describe what should be generated in the new expanded areas"
    )
    
    if st.button("🖼️ Extend Image", type="primary", use_container_width=True):
        if extension_prompt.strip():
            with st.spinner("🖼️ Extending image..."):
                result = outpaint_image(api_key, image, extension_prompt, direction, extension_size)
                if result:
                    # Show size comparison
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
        
        # Show comparison metrics
        if hasattr(result_image, 'size'):
            pixels = result_image.size[0] * result_image.size[1]
            st.caption(f"Result: {result_image.size[0]}×{result_image.size[1]} ({pixels:,} pixels)")
