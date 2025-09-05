import streamlit as st
import requests
import io
from PIL import Image
import numpy as np
import base64
from streamlit.components.v1 import html

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

def image_to_base64(image):
    """Convert PIL image to base64 string"""
    buffered = io.BytesIO()
    image.save(buffered, format="PNG")
    img_str = base64.b64encode(buffered.getvalue()).decode()
    return f"data:image/png;base64,{img_str}"

def create_drawing_canvas(image, canvas_id="drawingCanvas"):
    """Create HTML5 Canvas for free drawing"""
    
    # Convert image to base64
    img_b64 = image_to_base64(image)
    
    # Scale image if too large
    max_size = 600
    if max(image.size) > max_size:
        ratio = max_size / max(image.size)
        canvas_width = int(image.size[0] * ratio)
        canvas_height = int(image.size[1] * ratio)
    else:
        canvas_width, canvas_height = image.size
    
    html_code = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <style>
            #canvasContainer {{
                position: relative;
                display: inline-block;
                border: 2px solid #ddd;
                border-radius: 8px;
                background: #f9f9f9;
            }}
            #backgroundCanvas, #drawingCanvas {{
                position: absolute;
                top: 0;
                left: 0;
                cursor: crosshair;
            }}
            #backgroundCanvas {{
                z-index: 1;
            }}
            #drawingCanvas {{
                z-index: 2;
            }}
            .controls {{
                margin: 10px 0;
                padding: 10px;
                background: #f0f2f6;
                border-radius: 5px;
            }}
            button {{
                margin: 5px;
                padding: 8px 16px;
                border: none;
                border-radius: 4px;
                cursor: pointer;
                font-size: 14px;
            }}
            .primary-btn {{
                background: #ff4b4b;
                color: white;
            }}
            .secondary-btn {{
                background: #f0f2f6;
                color: #333;
                border: 1px solid #ddd;
            }}
            input[type="range"] {{
                width: 100px;
            }}
        </style>
    </head>
    <body>
        <div class="controls">
            <label>🖌️ Brush Size: </label>
            <input type="range" id="brushSize" min="5" max="50" value="20" oninput="updateBrushSize()">
            <span id="brushSizeValue">20</span>px
            
            <button class="secondary-btn" onclick="clearCanvas()">🗑️ Clear</button>
            <button class="secondary-btn" onclick="undoLast()">↶ Undo</button>
            <button class="primary-btn" onclick="downloadMask()">💾 Generate Mask</button>
        </div>
        
        <div id="canvasContainer">
            <canvas id="backgroundCanvas" width="{canvas_width}" height="{canvas_height}"></canvas>
            <canvas id="drawingCanvas" width="{canvas_width}" height="{canvas_height}"></canvas>
        </div>
        
        <div style="margin-top: 10px;">
            <p>🎯 <strong>Instructions:</strong> Paint over the areas you want to edit. The mask will be automatically generated.</p>
        </div>

        <script>
            let isDrawing = false;
            let brushSize = 20;
            let paths = [];
            let currentPath = [];
            
            const backgroundCanvas = document.getElementById('backgroundCanvas');
            const drawingCanvas = document.getElementById('drawingCanvas');
            const backgroundCtx = backgroundCanvas.getContext('2d');
            const drawingCtx = drawingCanvas.getContext('2d');
            
            // Load background image
            const img = new Image();
            img.onload = function() {{
                backgroundCtx.drawImage(img, 0, 0, {canvas_width}, {canvas_height});
            }};
            img.src = '{img_b64}';
            
            // Set up drawing context
            drawingCtx.strokeStyle = 'rgba(255, 0, 0, 0.7)';
            drawingCtx.lineWidth = brushSize;
            drawingCtx.lineCap = 'round';
            drawingCtx.lineJoin = 'round';
            
            // Mouse events
            drawingCanvas.addEventListener('mousedown', startDrawing);
            drawingCanvas.addEventListener('mousemove', draw);
            drawingCanvas.addEventListener('mouseup', stopDrawing);
            drawingCanvas.addEventListener('mouseout', stopDrawing);
            
            // Touch events for mobile
            drawingCanvas.addEventListener('touchstart', function(e) {{
                e.preventDefault();
                const touch = e.touches[0];
                const rect = drawingCanvas.getBoundingClientRect();
                const x = touch.clientX - rect.left;
                const y = touch.clientY - rect.top;
                startDrawing({{offsetX: x, offsetY: y}});
            }});
            
            drawingCanvas.addEventListener('touchmove', function(e) {{
                e.preventDefault();
                const touch = e.touches[0];
                const rect = drawingCanvas.getBoundingClientRect();
                const x = touch.clientX - rect.left;
                const y = touch.clientY - rect.top;
                draw({{offsetX: x, offsetY: y}});
            }});
            
            drawingCanvas.addEventListener('touchend', function(e) {{
                e.preventDefault();
                stopDrawing();
            }});
            
            function startDrawing(e) {{
                isDrawing = true;
                currentPath = [];
                currentPath.push({{x: e.offsetX, y: e.offsetY}});
                
                drawingCtx.beginPath();
                drawingCtx.moveTo(e.offsetX, e.offsetY);
            }}
            
            function draw(e) {{
                if (!isDrawing) return;
                
                currentPath.push({{x: e.offsetX, y: e.offsetY}});
                
                drawingCtx.lineTo(e.offsetX, e.offsetY);
                drawingCtx.stroke();
            }}
            
            function stopDrawing() {{
                if (isDrawing) {{
                    isDrawing = false;
                    paths.push([...currentPath]);
                }}
            }}
            
            function updateBrushSize() {{
                brushSize = document.getElementById('brushSize').value;
                document.getElementById('brushSizeValue').textContent = brushSize;
                drawingCtx.lineWidth = brushSize;
            }}
            
            function clearCanvas() {{
                drawingCtx.clearRect(0, 0, drawingCanvas.width, drawingCanvas.height);
                paths = [];
            }}
            
            function undoLast() {{
                if (paths.length > 0) {{
                    paths.pop();
                    redrawCanvas();
                }}
            }}
            
            function redrawCanvas() {{
                drawingCtx.clearRect(0, 0, drawingCanvas.width, drawingCanvas.height);
                
                for (let path of paths) {{
                    if (path.length > 0) {{
                        drawingCtx.beginPath();
                        drawingCtx.moveTo(path[0].x, path[0].y);
                        
                        for (let i = 1; i < path.length; i++) {{
                            drawingCtx.lineTo(path[i].x, path[i].y);
                        }}
                        drawingCtx.stroke();
                    }}
                }}
            }}
            
            function downloadMask() {{
                // Create mask canvas (white drawing on black background)
                const maskCanvas = document.createElement('canvas');
                maskCanvas.width = {canvas_width};
                maskCanvas.height = {canvas_height};
                const maskCtx = maskCanvas.getContext('2d');
                
                // Black background
                maskCtx.fillStyle = 'black';
                maskCtx.fillRect(0, 0, maskCanvas.width, maskCanvas.height);
                
                // White strokes
                maskCtx.strokeStyle = 'white';
                maskCtx.lineWidth = brushSize;
                maskCtx.lineCap = 'round';
                maskCtx.lineJoin = 'round';
                
                // Draw all paths
                for (let path of paths) {{
                    if (path.length > 0) {{
                        maskCtx.beginPath();
                        maskCtx.moveTo(path[0].x, path[0].y);
                        
                        for (let i = 1; i < path.length; i++) {{
                            maskCtx.lineTo(path[i].x, path[i].y);
                        }}
                        maskCtx.stroke();
                    }}
                }}
                
                // Convert to base64 and send to Streamlit
                const maskDataUrl = maskCanvas.toDataURL('image/png');
                
                // Send mask data to parent window
                window.parent.postMessage({{
                    type: 'mask_data',
                    data: maskDataUrl,
                    original_size: [{image.size[0]}, {image.size[1]}],
                    canvas_size: [{canvas_width}, {canvas_height}]
                }}, '*');
                
                alert('Mask generated! You can now apply inpainting.');
            }}
        </script>
    </body>
    </html>
    """
    
    return html_code, canvas_width, canvas_height

def show_edit_interface(api_key):
    """Show the custom interactive edit interface"""
    
    st.write("✏️ **Professional Interactive Image Editing**")
    st.write("🖌️ **Draw freely anywhere on your image!**")
    
    # Image upload
    uploaded_file = st.file_uploader(
        "Upload image to edit:",
        type=['png', 'jpg', 'jpeg'],
        help="Upload the image you want to edit"
    )
    
    if uploaded_file is not None:
        original_image = Image.open(uploaded_file)
        
        # Store in session state
        if 'editing_image' not in st.session_state:
            st.session_state.editing_image = original_image
        
        # Main editing tools
        edit_tool = st.selectbox(
            "Choose editing tool:",
            [
                "🗑️ Remove Background",
                "🎨 Free Drawing Inpainting", 
                "🖼️ Outpainting"
            ],
            help="Select the editing operation"
        )
        
        st.markdown("---")
        
        if edit_tool == "🗑️ Remove Background":
            show_background_removal(api_key, original_image)
        elif edit_tool == "🎨 Free Drawing Inpainting":
            show_free_drawing_inpainting(api_key, original_image)
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

def show_free_drawing_inpainting(api_key, image):
    """Show free drawing inpainting interface"""
    st.subheader("🎨 Free Drawing Inpainting")
    st.write("🖌️ **Draw exactly where you want to edit - complete freedom!**")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.write("**🎨 Interactive Drawing Canvas**")
        
        # Create the HTML5 canvas
        html_code, canvas_width, canvas_height = create_drawing_canvas(image)
        
        # Display the interactive canvas
        components_html = html(html_code, height=canvas_height + 150, scrolling=False)
    
    with col2:
        st.write("**📷 Original Image**")
        st.image(image, caption=f"Size: {image.size[0]}x{image.size[1]}", width=300)
        
        st.markdown("---")
        
        # Prompt for inpainting
        st.write("**📝 Inpainting Prompt**")
        prompt = st.text_area(
            "What should appear in the drawn areas:",
            placeholder="beautiful flowers, blue sky, person smiling, modern building...",
            help="Describe what you want to generate in the areas you drew",
            height=100
        )
        
        # File uploader for mask (alternative method)
        st.write("**🎭 Or Upload Mask Manually**")
        uploaded_mask = st.file_uploader(
            "Upload a mask image (optional):",
            type=['png', 'jpg', 'jpeg'],
            help="White areas = edit, Black areas = keep original"
        )
        
        # Apply inpainting button
        if st.button("🎨 Apply Inpainting", type="primary", use_container_width=True):
            if prompt.strip():
                if uploaded_mask is not None:
                    # Use uploaded mask
                    mask_image = Image.open(uploaded_mask).convert('L')
                    mask_resized = mask_image.resize(image.size)
                    
                    with st.spinner("🎨 Applying inpainting with uploaded mask..."):
                        result = inpaint_image(api_key, image, mask_resized, prompt)
                        if result:
                            st.success("✅ Inpainting completed!")
                            st.image(result, caption="Inpainting result")
                            
                            # Download button
                            buf = io.BytesIO()
                            result.save(buf, format="PNG")
                            st.download_button(
                                "📥 Download Result",
                                data=buf.getvalue(),
                                file_name="inpainted_result.png",
                                mime="image/png"
                            )
                else:
                    st.info("💡 Use the drawing canvas on the left to create a mask, then click 'Generate Mask' in the canvas, then try this button again.")
            else:
                st.warning("Please enter a prompt describing what should appear in the drawn areas.")

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
    
    prompt = st.text_area(
        "What should appear in the extended area:",
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
