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
        
        # Load original image
        print(f"Loading {input_path}...")
        orig_img = Image.open(input_path).convert("RGBA")
        
        # Run background removal first on the full image to locate the subject
        print("Locating subject using rembg to find bounding box...")
        buffer = BytesIO()
        orig_img.save(buffer, format="PNG")
        orig_data = buffer.getvalue()
        
        subject_data = remove(orig_data)
        rgba_img = Image.open(BytesIO(subject_data)).convert("RGBA")
        
        # Get alpha channel as numpy array to find non-transparent pixels
        alpha_np = np.array(rgba_img.split()[-1])
        y_indices, x_indices = np.where(alpha_np > 10)
        
        if len(x_indices) > 0 and len(y_indices) > 0:
            min_x, max_x = np.min(x_indices), np.max(x_indices)
            min_y, max_y = np.min(y_indices), np.max(y_indices)
            
            subject_w = max_x - min_x
            subject_h = max_y - min_y
            center_x = (min_x + max_x) // 2
            
            print(f"Subject bounding box: X={min_x}..{max_x}, Y={min_y}..{max_y} (size {subject_w}x{subject_h})")
            
            # Crop to head and shoulders:
            # We take from the top of the subject (min_y) down to 45% of the subject height
            crop_h = int(subject_h * 0.45)
            # Make crop width roughly 1.1 times the crop height for a nice frame
            crop_w = int(crop_h * 1.1)
            
            x1 = max(0, center_x - crop_w // 2)
            y1 = max(0, min_y)
            x2 = min(orig_img.width, center_x + crop_w // 2)
            y2 = min(orig_img.height, min_y + crop_h)
            
            print(f"Cropping head and shoulders: ({x1}, {y1}) to ({x2}, {y2})")
            cropped_img = orig_img.crop((x1, y1, x2, y2))
        else:
            print("Subject not found. Falling back to upper-center crop...")
            width, height = orig_img.size
            crop_w = int(width * 0.8)
            crop_h = int(height * 0.7)
            x1 = (width - crop_w) // 2
            y1 = int(height * 0.05)
            x2 = x1 + crop_w
            y2 = y1 + crop_h
            cropped_img = orig_img.crop((x1, y1, x2, y2))
            
        # Run background removal again on the cropped headshot
        print("Removing background on cropped headshot...")
        buffer = BytesIO()
        cropped_img.save(buffer, format="PNG")
        cropped_data = buffer.getvalue()
        
        cropped_subject_data = remove(cropped_data)
        rgba_img = Image.open(BytesIO(cropped_subject_data)).convert("RGBA")
        
        # Convert RGB channels to grayscale for CLAHE
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
