import streamlit as st
import requests
import io
from PIL import Image

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

def inpaint_image(api_key, image, prompt, mask=None):
    """Inpaint to add elements using Stability AI API"""
    url = "https://api.stability.ai/v2beta/stable-image/edit/inpaint"
    
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Accept": "image/*"
    }
    
    img_byte_arr = io.BytesIO()
    image.save(img_byte_arr, format='PNG')
    img_byte_arr = img_byte_arr.getvalue()
    
    # Create a simple mask for the entire image if none provided
    if mask is None:
        # Create a small mask in the center for adding elements
        from PIL import ImageDraw
        mask = Image.new('L', image.size, 0)
        draw = ImageDraw.Draw(mask)
        # Small area in center where new element can be added
        w, h = image.size
        draw.rectangle([w//3, h//3, 2*w//3, 2*h//3], fill=255)
    
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

def detect_person_in_image(image):
    """Simple person detection (placeholder - could be enhanced with CV)"""
    # For now, we'll assume any uploaded image could contain a person
    # In a real implementation, you'd use object detection
    return True

def show_edit_interface(api_key):
    """Show the 2-level edit interface"""
    
    st.write("✏️ **Professional AI Image Editing Suite**")
    
    # Create tabs for Basic and Advanced
    tab1, tab2 = st.tabs(["🎯 Basic Editing", "🔧 Advanced Editing"])
    
    # Image upload (shared between tabs)
    uploaded_file = st.file_uploader(
        "Upload image to edit:",
        type=['png', 'jpg', 'jpeg'],
        help="Upload the image you want to edit"
    )
    
    if uploaded_file is not None:
        original_image = Image.open(uploaded_file)
        
        with tab1:
            show_basic_editing(api_key, original_image)
        
        with tab2:
            show_advanced_editing(api_key, original_image)

def show_basic_editing(api_key, image):
    """Show basic editing interface with prompt-only tools"""
    
    st.subheader("🎯 Basic Editing - Prompt-Only Tools")
    st.write("Simple, powerful editing using only text descriptions!")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.write("**📷 Original Image**")
        st.image(image, caption=f"Size: {image.size[0]}x{image.size[1]}")
    
    # Basic editing tools selection
    edit_tool = st.selectbox(
        "Choose editing tool:",
        [
            "🗑️ Remove Background",
            "🌅 Change Background", 
            "👕 Change Outfit",
            "🖼️ Generate Headshot",
            "➕ Add Elements"
        ],
        help="Select the editing operation"
    )
    
    st.markdown("---")
    
    if edit_tool == "🗑️ Remove Background":
        st.subheader("🗑️ Remove Background")
        st.write("Automatically remove the background to create a transparent image.")
        
        if st.button("🗑️ Remove Background", type="primary", use_container_width=True):
            with st.spinner("🗑️ Removing background..."):
                result = remove_background(api_key, image)
                if result:
                    show_result(result, "Background removed!", "no_background.png", col2)
    
    elif edit_tool == "🌅 Change Background":
        st.subheader("🌅 Change Background")
        st.write("Replace the background while keeping the main subject.")
        
        # Background presets
        st.write("**Quick Presets:**")
        preset_cols = st.columns(4)
        
        background_presets = {
            "🏖️ Beach": "beautiful tropical beach with white sand and turquoise water",
            "🏙️ City": "modern city skyline at sunset with skyscrapers",
            "🌲 Nature": "lush green forest with sunlight filtering through trees",
            "🎨 Studio": "professional white studio background with soft lighting"
        }
        
        selected_preset = None
        for i, (preset_name, preset_desc) in enumerate(background_presets.items()):
            with preset_cols[i % 4]:
                if st.button(preset_name, key=f"bg_preset_{i}"):
                    selected_preset = preset_desc
        
        # Custom background
        background_prompt = st.text_area(
            "Or describe custom background:",
            value=selected_preset or "",
            placeholder="mountain landscape, office space, cosmic background...",
            help="Describe the new background you want"
        )
        
        if st.button("🌅 Change Background", type="primary", use_container_width=True):
            if background_prompt.strip():
                with st.spinner("🌅 Changing background..."):
                    result = replace_background(api_key, image, background_prompt)
                    if result:
                        show_result(result, f"Background: {background_prompt[:30]}...", "new_background.png", col2)
            else:
                st.warning("Please select a preset or describe a custom background.")
    
    elif edit_tool == "👕 Change Outfit":
        st.subheader("👕 Change Outfit")
        st.write("Change clothing and outfits in the image.")
        
        # Outfit presets
        st.write("**Outfit Styles:**")
        outfit_cols = st.columns(3)
        
        outfit_presets = {
            "💼 Business": "professional business suit, formal attire",
            "👕 Casual": "casual t-shirt and jeans, relaxed clothing",
            "👗 Formal": "elegant formal dress, sophisticated attire",
            "🏃 Sports": "athletic sportswear, gym clothing",
            "🎭 Vintage": "vintage retro clothing, classic style",
            "🦸 Superhero": "superhero costume, cape and mask"
        }
        
        selected_outfit = None
        for i, (outfit_name, outfit_desc) in enumerate(outfit_presets.items()):
            with outfit_cols[i % 3]:
                if st.button(outfit_name, key=f"outfit_preset_{i}"):
                    selected_outfit = outfit_desc
        
        # Custom outfit
        outfit_prompt = st.text_area(
            "Or describe custom outfit:",
            value=selected_outfit or "",
            placeholder="red evening gown, leather jacket, traditional kimono...",
            help="Describe the new outfit you want"
        )
        
        if st.button("👕 Change Outfit", type="primary", use_container_width=True):
            if outfit_prompt.strip():
                with st.spinner("👕 Changing outfit..."):
                    result = search_and_replace(api_key, image, "clothing, outfit, shirt, dress", outfit_prompt)
                    if result:
                        show_result(result, f"Outfit: {outfit_prompt[:30]}...", "new_outfit.png", col2)
            else:
                st.warning("Please select a preset or describe a custom outfit.")
    
    elif edit_tool == "🖼️ Generate Headshot":
        st.subheader("🖼️ Generate Headshot")
        st.write("Create a professional headshot from a person's image.")
        
        # Check if image likely contains a person
        if detect_person_in_image(image):
            headshot_style = st.selectbox(
                "Headshot style:",
                [
                    "Professional business headshot",
                    "LinkedIn profile photo",
                    "Corporate executive portrait",
                    "Creative professional headshot",
                    "Academic professional photo"
                ]
            )
            
            if st.button("🖼️ Generate Headshot", type="primary", use_container_width=True):
                with st.spinner("🖼️ Creating professional headshot..."):
                    result = search_and_replace(api_key, image, "background, clothing", headshot_style)
                    if result:
                        show_result(result, "Professional headshot created!", "headshot.png", col2)
        else:
            st.error("⚠️ No person detected in the image. Please upload an image containing a person for headshot generation.")
    
    elif edit_tool == "➕ Add Elements":
        st.subheader("➕ Add Elements")
        st.write("Add people, animals, or objects to your image.")
        
        element_type = st.selectbox(
            "What to add:",
            ["👥 People", "🐕 Animals", "🚗 Objects", "🌸 Nature Elements"],
            help="Choose the type of element to add"
        )
        
        element_prompt = st.text_area(
            "Describe what to add:",
            placeholder="a smiling person waving, a golden retriever, a red sports car, blooming flowers...",
            help="Be specific about what you want to add to the image"
        )
        
        position_hint = st.selectbox(
            "Where to add (hint):",
            ["center of image", "left side", "right side", "background", "foreground"],
            help="Suggest where the element should appear"
        )
        
        if st.button("➕ Add Element", type="primary", use_container_width=True):
            if element_prompt.strip():
                full_prompt = f"{element_prompt} in the {position_hint}"
                with st.spinner("➕ Adding element to image..."):
                    result = inpaint_image(api_key, image, full_prompt)
                    if result:
                        show_result(result, f"Added: {element_prompt[:30]}...", "added_element.png", col2)
            else:
                st.warning("Please describe what you want to add.")

def show_advanced_editing(api_key, image):
    """Show advanced editing interface (placeholder for future)"""
    
    st.subheader("🔧 Advanced Editing")
    st.write("Advanced tools with manual control coming soon!")
    
    st.info("🚧 **Coming Soon:**")
    st.write("- Interactive masking tools")
    st.write("- Precise inpainting control") 
    st.write("- Manual object selection")
    st.write("- Layer-based editing")
    st.write("- Custom brush sizes")
    
    st.write("For now, use the Basic Editing tab for powerful prompt-based editing!")

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
