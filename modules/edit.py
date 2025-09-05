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

def search_and_recolor(api_key, image, search_prompt, color_prompt):
    """Search and recolor using Stability AI API"""
    
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

def show_edit_interface(api_key):
    """Show the edit interface"""
    
    st.write("✏️ **AI-powered image editing tools**")
    st.write("Professional editing with automatic object detection!")
    
    # Edit mode selection
    edit_mode = st.selectbox(
        "Choose editing tool:",
        ["🗑️ Remove Background", "🎨 Replace Background", "🌈 Search & Recolor"],
        help="Select the editing operation you want to perform"
    )
    
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
            st.subheader("📷 Original Image")
            st.image(original_image, caption=f"Size: {original_image.size[0]}x{original_image.size[1]}")
        
        st.markdown("---")
        
        if edit_mode == "🗑️ Remove Background":
            st.subheader("🗑️ Remove Background")
            st.write("Automatically detect and remove the background from your image.")
            
            if st.button("🗑️ Remove Background", type="primary"):
                with st.spinner("🗑️ Removing background..."):
                    result = remove_background(api_key, original_image)
                    
                    if result:
                        with col2:
                            st.subheader("✨ Result")
                            st.image(result, caption="Background removed!")
                            
                            # Download
                            buf = io.BytesIO()
                            result.save(buf, format="PNG")
                            st.download_button(
                                "📥 Download Result",
                                data=buf.getvalue(),
                                file_name="no_background.png",
                                mime="image/png",
                                use_container_width=True
                            )
        
        elif edit_mode == "🎨 Replace Background":
            st.subheader("🎨 Replace Background")
            st.write("Keep the main subject and replace the background with something new.")
            
            background_prompt = st.text_area(
                "New background description:",
                placeholder="beautiful sunset beach, modern office space, mountain landscape, studio lighting...",
                help="Describe what kind of background you want",
                height=80
            )
            
            if st.button("🎨 Replace Background", type="primary"):
                if background_prompt.strip():
                    with st.spinner("🎨 Replacing background..."):
                        result = replace_background(api_key, original_image, background_prompt)
                        
                        if result:
                            with col2:
                                st.subheader("✨ Result")
                                st.image(result, caption=f"New background: {background_prompt[:30]}...")
                                
                                # Download
                                buf = io.BytesIO()
                                result.save(buf, format="PNG")
                                st.download_button(
                                    "📥 Download Result",
                                    data=buf.getvalue(),
                                    file_name="new_background.png",
                                    mime="image/png",
                                    use_container_width=True
                                )
                else:
                    st.warning("Please describe the new background you want.")
        
        elif edit_mode == "🌈 Search & Recolor":
            st.subheader("🌈 Search & Recolor")
            st.write("Find specific objects or areas and change their colors.")
            
            col_search, col_color = st.columns(2)
            
            with col_search:
                search_prompt = st.text_input(
                    "What to find:",
                    placeholder="shirt, car, hair, flowers, walls...",
                    help="Describe what you want to recolor"
                )
            
            with col_color:
                color_prompt = st.text_input(
                    "New color:",
                    placeholder="bright red, deep blue, golden yellow, pink...",
                    help="Describe the new color"
                )
            
            if st.button("🌈 Search & Recolor", type="primary"):
                if search_prompt.strip() and color_prompt.strip():
                    with st.spinner("🌈 Recoloring..."):
                        result = search_and_recolor(api_key, original_image, search_prompt, color_prompt)
                        
                        if result:
                            with col2:
                                st.subheader("✨ Result")
                                st.image(result, caption=f"Recolored '{search_prompt}' to '{color_prompt}'")
                                
                                # Download
                                buf = io.BytesIO()
                                result.save(buf, format="PNG")
                                st.download_button(
                                    "📥 Download Result",
                                    data=buf.getvalue(),
                                    file_name="recolored_image.png",
                                    mime="image/png",
                                    use_container_width=True
                                )
                else:
                    st.warning("Please fill in both search and color prompts.")
        
        # Tips section
        with st.expander("💡 Editing Tips"):
            st.write("**For best results:**")
            st.write("- Use clear, simple descriptions")
            st.write("- 'Remove Background' works best with clear subjects")
            st.write("- 'Replace Background' keeps the main subject intact") 
            st.write("- 'Search & Recolor' works well for clothing, objects, and large areas")
            st.write("- Try different phrasings if the first attempt doesn't work perfectly")
