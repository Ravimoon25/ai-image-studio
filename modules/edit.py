import streamlit as st
import requests
import io
from PIL import Image
import base64
from streamlit.components.v1 import html

def inpaint_with_white_mask_image(api_key, original_image, mask_image, prompt):
    """Inpaint using white painted areas as mask"""
    url = "https://api.stability.ai/v2beta/stable-image/edit/inpaint"
    
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Accept": "image/*"
    }
    
    # Convert original image to bytes
    img_byte_arr = io.BytesIO()
    original_image.save(img_byte_arr, format='PNG')
    img_byte_arr = img_byte_arr.getvalue()
    
    # Convert mask image to grayscale mask
    mask_gray = mask_image.convert('L')
    mask_byte_arr = io.BytesIO()
    mask_gray.save(mask_byte_arr, format='PNG')
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

def image_to_base64(image):
    """Convert PIL image to base64 string"""
    buffered = io.BytesIO()
    image.save(buffered, format="PNG")
    img_str = base64.b64encode(buffered.getvalue()).decode()
    return f"data:image/png;base64,{img_str}"

def create_white_painting_interface(image):
    """Create HTML/JS interface for white painting"""
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
                <strong>🎯 Instructions:</strong> Paint WHITE areas where you want AI to generate new content. 
                White = change, Original image = keep unchanged.
            </div>
            
            <div class="controls">
                <label>🖌️ Brush Size:</label>
                <input type="range" id="brushSize" min="5" max="80" value="25" oninput="updateBrushSize()">
                <span id="brushSizeValue" class="brush-info">25px</span>
                
                <button class="btn-secondary" onclick="clearCanvas()">🗑️ Clear All</button>
                <button class="btn-secondary" onclick="undoLast()">↶ Undo</button>
                <button class="btn-success" onclick="downloadPaintedImage()">📥 Download Painted Image</button>
            </div>
            
            <div class="canvas-container">
                <canvas id="backgroundCanvas" width="{canvas_width}" height="{canvas_height}"></canvas>
                <canvas id="drawingCanvas" width="{canvas_width}" height="{canvas_height}"></canvas>
            </div>
            
            <div style="margin-top: 15px; padding: 10px; background: #d4edda; border-radius: 6px; color: #155724;">
                <strong>Next steps:</strong> 
                1. Paint white areas → 2. Click "Download Painted Image" → 3. Re-upload below for inpainting
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
            
            // Load background image
            const img = new Image();
            img.onload = function() {{
                backgroundCtx.drawImage(img, 0, 0, {canvas_width}, {canvas_height});
            }};
            img.src = '{img_b64}';
            
            // Set up drawing context for WHITE painting
            drawingCtx.fillStyle = 'rgba(255, 255, 255, 0.9)';  // WHITE paint
            drawingCtx.strokeStyle = 'rgba(255, 255, 255, 0.9)';
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
                // Create composite canvas with original image + white paint
                const compositeCanvas = document.createElement('canvas');
                compositeCanvas.width = {image.size[0]};  // Full resolution
                compositeCanvas.height = {image.size[1]};
                const compositeCtx = compositeCanvas.getContext('2d');
                
                // Scale factor for full resolution
                const scaleX = {image.size[0]} / {canvas_width};
                const scaleY = {image.size[1]} / {canvas_height};
                
                // Draw original image at full resolution
                const originalImg = new Image();
                originalImg.onload = function() {{
                    compositeCtx.drawImage(originalImg, 0, 0, {image.size[0]}, {image.size[1]});
                    
                    // Draw white painted areas scaled to full resolution
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
                    
                    // Download the painted image
                    const link = document.createElement('a');
                    link.download = 'painted_image_white_mask.png';
                    link.href = compositeCanvas.toDataURL('image/png');
                    link.click();
                    
                    alert('Painted image downloaded! Now re-upload it below for inpainting.');
                }};
                originalImg.src = '{img_b64}';
            }}
        </script>
    </body>
    </html>
    """
    
    return html_code

def show_edit_interface(api_key):
    """Show simple inpainting focus interface"""
    
    st.write("✏️ **Simple White Paint Inpainting**")
    st.write("🎯 **Focus: Paint white areas, download, re-upload, inpaint**")
    
    # Step 1: Upload original image
    st.subheader("📤 Step 1: Upload Original Image")
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
        
        # Step 2: White painting interface
        st.markdown("---")
        st.subheader("🎨 Step 2: Paint White Areas")
        st.write("Paint WHITE on areas where you want AI to generate new content")
        
        # Create the HTML interface
        html_interface = create_white_painting_interface(original_image)
        html(html_interface, height=700, scrolling=False)
        
        # Step 3: Re-upload painted image
        st.markdown("---")
        st.subheader("📥 Step 3: Upload Painted Image")
        st.write("After downloading the painted image above, upload it here:")
        
        painted_file = st.file_uploader(
            "Upload painted image with white areas:",
            type=['png', 'jpg', 'jpeg'],
            help="Upload the image you just downloaded with white painted areas",
            key="painted_image_upload"
        )
        
        if painted_file is not None:
            painted_image = Image.open(painted_file)
            st.write("**🎨 Your Painted Image:**")
            st.image(painted_image, caption="Image with white painted areas", width=400)
            
            # Step 4: Prompt and inpaint
            st.markdown("---")
            st.subheader("📝 Step 4: Describe & Inpaint")
            
            prompt = st.text_area(
                "What should appear in the WHITE painted areas:",
                placeholder="beautiful flowers, blue sky, modern building, person smiling...",
                help="Describe what you want to generate in the white painted areas",
                height=80
            )
            
            if st.button("🎨 Apply Inpainting", type="primary"):
                if prompt.strip():
                    with st.spinner("🎨 Inpainting white areas..."):
                        result = inpaint_with_white_mask_image(api_key, original_image, painted_image, prompt)
                        
                        if result:
                            with col2:
                                st.write("**✨ Inpainting Result**")
                                st.image(result, caption="White areas replaced!")
                                
                                # Download result
                                buf = io.BytesIO()
                                result.save(buf, format="PNG")
                                st.download_button(
                                    "📥 Download Result",
                                    data=buf.getvalue(),
                                    file_name="inpainted_result.png",
                                    mime="image/png"
                                )
                else:
                    st.warning("Please enter a prompt describing what should appear in the white areas.")
