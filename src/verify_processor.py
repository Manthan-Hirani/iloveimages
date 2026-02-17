import os
from processor import ImageProcessor


def test_processor():
    print("Starting verification...")
    processor = ImageProcessor()
    
    # Check for images in current or parent directory
    if os.path.exists("test_images"):
        base_dir = "."
    elif os.path.exists("../test_images"):
        base_dir = ".."
    else:
        print("Error: test_images directory not found.")
        return

    input_path = os.path.join(base_dir, "test_images/products/shoes/1.png")
    output_dir = os.path.join(base_dir, "output")
    os.makedirs(output_dir, exist_ok=True)

    if not os.path.exists(input_path):
        print(f"Error: Test image not found at {input_path}")
        return

    # Test 1: Format Conversion (PNG -> JPEG)
    print("Test 1: Format Conversion (PNG -> JPEG)")
    try:
        img = processor.process_image(input_path, output_format="JPEG", remove_bg=False)
        output_path = os.path.join(output_dir, "test_conversion.jpg")
        processor.save_image(img, output_path, "JPEG")
        print(f"  Success: Saved to {output_path}")
    except Exception as e:
        print(f"  Failed: {e}")

    # Test 2: Background Removal ("Nano Banana")
    print("Test 2: Background Removal")
    try:
        img = processor.process_image(input_path, output_format="PNG", remove_bg=True)
        output_path = os.path.join(output_dir, "test_rembg.png")
        processor.save_image(img, output_path, "PNG")
        print(f"  Success: Saved to {output_path}")
    except Exception as e:
        print(f"  Failed: {e}")

    # Test 3: Verbose Format String (Simulating UI input)
    print("Test 3: Verbose Format String")
    try:
        verbose_format = "WEBP (Best for e-commerce)"
        selected_format = verbose_format.split()[0] # Logic from app.py
        img = processor.process_image(input_path, output_format=selected_format, remove_bg=False)
        output_path = os.path.join(output_dir, "test_verbose.webp")
        processor.save_image(img, output_path, selected_format)
        print(f"  Success: Saved to {output_path} using format {selected_format}")
    except Exception as e:
        print(f"  Failed: {e}")

if __name__ == "__main__":
    test_processor()
