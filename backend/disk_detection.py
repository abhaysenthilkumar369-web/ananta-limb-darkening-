import cv2
import numpy as np

def detect_stellar_disk(processed_img: np.ndarray):
    """
    Finds the center (cx, cy) and radius of the stellar disk using Hough Circles
    layered with Canny edge detection. Fallback to contour detection if circles fail.
    """
    # 1. Primary Method: Hough Circle Transform
    # DP=1 (resolution ratio), minDist=img_height/2 (expect 1 main star)
    # param1: Canny high threshold, param2: accumulator threshold
    circles = cv2.HoughCircles(
        processed_img,
        cv2.HOUGH_GRADIENT,
        dp=1,
        minDist=processed_img.shape[0] // 2,
        param1=50,
        param2=30,
        minRadius=processed_img.shape[0] // 8,
        maxRadius=processed_img.shape[0] // 2
    )

    if circles is not None and len(circles) > 0:
        circles = np.uint16(np.around(circles))
        largest_circle = max(circles[0, :], key=lambda c: c[2])
        cx, cy, r = largest_circle[0], largest_circle[1], largest_circle[2]
        return cx, cy, r

    # 2. Fallback Method: Contour detection + Minimum Enclosing Circle
    # Apply Otsu's thresholding
    _, thresh = cv2.threshold(processed_img, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    
    # Find contours
    contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    if not contours:
        raise ValueError("No stellar disk detected in the image.")
        
    # Get the largest contour by area
    largest_contour = max(contours, key=cv2.contourArea)
    
    # Fit a circle
    (x, y), radius_float = cv2.minEnclosingCircle(largest_contour)
    
    if radius_float < 10:
        raise ValueError("Detected object is too small to be a stellar disk.")
        
    return int(x), int(y), int(radius_float)
