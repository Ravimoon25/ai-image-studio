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

def replace_background(api_key, image, prompt):
    """Replace background using Stability AI API"""
    url = "https://api.stability.ai/v2beta/stable-image/edit/replace-background"
    
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

def search_and_replace(api_key, image, search_prompt, replace_prompt):
    """Search and replace using Stability AI API"""
    url = "https://api.stability.ai/v2beta/stable-image/edit/search-and-replace"
    
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Accept": "image/*"
    }
    
    img_byte_arr = io.BytesIO()
    image.save(img_byte_arr, format='PNG')
    img_byte_arr = img_byte_arr.getvalue()
    
    files = {
        "image": ("image.png", img_byte_arr, "image/png"),
        "search_prompt": (None, search_prompt),
        "replace_prompt": (None, replace_prompt),
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

def erase_object(api_key, image, object_prompt):
    """Erase object using Stability AI API"""
    url = "https://api.stability.ai/v2beta/stable-image/edit/erase"
    
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Accept": "image/*"
    }
    
    img_byte_arr = io.BytesIO()
    image.save(img_byte_arr, format='PNG')
    img_byte_arr = img_byte_arr.getvalue()
    
    files = {
        "image": ("image.png", img_byte_arr, "image/png"),
        "mask": (None, object_prompt),
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
    """Extract white mask from black painted areas (CORRECTED)"""
    original_array = np.array(original_image.convert('RGB'))
    painted_array = np.array(painted_image.convert('RGB'))
    
    # Find where user painted BLACK
    black_threshold = 50
    diff = np.sum(original_array, axis=2) - np.sum(painted_array, axis=2)
    black_areas = diff > 100  # Areas that became much darker
    pure_black = np.all(painted_array < black_threshold, axis=2)
    
    # Combine both conditions to find all black painted areas
    painted_black_areas = black_areas | pure_black
    
    # Create WHITE mask where user painted BLACK
    # (White in mask = inpaint these areas)
    mask_array = np.zeros(original_image.size[::-1], dtype=np.uint8)
    mask_array[painted_black_areas] = 255  # WHITE where user painted BLACK
    
    return Image.fromarray(mask_array, mode='L')

def inpaint_with_black_painted_image(api_key, original_image, painted_image, prompt):
    """Inpaint using black painted areas"""
    mask = extract_mask_from_black_areas(original_image, painted_image)
    
    url = "https://api.stability.ai/v2beta/stable-image/edit/inpaint"
    
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Accept": "image/*"
    }
    
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

def image_to_base64(image):
    """Convert PIL image to base64 string"""
    buffered = io.BytesIO()
    image.save(buffered, format="PNG")
    img_str = base64.b64encode(buffered.getvalue()).decode()
    return f"data:image/png;base64,{img_str}"

def create_black_painting_interface(image):
    """Create HTML/JS interface for black painting"""
    img_b64 = image_to_base64(image)
    
    # Scale image for canvas
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
            body {{ font-family: Arial, sans-serif; margin: 20px; }}
            .container {{ max-width: 800px; margin: 0 auto; }}
            .controls {{ 
                background: #f0f2f6; 
                padding: 15px; 
                border-radius: 8px; 
                margin-bottom: 15px;
                display: flex;
                flex-wrap: wrap;
                gap: 10px;
                align-items: center;
            }}
            .canvas-container {{ 
                position: relative; 
                display: inline-block; 
                border: 2px solid #ddd; 
                border-radius: 8px;
                background: #fff;
            }}
            #backgroundCanvas, #drawingCanvas {{ 
                position: absolute; 
                top: 0; 
                left: 0; 
            }}
            #backgroundCanvas {{ z-index: 1; }}
            #drawingCanvas {{ z-index: 2; cursor: crosshair; }}
            button {{ 
                padding: 8px 16px; 
                border: none; 
                border-radius: 4px; 
                cursor: pointer; 
                font-size: 14px;
                font-weight: 500;
            }}
            .btn-primary {{ background: #ff4b4b; color: white; }}
            .btn-secondary {{ background: #f0f2f6; color: #333; border: 1px solid #ddd; }}
            .btn-success {{ background: #00d924; color: white; }}
            input[type="range"] {{ width: 120px; }}
            .brush-info {{ 
                background: #e6f3ff; 
                padding: 8px 12px; 
                border-radius: 4px; 
                font-size: 12px;
            }}
            .status {{ 
                margin-top: 10px; 
                padding: 8px; 
                border-radius: 4px; 
                font-size: 14px;
            }}
            .status.success {{ background: #d4edda; color: #155724; }}
            .status.info {{ background: #d1ecf1; color: #0c5460; }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="controls">
                <label>🖌️ Brush Size:</label>
                <input type="range" id="brushSize" min="5" max="80" value="25" oninput="updateBrushSize()">
                <span id="brushSizeValue" class="brush-info">25px</span>
                
                <button class="btn-secondary" onclick="clearCanvas()">🗑️ Clear All</button>
                <button class="btn-secondary" onclick="undoLast()">↶ Undo</button>
                <button class="btn-success" onclick="downloadPaintedImage()">💾 Generate Painted Image</button>
            </div>
            
            <div class="canvas-container">
                <canvas id="backgroundCanvas" width="{canvas_width}" height="{canvas_height}"></canvas>
                <canvas id="drawingCanvas" width="{canvas_width}" height="{canvas_height}"></canvas>
            </div>
            
            <div id="status" class="status info">
                🎯 <strong>Instructions:</strong> Paint black areas where you want AI to generate new content. Use mouse or touch to paint.
            </div>
        </div>

        <script>
            let isDrawing = false;
            let brushSize = 25;
            let strokes = [];
            let currentStroke = [];
            
            const backgroundCanvas = document.getElementById('backgroundCanvas');
            const drawingCanvas = document.getElementById('drawingCanvas');
            const backgroundCtx = backgroundCanvas.getContext('2d');
            const drawingCtx = drawingCanvas.getContext('2d');
            const statusDiv = document.getElementById('status');
            
            // Load background image
            const img = new Image();
            img.onload = function() {{
                backgroundCtx.drawImage(img, 0, 0, {canvas_width}, {canvas_height});
            }};
            img.src = '{img_b64}';
            
            // Set up drawing context
            drawingCtx.fillStyle = 'rgba(0, 0, 0, 0.8)';
            drawingCtx.strokeStyle = 'rgba(0, 0, 0, 0.8)';
            drawingCtx.lineWidth = brushSize;
            drawingCtx.lineCap = 'round';
            drawingCtx.lineJoin = 'round';
            
            // Mouse events
            drawingCanvas.addEventListener('mousedown', startDrawing);
            drawingCanvas.addEventListener('mousemove', draw);
            drawingCanvas.addEventListener('mouseup', stopDrawing);
            drawingCanvas.addEventListener('mouseout', stopDrawing);
            
            // Touch events
            drawingCanvas.addEventListener('touchstart', handleTouch);
            drawingCanvas.addEventListener('touchmove', handleTouch);
            drawingCanvas.addEventListener('touchend', stopDrawing);
            
            function handleTouch(e) {{
                e.preventDefault();
                const touch = e.touches[0];
                const rect = drawingCanvas.getBoundingClientRect();
                const x = touch.clientX - rect.left;
                const y = touch.clientY - rect.top;
                
                if (e.type === 'touchstart') {{
                    startDrawing({{offsetX: x, offsetY: y}});
                }} else if (e.type === 'touchmove') {{
                    draw({{offsetX: x, offsetY: y}});
                }}
            }}
            
            function startDrawing(e) {{
                isDrawing = true;
                currentStroke = [];
                currentStroke.push({{x: e.offsetX, y: e.offsetY, size: brushSize}});
                
                drawingCtx.beginPath();
                drawingCtx.arc(e.offsetX, e.offsetY, brushSize/2, 0, 2 * Math.PI);
                drawingCtx.fill();
            }}
            
            function draw(e) {{
                if (!isDrawing) return;
                
                currentStroke.push({{x: e.offsetX, y: e.offsetY, size: brushSize}});
                
                drawingCtx.lineWidth = brushSize;
                drawingCtx.lineTo(e.offsetX, e.offsetY);
                drawingCtx.stroke();
                
                // Also draw a circle at current position for smooth painting
                drawingCtx.beginPath();
                drawingCtx.arc(e.offsetX, e.offsetY, brushSize/2, 0, 2 * Math.PI);
                drawingCtx.fill();
            }}
            
            function stopDrawing() {{
                if (isDrawing) {{
                    isDrawing = false;
                    strokes.push([...currentStroke]);
                    updateStatus(`Painted stroke ${{strokes.length}}. Total strokes: ${{strokes.length}}`);
                }}
            }}
            
            function updateBrushSize() {{
                brushSize = document.getElementById('brushSize').value;
                document.getElementById('brushSizeValue').textContent = brushSize + 'px';
                drawingCtx.lineWidth = brushSize;
            }}
            
            function clearCanvas() {{
                drawingCtx.clearRect(0, 0, drawingCanvas.width, drawingCanvas.height);
                strokes = [];
                updateStatus('Canvas cleared. Ready to paint new areas.');
            }}
            
            function undoLast() {{
                if (strokes.length > 0) {{
                    strokes.pop();
                    redrawCanvas();
                    updateStatus(`Undone. ${{strokes.length}} strokes remaining.`);
                }}
            }}
            
            function redrawCanvas() {{
                drawingCtx.clearRect(0, 0, drawingCanvas.width, drawingCanvas.height);
                
                for (let stroke of strokes) {{
                    if (stroke.length > 0) {{
                        drawingCtx.beginPath();
                        
                        // Draw circles for each point
                        for (let point of stroke) {{
                            drawingCtx.arc(point.x, point.y, point.size/2, 0, 2 * Math.PI);
                            drawingCtx.fill();
                        }}
                        
                        // Draw connecting lines
                        if (stroke.length > 1) {{
                            drawingCtx.beginPath();
                            drawingCtx.lineWidth = stroke[0].size;
                            drawingCtx.moveTo(stroke[0].x, stroke[0].y);
                            
                            for (let i = 1; i < stroke.length; i++) {{
                                drawingCtx.lineTo(stroke[i].x, stroke[i].y);
                            }}
                            drawingCtx.stroke();
                        }}
                    }}
                }}
            }}
            
            function updateStatus(message) {{
                statusDiv.innerHTML = `<strong>Status:</strong> ${{message}}`;
                statusDiv.className = 'status success';
            }}
            
            function downloadPaintedImage() {{
                if (strokes.length === 0) {{
                    alert('Please paint some black areas first!');
                    return;
                }}
                
                // Create composite canvas
                const compositeCanvas = document.createElement('canvas');
                compositeCanvas.width = {canvas_width};
                compositeCanvas.height = {canvas_height};
                const compositeCtx = compositeCanvas.getContext('2d');
                
                // Draw background image
                compositeCtx.drawImage(backgroundCanvas, 0, 0);
                
                // Draw black painted areas on top
                compositeCtx.drawImage(drawingCanvas, 0, 0);
                
                // Convert to base64 and send to Streamlit
                const paintedDataUrl = compositeCanvas.toDataURL('image/png');
                
                window.parent.postMessage({{
                    type: 'painted_image_ready',
                    data: paintedDataUrl,
                    original_size: [{image.size[0]}, {image.size[1]}],
                    canvas_size: [{canvas_width}, {canvas_height}],
                    strokes_count: strokes.length
                }}, '*');
                
                updateStatus(`Painted image generated with ${{strokes.length}} strokes! Ready for inpainting.`);
            }}
        </script>
    </body>
    </html>
    """
    
    return html_code

def show_edit_interface(api_key):
    """Show the HTML/JS based edit interface"""
    
    st.write("✏️ **Professional Image Editing Suite**")
    st.write("💰 **Cost-effective tools (5 credits each)**")
    
    # Basic Streamlit file upload (reliable)
    uploaded_file = st.file_uploader(
        "Upload image to edit:",
        type=['png', 'jpg', 'jpeg'],
        help="Upload the image you want to edit"
    )
    
    if uploaded_file is not None:
        original_image = Image.open(uploaded_file)
        
        # Store in session state
        if 'current_image' not in st.session_state:
            st.session_state.current_image = original_image
        
        # Show original image
        col1, col2 = st.columns([1, 1])
        
        with col1:
            st.write("**📷 Original Image**")
            st.image(original_image, caption=f"Size: {original_image.size[0]}x{original_image.size[1]}")
        
        # Tool selection
        edit_tool = st.selectbox(
            "Choose editing tool:",
            [
                "🖤 Black Paint Inpainting",
                "🗑️ Remove Background", 
                "🔄 Replace Background",
                "🔍 Search & Replace",
                "⭕ Erase Object"
            ]
        )
        
        st.markdown("---")
        
        if edit_tool == "🖤 Black Paint Inpainting":
            show_html_black_paint_inpainting(api_key, original_image, col2)
        elif edit_tool == "🗑️ Remove Background":
            show_simple_background_removal(api_key, original_image, col2)
        elif edit_tool == "🔄 Replace Background":
            show_simple_background_replacement(api_key, original_image, col2)
        elif edit_tool == "🔍 Search & Replace":
            show_simple_search_replace(api_key, original_image, col2)
        elif edit_tool == "⭕ Erase Object":
            show_simple_erase_object(api_key, original_image, col2)

def show_html_black_paint_inpainting(api_key, image, result_column):
    """Show HTML/JS black painting interface"""
    st.subheader("🖤 Black Paint Inpainting")
    st.write("🎯 **Paint black areas where you want AI to generate new content**")
    
    # Create the HTML interface
    html_interface = create_black_painting_interface(image)
    
    # Display the interface
    html(html_interface, height=700, scrolling=False)
    
    # Simple prompt input (reliable Streamlit)
    prompt = st.text_area(
        "What should appear in the black painted areas:",
        placeholder="beautiful flowers, blue sky, modern building, person smiling...",
        help="Describe what you want to generate in the black painted areas",
        height=80
    )
    
    # File upload for painted image (fallback method)
    st.write("**Alternative: Upload painted image directly**")
    painted_file = st.file_uploader(
        "Or upload image with black painted areas:",
        type=['png', 'jpg', 'jpeg'],
        help="If the painting interface doesn't work, paint black areas in any image editor and upload here",
        key="painted_image_upload"
    )
    
    # Process button
    if st.button("🎨 Apply Inpainting", type="primary"):
        if painted_file is not None and prompt.strip():
            painted_image = Image.open(painted_file)
            
            with st.spinner("🎨 Processing black painted areas..."):
                result, mask = inpaint_with_black_painted_image(api_key, image, painted_image, prompt)
                
                if result:
                    with result_column:
                        st.write("**✨ Inpainting Result**")
                        st.image(result, caption="Black areas replaced!")
                        
                        # Download button (reliable Streamlit)
                        buf = io.BytesIO()
                        result.save(buf, format="PNG")
                        st.download_button(
                            "📥 Download Result",
                            data=buf.getvalue(),
                            file_name="inpainted_result.png",
                            mime="image/png"
                        )
        elif not prompt.strip():
            st.warning("Please enter a prompt describing what should appear in the black areas.")
        else:
            st.info("Use the painting interface above or upload a painted image.")

def show_simple_background_removal(api_key, image, result_column):
    """Simple background removal"""
    st.subheader("🗑️ Remove Background")
    
    if st.button("🗑️ Remove Background", type="primary"):
        with st.spinner("🗑️ Removing background..."):
            result = remove_background(api_key, image)
            if result:
                with result_column:
                    st.write("**✨ Result**")
                    st.image(result, caption="Background removed!")
                    
                    buf = io.BytesIO()
                    result.save(buf, format="PNG")
                    st.download_button(
                        "📥 Download Result",
                        data=buf.getvalue(),
                        file_name="no_background.png",
                        mime="image/png"
                    )

def show_simple_background_replacement(api_key, image, result_column):
    """Simple background replacement"""
    st.subheader("🔄 Replace Background")
    
    prompt = st.text_input(
        "New background description:",
        placeholder="beautiful sunset beach, modern office, mountain landscape..."
    )
    
    if st.button("🔄 Replace Background", type="primary") and prompt.strip():
        with st.spinner("🔄 Replacing background..."):
            result = replace_background(api_key, image, prompt)
            if result:
                with result_column:
                    st.write("**✨ Result**")
                    st.image(result, caption=f"New background: {prompt}")
                    
                    buf = io.BytesIO()
                    result.save(buf, format="PNG")
                    st.download_button(
                        "📥 Download Result",
                        data=buf.getvalue(),
                        file_name="new_background.png",
                        mime="image/png"
                    )

def show_simple_search_replace(api_key, image, result_column):
    """Simple search and replace"""
    st.subheader("🔍 Search & Replace")
    
    col_search, col_replace = st.columns(2)
    
    with col_search:
        search_prompt = st.text_input("Find:", placeholder="red car, person, tree...")
    
    with col_replace:
        replace_prompt = st.text_input("Replace with:", placeholder="blue car, dog, building...")
    
    if st.button("🔍 Search & Replace", type="primary") and search_prompt.strip() and replace_prompt.strip():
        with st.spinner("🔍 Searching and replacing..."):
            result = search_and_replace(api_key, image, search_prompt, replace_prompt)
            if result:
                with result_column:
                    st.write("**✨ Result**")
                    st.image(result, caption=f"Replaced '{search_prompt}' with '{replace_prompt}'")
                    
                    buf = io.BytesIO()
                    result.save(buf, format="PNG")
                    st.download_button(
                        "📥 Download Result",
                        data=buf.getvalue(),
                        file_name="search_replace.png",
                        mime="image/png"
                    )

def show_simple_erase_object(api_key, image, result_column):
    """Simple object erasing"""
    st.subheader("⭕ Erase Object")
    
    object_prompt = st.text_input(
        "Object to erase:",
        placeholder="person in background, watermark, unwanted object..."
    )
    
    if st.button("⭕ Erase Object", type="primary") and object_prompt.strip():
        with st.spinner("⭕ Erasing object..."):
            result = erase_object(api_key, image, object_prompt)
            if result:
                with result_column:
                    st.write("**✨ Result**")
                    st.image(result, caption=f"Erased: {object_prompt}")
                    
                    buf = io.BytesIO()
                    result.save(buf, format="PNG")
                    st.download_button(
                        "📥 Download Result",
                        data=buf.getvalue(),
                        file_name="erased_object.png",
                        mime="image/png"
                        
                    )



