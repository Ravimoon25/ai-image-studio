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

def extract_mask_from_black_areas(original_image, painted_image):
    """Extract white mask from black painted areas"""
    # Convert images to arrays
    original_array = np.array(original_image.convert('RGB'))
    painted_array = np.array(painted_image.convert('RGB'))
    
    # Find black areas (where user painted)
    # Black areas are where RGB values are very low
    black_threshold = 30  # Adjust if needed
    
    # Check where painted image is significantly darker than original
    diff = np.sum(original_array, axis=2) - np.sum(painted_array, axis=2)
    black_areas = diff > 100  # Areas that became much darker
    
    # Also check for pure black areas
    pure_black = np.all(painted_array < black_threshold, axis=2)
    
    # Combine both conditions
    mask_areas = black_areas | pure_black
    
    # Create white mask (white = inpaint, black = keep original)
    mask_array = np.zeros(original_image.size[::-1], dtype=np.uint8)
    mask_array[mask_areas] = 255
    
    # Convert to PIL image
    mask_image = Image.fromarray(mask_array, mode='L')
    
    return mask_image

def inpaint_with_black_painted_image(api_key, original_image, painted_image, prompt):
    """Inpaint using black painted areas"""
    
    # Extract mask from black painted areas
    mask = extract_mask_from_black_areas(original_image, painted_image)
    
    # Use standard inpaint API
    url = "https://api.stability.ai/v2beta/stable-image/edit/inpaint"
    
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Accept": "image/*"
    }
    
    # Convert images to bytes
    img_byte_arr = io.BytesIO()
    original_image.save(img_byte_arr, format='PNG')
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
            return Image.open(io.BytesIO(response.content)), mask
        else:
            st.error(f"Error: {response.status_code} - {response.text}")
            return None, None
    except Exception as e:
        st.error(f"Request failed: {str(e)}")
        return None, None

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

def paint_black_areas(image, areas, brush_size=30):
    """Paint black areas on image based on coordinates"""
    painted_image = image.copy()
    draw = ImageDraw.Draw(painted_image)
    
    for area in areas:
        if area['type'] == 'circle':
            x, y = area['center']
            radius = area.get('radius', brush_size // 2)
            draw.ellipse([x - radius, y - radius, x + radius, y + radius], fill=(0, 0, 0))
        elif area['type'] == 'rectangle':
            x1, y1, x2, y2 = area['coords']
            draw.rectangle([x1, y1, x2, y2], fill=(0, 0, 0))
        elif area['type'] == 'brush_stroke':
            points = area['points']
            width = area.get('width', brush_size)
            for i in range(len(points) - 1):
                draw.line([points[i], points[i + 1]], fill=(0, 0, 0), width=width)
    
    return painted_image

def show_edit_interface(api_key):
    """Show the black painting edit interface"""
    
    st.write("✏️ **Black Paint Image Editing**")
    st.write("🖤 **Paint black areas where you want changes - intuitive and simple!**")
    
    # Image upload
    uploaded_file = st.file_uploader(
        "Upload image to edit:",
        type=['png', 'jpg', 'jpeg'],
        help="Upload the image you want to edit"
    )
    
    if uploaded_file is not None:
        original_image = Image.open(uploaded_file)
        
        # Initialize session state for painted areas
        if 'painted_areas' not in st.session_state:
            st.session_state.painted_areas = []
        
        # Main editing tools
        edit_tool = st.selectbox(
            "Choose editing tool:",
            [
                "🗑️ Remove Background",
                "🖤 Black Paint Inpainting",
                "🖼️ Outpainting"
            ],
            help="Select the editing operation"
        )
        
        st.markdown("---")
        
        if edit_tool == "🗑️ Remove Background":
            show_background_removal(api_key, original_image)
        elif edit_tool == "🖤 Black Paint Inpainting":
            show_black_paint_inpainting(api_key, original_image)
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

def show_black_paint_inpainting(api_key, image):
    """Show black paint inpainting interface"""
    st.subheader("🖤 Black Paint Inpainting")
    st.write("🎯 **Paint black areas where you want changes - what you see is what gets edited!**")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.write("**📷 Original Image**")
        st.image(image, caption=f"Size: {image.size[0]}x{image.size[1]}")
    
    # Painting tools
    st.subheader("🎨 Painting Tools")
    
    tool_type = st.selectbox(
        "Painting tool:",
        ["🖌️ Click to Paint", "📐 Rectangle", "⭕ Circle", "📁 Upload Black Painted Image"],
        help="Choose how to create black areas"
    )
    
    if tool_type == "📁 Upload Black Painted Image":
        # Direct upload of painted image
        st.write("**Upload your image with black painted areas:**")
        painted_file = st.file_uploader(
            "Upload painted image:",
            type=['png', 'jpg', 'jpeg'],
            help="Upload the same image but with black areas painted where you want changes",
            key="painted_upload"
        )
        
        if painted_file is not None:
            painted_image = Image.open(painted_file)
            
            st.write("**🖤 Your Painted Image:**")
            st.image(painted_image, caption="Image with black painted areas", width=400)
            
            # Prompt
            prompt = st.text_area(
                "What should appear in the black areas:",
                placeholder="beautiful flowers, blue sky, modern building...",
                help="Describe what should replace the black painted areas",
                key="upload_prompt"
            )
            
            if st.button("🎨 Apply Inpainting", type="primary", key="apply_upload_inpainting"):
                if prompt.strip():
                    with st.spinner("🎨 Processing black painted areas..."):
                        result, mask = inpaint_with_black_painted_image(api_key, image, painted_image, prompt)
                        if result:
                            with col2:
                                st.write("**✨ Result**")
                                st.image(result, caption="Inpainting complete!")
                                
                                # Show extracted mask
                                st.write("**🎭 Extracted Mask:**")
                                st.image(mask, caption="White = inpainted areas")
                                
                                # Download
                                buf = io.BytesIO()
                                result.save(buf, format="PNG")
                                st.download_button(
                                    "📥 Download Result",
                                    data=buf.getvalue(),
                                    file_name="black_paint_result.png",
                                    mime="image/png"
                                )
                else:
                    st.warning("Please enter a prompt describing what should appear in the black areas.")
    
    else:
        # Interactive painting tools
        if tool_type == "🖌️ Click to Paint":
            brush_size = st.slider("Brush size:", 10, 100, 30, key="brush_size")
            
            st.write("**Click coordinates to paint black circles:**")
            
            col_x, col_y = st.columns(2)
            with col_x:
                x_coord = st.number_input("X coordinate:", 0, image.size[0], image.size[0]//2, key="paint_x")
            with col_y:
                y_coord = st.number_input("Y coordinate:", 0, image.size[1], image.size[1]//2, key="paint_y")
            
            if st.button("🖤 Paint Black Circle", key="paint_circle"):
                area = {
                    'type': 'circle',
                    'center': (x_coord, y_coord),
                    'radius': brush_size // 2
                }
                st.session_state.painted_areas.append(area)
                st.success(f"Added black circle at ({x_coord}, {y_coord})")
        
        elif tool_type == "📐 Rectangle":
            st.write("**Define rectangle to paint black:**")
            
            col_rect = st.columns(4)
            with col_rect[0]:
                rect_x1 = st.number_input("Left:", 0, image.size[0], 0, key="rect_x1")
            with col_rect[1]:
                rect_y1 = st.number_input("Top:", 0, image.size[1], 0, key="rect_y1")
            with col_rect[2]:
                rect_x2 = st.number_input("Right:", 0, image.size[0], 100, key="rect_x2")
            with col_rect[3]:
                rect_y2 = st.number_input("Bottom:", 0, image.size[1], 100, key="rect_y2")
            
            if st.button("🖤 Paint Black Rectangle", key="paint_rect"):
                area = {
                    'type': 'rectangle',
                    'coords': (rect_x1, rect_y1, rect_x2, rect_y2)
                }
                st.session_state.painted_areas.append(area)
                st.success(f"Added black rectangle")
        
        elif tool_type == "⭕ Circle":
            st.write("**Define circle to paint black:**")
            
            col_circle = st.columns(3)
            with col_circle[0]:
                circle_x = st.number_input("Center X:", 0, image.size[0], image.size[0]//2, key="circle_x")
            with col_circle[1]:
                circle_y = st.number_input("Center Y:", 0, image.size[1], image.size[1]//2, key="circle_y")
            with col_circle[2]:
                circle_radius = st.number_input("Radius:", 10, 200, 50, key="circle_radius")
            
            if st.button("🖤 Paint Black Circle", key="paint_big_circle"):
                area = {
                    'type': 'circle',
                    'center': (circle_x, circle_y),
                    'radius': circle_radius
                }
                st.session_state.painted_areas.append(area)
                st.success(f"Added black circle")
        
        # Show current painted image
        if st.session_state.painted_areas:
            painted_image = paint_black_areas(image, st.session_state.painted_areas)
            
            st.write("**🖤 Current Painted Image:**")
            st.image(painted_image, caption=f"Black areas will be replaced ({len(st.session_state.painted_areas)} areas painted)")
            
            # Clear button
            if st.button("🗑️ Clear All Black Paint", key="clear_paint"):
                st.session_state.painted_areas = []
                st.success("Cleared all black paint")
                st.rerun()
            
            # Prompt
            prompt = st.text_area(
                "What should appear in the black areas:",
                placeholder="beautiful flowers, blue sky, modern building...",
                help="Describe what should replace the black painted areas",
                key="paint_prompt"
            )
            
            # Apply inpainting
            if st.button("🎨 Apply Black Paint Inpainting", type="primary", key="apply_paint_inpainting"):
                if prompt.strip():
                    with st.spinner("🎨 Processing black painted areas..."):
                        result, mask = inpaint_with_black_painted_image(api_key, image, painted_image, prompt)
                        if result:
                            with col2:
                                st.write("**✨ Result**")
                                st.image(result, caption="Inpainting complete!")
                                
                                # Show extracted mask
                                st.write("**🎭 Extracted Mask:**")
                                st.image(mask, caption="White = inpainted areas")
                                
                                # Download
                                buf = io.BytesIO()
                                result.save(buf, format="PNG")
                                st.download_button(
                                    "📥 Download Result",
                                    data=buf.getvalue(),
                                    file_name="black_paint_result.png",
                                    mime="image/png"
                                )
                else:
                    st.warning("Please enter a prompt describing what should appear in the black areas.")
        else:
            st.info("👆 Use the tools above to paint black areas on your image")

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
