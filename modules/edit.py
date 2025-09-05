import streamlit as st
import requests
import io
from PIL import Image
import base64
from streamlit.components.v1 import html

def search_and_replace(api_key, image, search_prompt, replace_prompt, negative_prompt="", seed=0):
    """Search and replace using correct Stability AI API format"""
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
        "prompt": (None, replace_prompt),
        "search_prompt": (None, search_prompt),
        "negative_prompt": (None, negative_prompt),
        "mode": (None, "search"),
        "seed": (None, str(seed)),
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

def erase_with_mask(api_key, image, mask, seed=0):
    """Erase using mask (requires actual mask image, not text)"""
    url = "https://api.stability.ai/v2beta/stable-image/edit/erase"
    
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
        "seed": (None, str(seed)),
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

def replace_background_and_relight(api_key, image, background_prompt, foreground_prompt="", negative_prompt="", 
                                 preserve_original_subject=0.6, seed=0):
    """Replace background using correct API format"""
    url = "https://api.stability.ai/v2beta/stable-image/edit/replace-background-and-relight"
    
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Accept": "image/*"
    }
    
    img_byte_arr = io.BytesIO()
    image.save(img_byte_arr, format='PNG')
    img_byte_arr = img_byte_arr.getvalue()
    
    files = {
        "subject_image": ("image.png", img_byte_arr, "image/png"),
        "background_prompt": (None, background_prompt),
        "foreground_prompt": (None, foreground_prompt),
        "negative_prompt": (None, negative_prompt),
        "preserve_original_subject": (None, str(preserve_original_subject)),
        "seed": (None, str(seed)),
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
    """Remove background - this one already works"""
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

def inpaint_with_white_mask_image(api_key, original_image, mask_image, prompt, negative_prompt="", seed=0):
    """Inpaint using white painted areas as mask - already working"""
    url = "https://api.stability.ai/v2beta/stable-image/edit/inpaint"
    
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Accept": "image/*"
    }
    
    img_byte_arr = io.BytesIO()
    original_image.save(img_byte_arr, format='PNG')
    img_byte_arr = img_byte_arr.getvalue()
    
    mask_gray = mask_image.convert('L')
    mask_byte_arr = io.BytesIO()
    mask_gray.save(mask_byte_arr, format='PNG')
    mask_byte_arr = mask_byte_arr.getvalue()
    
    files = {
        "image": ("image.png", img_byte_arr, "image/png"),
        "mask": ("mask.png", mask_byte_arr, "image/png"),
        "prompt": (None, prompt),
        "negative_prompt": (None, negative_prompt),
        "mode": (None, "mask"),
        "seed": (None, str(seed)),
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

def create_white_painting_interface(image):
    """Create HTML/JS interface for white painting"""
    img_b64 = image_to_base64(image)
    
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
            .instruction {{ 
                background: #fff3cd; 
                border: 1px solid #ffeaa7; 
                padding: 12px; 
                border-radius: 6px; 
                margin-bottom: 15px;
                color: #856404;
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="instruction">
                <strong>Paint WHITE areas where you want AI to generate new content.</strong>
            </div>
            
            <div class="controls">
                <label>Brush Size:</label>
                <input type="range" id="brushSize" min="5" max="80" value="25" oninput="updateBrushSize()">
                <span id="brushSizeValue" class="brush-info">25px</span>
                
                <button class="btn-secondary" onclick="clearCanvas()">Clear All</button>
                <button class="btn-secondary" onclick="undoLast()">Undo</button>
                <button class="btn-success" onclick="downloadPaintedImage()">Download Painted Image</button>
            </div>
            
            <div class="canvas-container">
                <canvas id="backgroundCanvas" width="{canvas_width}" height="{canvas_height}"></canvas>
                <canvas id="drawingCanvas" width="{canvas_width}" height="{canvas_height}"></canvas>
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
            
            const img = new Image();
            img.onload = function() {{
                backgroundCtx.drawImage(img, 0, 0, {canvas_width}, {canvas_height});
            }};
            img.src = '{img_b64}';
            
            drawingCtx.fillStyle = 'rgba(255, 255, 255, 0.9)';
            drawingCtx.strokeStyle = 'rgba(255, 255, 255, 0.9)';
            drawingCtx.lineWidth = brushSize;
            drawingCtx.lineCap = 'round';
            drawingCtx.lineJoin = 'round';
            
            drawingCanvas.addEventListener('mousedown', startDrawing);
            drawingCanvas.addEventListener('mousemove', draw);
            drawingCanvas.addEventListener('mouseup', stopDrawing);
            drawingCanvas.addEventListener('mouseout', stopDrawing);
            
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
                
                drawingCtx.beginPath();
                drawingCtx.arc(e.offsetX, e.offsetY, brushSize/2, 0, 2 * Math.PI);
                drawingCtx.fill();
            }}
            
            function stopDrawing() {{
                if (isDrawing) {{
                    isDrawing = false;
                    strokes.push([...currentStroke]);
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
            }}
            
            function undoLast() {{
                if (strokes.length > 0) {{
                    strokes.pop();
                    redrawCanvas();
                }}
            }}
            
            function redrawCanvas() {{
                drawingCtx.clearRect(0, 0, drawingCanvas.width, drawingCanvas.height);
                
                for (let stroke of strokes) {{
                    if (stroke.length > 0) {{
                        drawingCtx.beginPath();
                        
                        for (let point of stroke) {{
                            drawingCtx.arc(point.x, point.y, point.size/2, 0, 2 * Math.PI);
                            drawingCtx.fill();
                        }}
                        
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
            
            function downloadPaintedImage() {{
                const compositeCanvas = document.createElement('canvas');
                compositeCanvas.width = {image.size[0]};
                compositeCanvas.height = {image.size[1]};
                const compositeCtx = compositeCanvas.getContext('2d');
                
                const scaleX = {image.size[0]} / {canvas_width};
                const scaleY = {image.size[1]} / {canvas_height};
                
                const originalImg = new Image();
                originalImg.onload = function() {{
                    compositeCtx.drawImage(originalImg, 0, 0, {image.size[0]}, {image.size[1]});
                    
                    compositeCtx.fillStyle = 'white';
                    compositeCtx.strokeStyle = 'white';
                    
                    for (let stroke of strokes) {{
                        if (stroke.length > 0) {{
                            for (let point of stroke) {{
                                const scaledX = point.x * scaleX;
                                const scaledY = point.y * scaleY;
                                const scaledSize = point.size * Math.min(scaleX, scaleY);
                                
                                compositeCtx.beginPath();
                                compositeCtx.arc(scaledX, scaledY, scaledSize/2, 0, 2 * Math.PI);
                                compositeCtx.fill();
                            }}
                            
                            if (stroke.length > 1) {{
                                compositeCtx.beginPath();
                                compositeCtx.lineWidth = stroke[0].size * Math.min(scaleX, scaleY);
                                compositeCtx.moveTo(stroke[0].x * scaleX, stroke[0].y * scaleY);
                                
                                for (let i = 1; i < stroke.length; i++) {{
                                    compositeCtx.lineTo(stroke[i].x * scaleX, stroke[i].y * scaleY);
                                }}
                                compositeCtx.stroke();
                            }}
                        }}
                    }}
                    
                    const link = document.createElement('a');
                    link.download = 'painted_image_white_mask.png';
                    link.href = compositeCanvas.toDataURL('image/png');
                    link.click();
                    
                    alert('Painted image downloaded! Re-upload it in the upload field below.');
                }};
                originalImg.src = '{img_b64}';
            }}
        </script>
    </body>
    </html>
    """
    
    return html_code

def show_edit_interface(api_key):
    """Show tabbed edit interface"""
    
    st.write("Professional Image Editing Suite")
    st.write("Cost-effective tools (5 credits each)")
    
    uploaded_file = st.file_uploader(
        "Upload image to edit:",
        type=['png', 'jpg', 'jpeg'],
        help="Upload the image you want to edit"
    )
    
    if uploaded_file is not None:
        original_image = Image.open(uploaded_file)
        
        st.write("**Original Image**")
        st.image(original_image, caption=f"Size: {original_image.size[0]}x{original_image.size[1]}", width=400)
        
        # Create tabs for different editing functions
        tab1, tab2, tab3, tab4, tab5 = st.tabs(["Inpaint", "Remove Background", "Search & Replace", "Replace Background", "Erase Object"])
        
        with tab1:
            show_inpaint_tab(api_key, original_image)
        
        with tab2:
            show_remove_background_tab(api_key, original_image)
        
        with tab3:
            show_search_replace_tab(api_key, original_image)
        
        with tab4:
            show_replace_background_tab(api_key, original_image)
        
        with tab5:
            show_erase_object_tab(api_key, original_image)

def show_inpaint_tab(api_key, image):
    """Inpaint tab - white painting"""
    st.subheader("White Paint Inpainting")
    st.write("Paint white areas where you want AI to generate new content")
    
    html_interface = create_white_painting_interface(image)
    html(html_interface, height=700, scrolling=False)
    
    painted_file = st.file_uploader(
        "Upload painted image with white areas:",
        type=['png', 'jpg', 'jpeg'],
        key="inpaint_painted"
    )
    
    if painted_file is not None:
        painted_image = Image.open(painted_file)
        st.image(painted_image, caption="Your painted image", width=300)
        
        col1, col2 = st.columns(2)
        with col1:
            prompt = st.text_area("What should appear in white areas:", key="inpaint_prompt")
        with col2:
            negative_prompt = st.text_area("What to avoid:", key="inpaint_negative")
        
        if st.button("Apply Inpainting", type="primary", key="inpaint_btn"):
            if prompt.strip():
                with st.spinner("Inpainting..."):
                    result = inpaint_with_white_mask_image(api_key, image, painted_image, prompt, negative_prompt)
                    if result:
                        st.image(result, caption="Inpainting result")
                        
                        buf = io.BytesIO()
                        result.save(buf, format="PNG")
                        st.download_button("Download Result", buf.getvalue(), "inpainted.png", "image/png")

def show_remove_background_tab(api_key, image):
    """Remove background tab"""
    st.subheader("Remove Background")
    st.write("Automatically remove the background while preserving the main subject")
    
    if st.button("Remove Background", type="primary", key="remove_bg_btn"):
        with st.spinner("Removing background..."):
            result = remove_background(api_key, image)
            if result:
                st.image(result, caption="Background removed")
                
                buf = io.BytesIO()
                result.save(buf, format="PNG")
                st.download_button("Download Result", buf.getvalue(), "no_background.png", "image/png")

def show_search_replace_tab(api_key, image):
    """Search and replace tab"""
    st.subheader("Search & Replace")
    st.write("Find specific objects and replace them with something else")
    
    col1, col2 = st.columns(2)
    with col1:
        search_prompt = st.text_input("Find (search for):", placeholder="red car, person, tree...", key="search_prompt")
    with col2:
        replace_prompt = st.text_input("Replace with:", placeholder="blue car, dog, building...", key="replace_prompt")
    
    negative_prompt = st.text_input("What to avoid:", key="search_negative")
    
    if st.button("Search & Replace", type="primary", key="search_replace_btn"):
        if search_prompt.strip() and replace_prompt.strip():
            with st.spinner("Searching and replacing..."):
                result = search_and_replace(api_key, image, search_prompt, replace_prompt, negative_prompt)
                if result:
                    st.image(result, caption=f"Replaced '{search_prompt}' with '{replace_prompt}'")
                    
                    buf = io.BytesIO()
                    result.save(buf, format="PNG")
                    st.download_button("Download Result", buf.getvalue(), "search_replace.png", "image/png")
        else:
            st.warning("Please fill in both search and replace prompts")

def show_replace_background_tab(api_key, image):
    """Replace background tab"""
    st.subheader("Replace Background & Relight")
    st.write("Change the background and adjust lighting to match")
    
    background_prompt = st.text_input("New background:", placeholder="sunset beach, office space, mountain landscape...", key="bg_prompt")
    
    col1, col2 = st.columns(2)
    with col1:
        foreground_prompt = st.text_input("Subject description (optional):", key="fg_prompt")
        preserve_subject = st.slider("Preserve original subject:", 0.0, 1.0, 0.6, key="preserve_slider")
    with col2:
        negative_prompt = st.text_input("What to avoid:", key="bg_negative")
    
    if st.button("Replace Background", type="primary", key="replace_bg_btn"):
        if background_prompt.strip():
            with st.spinner("Replacing background..."):
                result = replace_background_and_relight(api_key, image, background_prompt, foreground_prompt, negative_prompt, preserve_subject)
                if result:
                    st.image(result, caption=f"New background: {background_prompt}")
                    
                    buf = io.BytesIO()
                    result.save(buf, format="PNG")
                    st.download_button("Download Result", buf.getvalue(), "new_background.png", "image/png")
        else:
            st.warning("Please describe the new background")

def show_erase_object_tab(api_key, image):
    """Erase object tab"""
    st.subheader("Erase Object")
    st.write("Paint white over objects you want to remove, then upload the mask")
    
    # Same white painting interface but for erasing
    html_interface = create_white_painting_interface(image)
    html(html_interface, height=700, scrolling=False)
    
    mask_file = st.file_uploader(
        "Upload mask (white = erase, black = keep):",
        type=['png', 'jpg', 'jpeg'],
        key="erase_mask"
    )
    
    if mask_file is not None:
        mask_image = Image.open(mask_file)
        st.image(mask_image, caption="Erase mask", width=300)
        
        if st.button("Erase Object", type="primary", key="erase_btn"):
            with st.spinner("Erasing object..."):
                result = erase_with_mask(api_key, image, mask_image)
                if result:
                    st.image(result, caption="Object erased")
                    
                    buf = io.BytesIO()
                    result.save(buf, format="PNG")
                    st.download_button("Download Result", buf.getvalue(), "erased.png", "image/png")
