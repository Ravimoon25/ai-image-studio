import streamlit as st
import requests
import io
from PIL import Image, ImageDraw

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

def search_and_recolor(api_key, image, search_prompt, color_prompt):
    """Search and recolor using Stability AI API (this one works)"""
    url = "https://api.stability.ai/v2beta/stable-image/edit/search-and-recolor"
    
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
        "color_prompt": (None, color_prompt),
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

def create_variations(api_key, image, prompt):
    """Create variations of an image (alternative approach)"""
    url = "https://api.stability.ai/v2beta/stable-image/generate/ultra"
    
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Accept": "image/*"
    }
    
    # Use the uploaded image as reference and generate variations
    img_byte_arr = io.BytesIO()
    image.save(img_byte_arr, format='PNG')
    img_byte_arr = img_byte_arr.getvalue()
    
    files = {
        "prompt": (None, f"Similar to the uploaded image but {prompt}"),
        "image": ("reference.png", img_byte_arr, "image/png"),
        "strength": (None, "0.7"),  # How much to change from original
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
    """Show the simplified working edit interface"""
    
    st.write("✏️ **AI Image Editing - Working Tools Only**")
    
    # Image upload
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
        
        # Working editing tools
        edit_tool = st.selectbox(
            "Choose editing tool:",
            [
                "🗑️ Remove Background",
                "🌈 Change Colors", 
                "🎨 Style Variations",
                "👕 Outfit Colors"
            ],
            help="Select a working editing operation"
        )
        
        st.markdown("---")
        
        if edit_tool == "🗑️ Remove Background":
            st.subheader("🗑️ Remove Background")
            st.write("✅ **This tool works perfectly!**")
            
            if st.button("🗑️ Remove Background", type="primary", use_container_width=True):
                with st.spinner("🗑️ Removing background..."):
                    result = remove_background(api_key, original_image)
                    if result:
                        show_result(result, "Background removed!", "no_background.png", col2)
        
        elif edit_tool == "🌈 Change Colors":
            st.subheader("🌈 Change Colors")
            st.write("✅ **Change the color of specific objects in your image**")
            
            col_search, col_color = st.columns(2)
            
            with col_search:
                search_items = [
                    "shirt", "dress", "pants", "jacket", "hat",
                    "car", "house", "walls", "flowers", "hair",
                    "sky", "water", "grass", "eyes", "lips"
                ]
                
                search_prompt = st.selectbox(
                    "What to recolor:",
                    search_items,
                    help="Select what you want to change the color of"
                )
                
                # Allow custom input too
                custom_search = st.text_input("Or type custom item:", placeholder="shoes, bag, etc.")
                if custom_search:
                    search_prompt = custom_search
            
            with col_color:
                color_options = [
                    "bright red", "deep blue", "emerald green", "golden yellow",
                    "hot pink", "purple", "orange", "black", "white",
                    "silver", "bronze", "turquoise", "lavender", "coral"
                ]
                
                color_prompt = st.selectbox(
                    "New color:",
                    color_options,
                    help="Choose the new color"
                )
                
                # Allow custom color too
                custom_color = st.text_input("Or type custom color:", placeholder="neon green, etc.")
                if custom_color:
                    color_prompt = custom_color
            
            if st.button("🌈 Change Color", type="primary", use_container_width=True):
                with st.spinner(f"🌈 Changing {search_prompt} to {color_prompt}..."):
                    result = search_and_recolor(api_key, original_image, search_prompt, color_prompt)
                    if result:
                        show_result(result, f"Changed {search_prompt} to {color_prompt}", "recolored.png", col2)
        
        elif edit_tool == "🎨 Style Variations":
            st.subheader("🎨 Style Variations")
            st.write("✅ **Create artistic variations of your image**")
            
            style_options = [
                "as a professional portrait with studio lighting",
                "as a vintage photograph with sepia tones", 
                "as a modern digital art piece",
                "as an oil painting masterpiece",
                "as a watercolor illustration",
                "as a pencil sketch drawing",
                "as a comic book style illustration",
                "with dramatic cinematic lighting"
            ]
            
            selected_style = st.selectbox(
                "Choose style variation:",
                style_options,
                help="Select the artistic style you want"
            )
            
            if st.button("🎨 Create Variation", type="primary", use_container_width=True):
                with st.spinner("🎨 Creating artistic variation..."):
                    result = create_variations(api_key, original_image, selected_style)
                    if result:
                        show_result(result, f"Style: {selected_style[:30]}...", "style_variation.png", col2)
        
        elif edit_tool == "👕 Outfit Colors":
            st.subheader("👕 Outfit Colors")
            st.write("✅ **Change clothing colors specifically**")
            
            clothing_items = [
                "shirt", "t-shirt", "dress", "pants", "jeans",
                "jacket", "sweater", "skirt", "shorts", "suit"
            ]
            
            clothing_item = st.selectbox(
                "Select clothing item:",
                clothing_items,
                help="Choose the clothing item to recolor"
            )
            
            outfit_colors = [
                "navy blue", "charcoal gray", "burgundy red", "forest green",
                "cream white", "jet black", "royal purple", "golden yellow",
                "coral pink", "teal blue", "chocolate brown", "silver gray"
            ]
            
            new_color = st.selectbox(
                "New clothing color:",
                outfit_colors,
                help="Choose the new color for the clothing"
            )
            
            if st.button("👕 Change Outfit Color", type="primary", use_container_width=True):
                with st.spinner(f"👕 Changing {clothing_item} to {new_color}..."):
                    result = search_and_recolor(api_key, original_image, clothing_item, new_color)
                    if result:
                        show_result(result, f"Changed {clothing_item} to {new_color}", "outfit_recolor.png", col2)
        
        # Tips for better results
        with st.expander("💡 Tips for Better Results"):
            st.write("**✅ What works well:**")
            st.write("- Remove Background: Works perfectly on clear subjects")
            st.write("- Change Colors: Works great for clothing, objects, large areas")
            st.write("- Style Variations: Creates artistic interpretations")
            st.write("- Outfit Colors: Specifically designed for clothing")
            st.write("")
            st.write("**🎯 For best results:**")
            st.write("- Use images with clear, distinct objects")
            st.write("- Choose contrasting colors for better visibility")
            st.write("- Try different style variations to find the best one")

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
