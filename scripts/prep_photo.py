import sys
import os

def prep_photo_with_fallback(input_path, output_path="source-prepped.png"):
    if not os.path.exists(input_path):
        print(f"Error: Input file {input_path} does not exist.")
        sys.exit(1)
        
    try:
        import cv2
        import numpy as np
        from PIL import Image
        from rembg import remove
        from io import BytesIO
        
        print("Removing background using rembg...")
        with open(input_path, 'rb') as f:
            input_data = f.read()
            subject_data = remove(input_data)
            
        rgba_img = Image.open(BytesIO(subject_data)).convert("RGBA")
        
        # Convert RGB to OpenCV grayscale format
        # Note: rembg sets alpha to 0 for background, but the RGB channels still contain the original image data,
        # which is perfect because we want to run CLAHE before compositing onto white.
        rgb_img = rgba_img.convert("RGB")
        open_cv_image = np.array(rgb_img)
        bgr_img = open_cv_image[:, :, ::-1].copy()
        gray = cv2.cvtColor(bgr_img, cv2.COLOR_BGR2GRAY)
        
        # Apply CLAHE on the grayscale image containing original details (without flat background interference)
        print("Applying CLAHE contrast enhancement...")
        clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8, 8))
        clahe_img = clahe.apply(gray)
        
        # Normalize the subject pixels to full 0-255 range to capture details
        alpha_np = np.array(rgba_img.split()[-1]) # Alpha channel
        subject_mask = alpha_np > 10
        
        if np.any(subject_mask):
            print("Normalizing subject brightness range to enhance facial features...")
            subject_pixels = clahe_img[subject_mask]
            min_val = np.min(subject_pixels)
            max_val = np.max(subject_pixels)
            
            # Stretch contrast of the subject
            if max_val > min_val:
                normalized = (clahe_img.astype(float) - min_val) / (max_val - min_val) * 255
                normalized = np.clip(normalized, 0, 255).astype(np.uint8)
            else:
                normalized = clahe_img
        else:
            normalized = clahe_img
            
        # Composite onto a pure white background
        # Pixels outside the subject mask become 255 (white background, maps to spaces in ASCII)
        prepped = np.where(subject_mask, normalized, 255).astype(np.uint8)
        
        # Save output
        dir_name = os.path.dirname(output_path)
        if dir_name:
            os.makedirs(dir_name, exist_ok=True)
        cv2.imwrite(output_path, prepped)
        print(f"Prepped image saved to {output_path}")
        
    except ImportError as e:
        print(f"Libraries missing for advanced processing: {e}")
        print("Falling back to pure Pillow (no background removal, basic contrast boost)...")
        from PIL import Image, ImageOps, ImageEnhance
        
        # Fallback processing
        img = Image.open(input_path).convert("L") # Grayscale
        # Boost contrast
        enhancer = ImageEnhance.Contrast(img)
        img_contrast = enhancer.enhance(2.0)
        # Equalize histogram
        prepped = ImageOps.equalize(img_contrast)
        
        dir_name = os.path.dirname(output_path)
        if dir_name:
            os.makedirs(dir_name, exist_ok=True)
        prepped.save(output_path)
        print(f"Fallback prepped image saved to {output_path}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python prep_photo.py <path_to_source_photo> [path_to_output]")
        sys.exit(1)
        
    inp = sys.argv[1]
    out = sys.argv[2] if len(sys.argv) > 2 else "source-prepped.png"
    prep_photo_with_fallback(inp, out)
