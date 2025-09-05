import streamlit as st
import requests
import io
from PIL import Image
import random

def generate_image(api_key, prompt, negative_prompt="", style="enhance", aspect_ratio="1:1", seed=None):
    """Generate image using Stability AI API with advanced options"""
    
    url = "https://api.stability.ai/v2beta/stable-image/generate/ultra"
    
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Accept": "image/*"
    }
    
    # Prepare form data
    files = {
        "prompt": (None, prompt),
        "aspect_ratio": (None, aspect_ratio),
        "output_format": (None, "png")
    }
    
    # Add optional parameters
    if negative_prompt.strip():
        files["negative_prompt"] = (None, negative_prompt)
    
    if style != "enhance":
        files["style_preset"] = (None, style)
    
    if seed is not None:
        files["seed"] = (None, str(seed))
    
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

def show_generation_interface(api_key):
    """Show the enhanced generation interface"""
    
    # Main prompt
    st.subheader("✨ Prompt")
    prompt = st.text_area(
        "Describe the image you want to generate:",
        height=100,
        placeholder="A serene mountain landscape at sunset with golden light, highly detailed, professional photography"
    )
    
    # Advanced options in expander
    with st.expander("🎨 Style & Advanced Options", expanded=False):
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("Style Preset")
            style_options = {
                "Auto Enhance": "enhance",
                "🎨 Artistic": "anime", 
                "📸 Photographic": "photographic",
                "🎭 Digital Art": "digital-art",
                "🖼️ Fantasy Art": "fantasy-art",
                "✏️ Line Art": "line-art",
                "🎪 Analog Film": "analog-film",
                "🌟 Neon Punk": "neon-punk",
                "🏛️ Cinematic": "cinematic"
            }
            
            selected_style = st.selectbox(
                "Choose style:",
                list(style_options.keys()),
                help="Different artistic styles for your image"
            )
            
            st.subheader("Aspect Ratio")
            aspect_options = {
                "Square (1:1)": "1:1",
                "Portrait (9:16)": "9:16", 
                "Landscape (16:9)": "16:9",
                "Tall (9:21)": "9:21",
                "Wide (21:9)": "21:9"
            }
            
            selected_aspect = st.selectbox(
                "Choose aspect ratio:",
                list(aspect_options.keys())
            )
        
        with col2:
            st.subheader("Negative Prompt")
            negative_prompt = st.text_area(
                "What to avoid in the image:",
                height=80,
                placeholder="blurry, low quality, distorted, ugly, bad anatomy",
                help="Describe what you don't want in the image"
            )
            
            st.subheader("Seed Control")
            use_custom_seed = st.checkbox("Use custom seed", help="For reproducible results")
            
            if use_custom_seed:
                seed = st.number_input(
                    "Seed value:", 
                    min_value=0, 
                    max_value=2147483647,
                    value=42,
                    help="Same seed + prompt = same image"
                )
            else:
                seed = None
                if st.button("🎲 Generate Random Seed"):
                    st.write(f"Random seed: {random.randint(0, 2147483647)}")
    
    # Quality presets
    st.subheader("🏆 Quality Preset")
    quality_col1, quality_col2, quality_col3 = st.columns(3)
    
    with quality_col1:
        if st.button("⚡ Fast", use_container_width=True):
            st.session_state.quality_preset = "fast"
    
    with quality_col2:
        if st.button("⚖️ Balanced", use_container_width=True):
            st.session_state.quality_preset = "balanced"
    
    with quality_col3:
        if st.button("🎨 Best Quality", use_container_width=True):
            st.session_state.quality_preset = "best"
    
    # Show selected preset
    preset = getattr(st.session_state, 'quality_preset', 'balanced')
    st.info(f"Current preset: **{preset.title()}**")
    
    # Generate button
    st.markdown("---")
    
    if st.button("🎨 Generate Image", type="primary", use_container_width=True):
        if prompt.strip():
            with st.spinner("Creating your masterpiece..."):
                style_key = style_options[selected_style]
                aspect_key = aspect_options[selected_aspect]
                
                image = generate_image(
                    api_key=api_key,
                    prompt=prompt,
                    negative_prompt=negative_prompt,
                    style=style_key,
                    aspect_ratio=aspect_key,
                    seed=seed
                )
                
                if image:
                    st.success("🎉 Image generated successfully!")
                    
                    # Display image with details
                    st.image(image, caption=f"Style: {selected_style} | Aspect: {selected_aspect}")
                    
                    # Image details
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.metric("Width", image.size[0])
                    with col2:
                        st.metric("Height", image.size[1])
                    with col3:
                        st.metric("Pixels", f"{image.size[0] * image.size[1]:,}")
                    
                    # Download section
                    st.markdown("---")
                    col1, col2 = st.columns([2, 1])
                    
                    with col1:
                        filename = st.text_input(
                            "Filename:", 
                            value=f"generated_{style_key}_{aspect_key}",
                            help="Name for your download file"
                        )
                    
                    with col2:
                        buf = io.BytesIO()
                        image.save(buf, format="PNG")
                        st.download_button(
                            label="📥 Download PNG",
                            data=buf.getvalue(),
                            file_name=f"{filename}.png",
                            mime="image/png",
                            use_container_width=True
                        )
                    
                    # Generation details
                    with st.expander("📊 Generation Details"):
                        st.write(f"**Prompt:** {prompt}")
                        if negative_prompt:
                            st.write(f"**Negative Prompt:** {negative_prompt}")
                        st.write(f"**Style:** {selected_style}")
                        st.write(f"**Aspect Ratio:** {selected_aspect}")
                        if seed is not None:
                            st.write(f"**Seed:** {seed}")
                        st.write(f"**Quality Preset:** {preset}")
        else:
            st.warning("⚠️ Please enter a prompt to generate an image.")
