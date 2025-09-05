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
        "mask": (None, object_prompt),  # AI will find the object
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
    """Show the simplified edit interface"""
    
    st.write("✏️ **AI-powered image editing tools**")
    st.write("Professional editing without complex masking - just describe what you want!")
    
    # Edit mode selection
    edit_mode = st.selectbox(
        "Choose editing tool:",
        ["🗑️ Remove Background", "🔍 Search & Replace", "⭕ Erase Object"],
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
            st.write("Automatically remove the background from your image.")
            
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
        
        elif edit_mode == "🔍 Search & Replace":
            st.subheader("🔍 Search & Replace")
            st.write("Find objects or areas in your image and replace them with something else.")
            
            col_search, col_replace = st.columns(2)
            
            with col_search:
                search_prompt = st.text_input(
                    "What to find:",
                    placeholder="red car, person, tree, blue shirt...",
                    help="Describe what you want to replace"
                )
            
            with col_replace:
                replace_prompt = st.text_input(
                    "Replace with:",
                    placeholder="yellow car, flowers, building...",
                    help="Describe what should replace it"
                )
            
            if st.button("🔍 Search & Replace", type="primary"):
                if search_prompt.strip() and replace_prompt.strip():
                    with st.spinner("🔍 Searching and replacing..."):
                        result = search_and_replace(api_key, original_image, search_prompt, replace_prompt)
                        
                        if result:
                            with col2:
                                st.subheader("✨ Result")
                                st.image(result, caption=f"Replaced '{search_prompt}' with '{replace_prompt}'")
                                
                                # Download
                                buf = io.BytesIO()
                                result.save(buf, format="PNG")
                                st.download_button(
                                    "📥 Download Result",
                                    data=buf.getvalue(),
                                    file_name="search_replace_result.png",
                                    mime="image/png",
                                    use_container_width=True
                                )
                else:
                    st.warning("Please fill in both search and replace prompts.")
        
        elif edit_mode == "⭕ Erase Object":
            st.subheader("⭕ Erase Object")
            st.write("Remove specific objects from your image by describing them.")
            
            object_prompt = st.text_input(
                "What to erase:",
                placeholder="person in background, watermark, unwanted object...",
                help="Describe what you want to remove from the image"
            )
            
            if st.button("⭕ Erase Object", type="primary"):
                if object_prompt.strip():
                    with st.spinner("⭕ Erasing object..."):
                        result = erase_object(api_key, original_image, object_prompt)
                        
                        if result:
                            with col2:
                                st.subheader("✨ Result")
                                st.image(result, caption=f"Erased: {object_prompt}")
                                
                                # Download
                                buf = io.BytesIO()
                                result.save(buf, format="PNG")
                                st.download_button(
                                    "📥 Download Result",
                                    data=buf.getvalue(),
                                    file_name="erased_object.png",
                                    mime="image/png",
                                    use_container_width=True
                                )
                else:
                    st.warning("Please describe what you want to erase.")
