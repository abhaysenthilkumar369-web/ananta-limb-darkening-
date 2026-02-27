import cv2
import numpy as np
import io
from PIL import Image

def preprocess_image(image_bytes: bytes) -> np.ndarray:
    """
    Decodes the uploaded image bytes, converts to grayscale, applies CLAHE,
    Gaussian smoothing, and median filtering to prepare for disk detection.
    """
    # Convert bytes to numpy array
    nparr = np.frombuffer(image_bytes, np.uint8)
    img_cv = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    
    if img_cv is None:
        raise ValueError("Could not decode image bytes.")
        
    # Convert RGB to grayscale
    gray = cv2.cvtColor(img_cv, cv2.COLOR_BGR2GRAY)
    
    # Adaptive histogram equalization (CLAHE)
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
    enhanced = clahe.apply(gray)
    
    # Gaussian smoothing to remove high-frequency noise
    smoothed = cv2.GaussianBlur(enhanced, (5, 5), 0)
    
    # Median filtering to remove salt-and-pepper noise
    filtered = cv2.medianBlur(smoothed, 5)
    
    # Optional saturation masking: Ignore pixels > 95% intensity (242 out of 255)
    # For extraction later, we just need a clean image to find the disk center.
    return filtered
