import os
from PIL import Image, ImageEnhance, ImageDraw, ImageFont
from rembg import remove
import io
from google import genai
from dotenv import load_dotenv

load_dotenv()

class ImageProcessor:
    def __init__(self):
        self.api_key = os.getenv("GEMINI_API_KEY")

    def process_image(self, image_input, output_format="PNG", resize_dim=None, remove_bg=False, enhance=False, gemini_prompt=None, gemini_api_key=None):
        """
        Process a single image.
        Args:
            image_input: file-like object or path
            output_format: str (PNG, JPEG, WEBP)
            resize_dim: tuple (width, height) or None
            remove_bg: bool
            enhance: bool
            gemini_prompt: str (Optional base prompt for Gemini)
            gemini_api_key: str (Optional override API key)
        Returns:
            processed_image: PIL Image object
        """
        # Determine API Key
        api_key_to_use = gemini_api_key if gemini_api_key else self.api_key
        
        # Load Image
        if isinstance(image_input, (str, os.PathLike)):
            img = Image.open(image_input)
        else:
            img = Image.open(image_input)

        # Apply "Nano Banana" (Background Removal)
        if remove_bg:
            img = remove(img)

        # Convert to RGB if saving as JPEG (rembg outputs RGBA)
        if output_format.upper() in ["JPEG", "JPG"] and img.mode == "RGBA":
            background = Image.new("RGB", img.size, (255, 255, 255))
            background.paste(img, mask=img.split()[3]) # 3 is the alpha channel
            img = background
        
        # GEMINI INTEGRATION
        # Since standard Gemini Flash doesn't edit pixels directly, we use it to generate
        # a caption/marketing text and overlay it, OR analyze quality.
        # User request: "manage image quality and text on the product image"
        if gemini_prompt and api_key_to_use:
            try:
                client = genai.Client(api_key=api_key_to_use)
                
                # Ask Gemini for marketing text or analysis based on the prompt
                # We send the processed image (or original) to get context
                # STRICT PROMPT to ensure only one slogan is returned
                response = client.models.generate_content(
                    model='gemini-2.5-flash',
                    contents=[
                    gemini_prompt + " Create ONE short, punchy marketing slogan (max 6 words). Return ONLY the slogan text. Do not number it. Do not include 'Here is a slogan'. Do not use markdown bolding.",
                    img
                ])
                
                generated_text = response.text.strip()
                # Clean up potential markdown or quotes
                generated_text = generated_text.replace("*", "").replace('"', '').replace("'", "")
                
                # Overlay the generated text
                draw = ImageDraw.Draw(img)
                
                # Load a better font
                font_size = int(img.height / 20)
                try:
                    # Try common system fonts or a local font if available
                    font_options = ["Arial.ttf", "Roboto-Bold.ttf", "DejaVuSans-Bold.ttf", "LiberationSans-Bold.ttf"]
                    font = None
                    for font_name in font_options:
                        try:
                            font = ImageFont.truetype(font_name, font_size)
                            break
                        except:
                            continue
                    if not font:
                         font = ImageFont.load_default()
                except:
                    font = ImageFont.load_default()

                # Text Wrapping Logic
                lines = []
                words = generated_text.split()
                current_line = []
                
                # Estimate char width (approximate for variable width fonts)
                # This is a simple heuristic; for perfect wrapping use getlength if available in newer PIL
                max_width = img.width * 0.9
                
                for word in words:
                    current_line.append(word)
                    line_str = " ".join(current_line)
                    bbox = draw.textbbox((0, 0), line_str, font=font)
                    if (bbox[2] - bbox[0]) > max_width:
                        current_line.pop()
                        lines.append(" ".join(current_line))
                        current_line = [word]
                if current_line:
                    lines.append(" ".join(current_line))
                
                # Calculate total text height
                line_heights = []
                total_text_h = 0
                for line in lines:
                    bbox = draw.textbbox((0, 0), line, font=font)
                    h = bbox[3] - bbox[1]
                    line_heights.append(h)
                    total_text_h += h + 5 # 5px line spacing

                # Draw Text and Background
                y_text = img.height - total_text_h - 40 # 40px padding from bottom
                
                for i, line in enumerate(lines):
                    bbox = draw.textbbox((0, 0), line, font=font)
                    text_w = bbox[2] - bbox[0]
                    x_text = (img.width - text_w) / 2
                    
                    # Draw semi-transparent background box for readability
                    padding = 10
                    overlay = Image.new('RGBA', img.size, (0,0,0,0))
                    draw_overlay = ImageDraw.Draw(overlay)
                    draw_overlay.rectangle(
                        [x_text - padding, y_text - padding, x_text + text_w + padding, y_text + line_heights[i] + padding],
                        fill=(0, 0, 0, 128)
                    )
                    img = Image.alpha_composite(img.convert('RGBA'), overlay)
                    
                    # Draw text
                    draw = ImageDraw.Draw(img) # Re-init draw on new image
                    draw.text((x_text, y_text), line, font=font, fill="white")
                    
                    y_text += line_heights[i] + 5
                
                if output_format.upper() in ["JPEG", "JPG"]:
                     img = img.convert("RGB") # Convert back if needed for JPEG
                
            except Exception as e:
                print(f"Gemini Processing Failed: {e}")

        # Resize
        if resize_dim:
            img = img.resize(resize_dim, Image.Resampling.LANCZOS)

        # Enhance (Simple "Professional" Polish)
        if enhance:
            enhancer = ImageEnhance.Color(img)
            img = enhancer.enhance(1.2) # Slight saturation boost
            enhancer = ImageEnhance.Contrast(img)
            img = enhancer.enhance(1.1) # Slight contrast boost

        return img

    def save_image(self, img, output_path, format):
        img.save(output_path, format=format)
