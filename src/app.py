import streamlit as st
import os
from processor import ImageProcessor
import io
from PIL import Image

st.set_page_config(page_title="I ❤️ Images", layout="wide")

st.title("I ❤️ Images")
st.markdown("Transform your product images instantly with AI-powered processing.")

# Sidebar Configuration
st.sidebar.header("Configuration")
output_format = st.sidebar.selectbox("Output Format", ["PNG (Best for details)", "JPEG (Best for size)", "WEBP (Best for e-commerce platform)"])
remove_bg = st.sidebar.checkbox("Remove Background (Nano Banana AI)", value=True)
enhance_img = st.sidebar.checkbox("Auto-Enhance (Professional Look)", value=True)

st.sidebar.divider()
st.sidebar.header("Gemini AI Settings")
gemini_api_key = st.sidebar.text_input("Gemini API Key", type="password", help="Enter your Google Gemini API Key")
gemini_prompt = st.sidebar.text_area("Base Prompt", value="Make it professional, luxury product", help="Prompt to guide Gemini's analysis/text generation for the image.")
enable_gemini = st.sidebar.checkbox("Enable Gemini Processing", value=False)

resize_option = st.sidebar.radio("Resize", ["Original", "Custom"])
resize_w, resize_h = None, None
if resize_option == "Custom":
    resize_w = st.sidebar.number_input("Width", min_value=100, value=800)
    resize_h = st.sidebar.number_input("Height", min_value=100, value=800)

processor = ImageProcessor()


# Extract the format string (e.g., "PNG" from "PNG (Best for details)")
selected_format = output_format.split()[0]

# Tabs for Modes
tab1, tab2 = st.tabs(["Single Image", "Batch Processing"])

with tab1:
    st.header("Single Image Upload")
    uploaded_file = st.file_uploader("Choose an image", type=['png', 'jpg', 'jpeg', 'webp'])
    
    if uploaded_file is not None:
        col1, col2 = st.columns(2)
        with col1:
            st.image(uploaded_file, caption="Original", use_container_width=True)
        
        with col2:
            if st.button("Process Image"):
                with st.spinner("Processing with Nano Banana..."):
                    try:
                        dims = (resize_w, resize_h) if resize_option == "Custom" else None
                        
                        # Use Gemini Prompt only if enabled
                        prompt_to_use = gemini_prompt if enable_gemini else None
                        
                        processed_img = processor.process_image(
                            uploaded_file, 
                            output_format=selected_format,
                            resize_dim=dims,
                            remove_bg=remove_bg,
                            enhance=enhance_img,
                            gemini_prompt=prompt_to_use,
                            gemini_api_key=gemini_api_key
                        )
                        st.image(processed_img, caption="Processed", use_container_width=True)
                        
                        # Download Button
                        buf = io.BytesIO()
                        processed_img.save(buf, format=selected_format)
                        byte_im = buf.getvalue()
                        st.download_button(
                            label=f"Download {selected_format}",
                            data=byte_im,
                            file_name=f"processed_image.{selected_format.lower()}",
                            mime=f"image/{selected_format.lower()}"
                        )
                    except Exception as e:
                        st.error(f"Error: {e}")

with tab2:
    st.header("Batch Processing")
    st.info("Batch processing requires a local directory path.")
    input_dir = st.text_input("Input Directory Path", value="/media/hirani/New Volume/Manthan/I_Love_Images/test_images")
    output_dir = st.text_input("Output Directory Path", value="/media/hirani/New Volume/Manthan/I_Love_Images/output")
    
    if st.button("Start Batch Job"):
        if not os.path.exists(input_dir):
            st.error("Input directory does not exist.")
        else:
            if not os.path.exists(output_dir):
                os.makedirs(output_dir)
            
            # Recurse through directories
            file_paths = []
            for root, dirs, files in os.walk(input_dir):
                for file in files:
                    if file.lower().endswith(('png', 'jpg', 'jpeg', 'webp')):
                        file_paths.append(os.path.join(root, file))
            
            if not file_paths:
                st.warning("No images found in the input directory.")
            else:
                progress_bar = st.progress(0)
                status_text = st.empty()
                
                for i, filepath in enumerate(file_paths):
                    filename = os.path.basename(filepath)
                    status_text.text(f"Processing {filename}...")
                    try:
                        dims = (resize_w, resize_h) if resize_option == "Custom" else None
                        prompt_to_use = gemini_prompt if enable_gemini else None

                        # Open and process
                        with open(filepath, "rb") as f:
                            processed_img = processor.process_image(
                                f,
                                output_format=selected_format,
                                resize_dim=dims,
                                remove_bg=remove_bg,
                                enhance=enhance_img,
                                gemini_prompt=prompt_to_use,
                                gemini_api_key=gemini_api_key
                            )
                        
                        # Create relative path structure in output
                        rel_path = os.path.relpath(os.path.dirname(filepath), input_dir)
                        output_subdir = os.path.join(output_dir, rel_path)
                        os.makedirs(output_subdir, exist_ok=True)
                        
                        save_path = os.path.join(output_subdir, f"{os.path.splitext(filename)[0]}.{selected_format.lower()}")
                        processed_img.save(save_path, format=selected_format)
                    except Exception as e:
                        st.warning(f"Failed to process {filename}: {e}")
                    
                    progress_bar.progress((i + 1) / len(file_paths))
                
                st.success(f"Batch processing complete! Processed {len(file_paths)} images.")
