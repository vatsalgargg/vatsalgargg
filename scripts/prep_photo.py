import sys
import os

def prep_photo_with_fallback(input_path, output_path="source-prepped.png"):
    if not os.path.exists(input_path):
        print(f"Error: Input file {input_path} does not exist.")
        sys.exit(1)
        
    try:
        import cv2
        import numpy as np
        from PIL import Image, ImageEnhance
        from rembg import remove
        from io import BytesIO
        
        print("Removing background using rembg...")
        with open(input_path, 'rb') as f:
            input_data = f.read()
            subject_data = remove(input_data)
            
        rgba_img = Image.open(BytesIO(subject_data)).convert("RGBA")
        
        # Composite onto white background
        white_bg = Image.new("RGBA", rgba_img.size, (255, 255, 255, 255))
        composited = Image.alpha_composite(white_bg, rgba_img).convert("RGB")
        
        # Convert to OpenCV format (BGR)
        open_cv_image = np.array(composited)
        bgr_img = open_cv_image[:, :, ::-1].copy()
        
        # Convert to grayscale
        gray = cv2.cvtColor(bgr_img, cv2.COLOR_BGR2GRAY)
        
        # Apply CLAHE
        print("Applying CLAHE contrast enhancement...")
        clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8, 8))
        prepped = clahe.apply(gray)
        
        # Save output
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
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
        
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        prepped.save(output_path)
        print(f"Fallback prepped image saved to {output_path}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python prep_photo.py <path_to_source_photo> [path_to_output]")
        sys.exit(1)
        
    inp = sys.argv[1]
    out = sys.argv[2] if len(sys.argv) > 2 else "source-prepped.png"
    prep_photo_with_fallback(inp, out)
