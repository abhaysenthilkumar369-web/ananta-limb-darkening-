import os
import hashlib
from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.concurrency import run_in_threadpool
import logging

# Set up structured logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger("ananta-backend")

app = FastAPI(title="ANANTA Limb Darkening Analyser", version="1.0.0")

# CORS middleware for frontend interaction
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Adjust in production
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["*"],
)

# In-memory cache for radial extraction to avoid re-processing the same image
# Dictionary mapping: sha256_hash_of_image -> (mu_array, I_normalized_array)
IN_MEMORY_CACHE = {}

def process_and_fit(image_bytes: bytes, model_type: str):
    """
    CPU-bound function to process the image and fit the model.
    Executed in a threadpool.
    """
    import numpy as np
    from image_processing import preprocess_image
    from disk_detection import detect_stellar_disk
    from radial_analysis import extract_radial_profile

    # 1. Validation & Cache Check
    img_hash = hashlib.sha256(image_bytes).hexdigest()
    
    if img_hash in IN_MEMORY_CACHE:
        logger.info(f"Cache hit for image {img_hash}. Reusing extracted radial profile.")
        mu_arr, I_norm_arr = IN_MEMORY_CACHE[img_hash]
    else:
        logger.info(f"Extracting radial profile for new image {img_hash}.")
        # 2. Preprocessing
        processed_img = preprocess_image(image_bytes)
        
        # 3. Disk Detection
        cx, cy, radius = detect_stellar_disk(processed_img)
        
        # 4. Radial Profile Extraction
        mu_arr, I_norm_arr = extract_radial_profile(processed_img, cx, cy, radius)
        
        # Cache the arrays
        IN_MEMORY_CACHE[img_hash] = (mu_arr, I_norm_arr)
    
    # 5. Model Fitting
    # Implementation depends on the chosen model_type
    # from limb_models import fit_model
    # results = fit_model(mu_arr, I_norm_arr, model_type)
    
    # Mock return for scaffolding
    return {
        "status": "success",
        "model_type": model_type,
        "message": "Analysis completed.",
        "coefficients": [0.6],
        "r_squared": 0.98,
        "reduced_chi_square": 1.05
    }

@app.post("/analyze")
async def analyze_limb_darkening(
    image: UploadFile = File(...),
    model_type: str = Form(...)
):
    """
    Main endpoint for analyzing stellar images.
    """
    valid_models = ["linear", "quadratic", "square-root", "logarithmic", "claret", "compare"]
    if model_type.lower() not in valid_models:
        logger.error(f"Invalid model_type requested: {model_type}")
        raise HTTPException(status_code=400, detail=f"Invalid model_type. Must be one of {valid_models}")
    
    if not image.filename.lower().endswith(('.png', '.jpg', '.jpeg', '.fits')):
        raise HTTPException(status_code=400, detail="Invalid file format. Only PNG, JPEG, and FITS allowed.")

    try:
        image_bytes = await image.read()
        logger.info(f"Received request to analyze {image.filename} with model {model_type}.")
        
        # Run CPU-heavy tasks in a thread pool to avoid blocking the event loop
        results = await run_in_threadpool(process_and_fit, image_bytes, model_type.lower())
        
        return JSONResponse(content=results)
    
    except Exception as e:
        logger.exception("Analysis failed during request handling.")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
def health_check():
    return {"status": "ok", "service": "ANANTA Limb Darkening Analyser"}

@app.post("/download_report")
async def download_report(
    image: UploadFile = File(...),
    model_type: str = Form(...)
):
    """
    Separate endpoint to re-run or fetch the analysis quickly and stream a PDF file directly.
    """
    valid_models = ["linear", "quadratic", "square-root", "logarithmic", "claret", "compare"]
    if model_type.lower() not in valid_models:
        raise HTTPException(status_code=400, detail="Invalid model_type.")
        
    try:
        image_bytes = await image.read()
        logger.info(f"Generating PDF report for {image.filename} with {model_type}.")
        
        # 1. Processing and Fits
        import numpy as np
        from image_processing import preprocess_image
        from disk_detection import detect_stellar_disk
        from radial_analysis import extract_radial_profile
        from fitting_engine import fit_model, fit_all_models
        from report_generator import build_pdf_report
        
        # Use Cache if available
        img_hash = hashlib.sha256(image_bytes).hexdigest()
        if img_hash in IN_MEMORY_CACHE:
            mu_arr, I_norm_arr = IN_MEMORY_CACHE[img_hash]
        else:
            processed = preprocess_image(image_bytes)
            cx, cy, r = detect_stellar_disk(processed)
            mu_arr, I_norm_arr = extract_radial_profile(processed, cx, cy, r)
            IN_MEMORY_CACHE[img_hash] = (mu_arr, I_norm_arr)
            
        # 2. Get Fitting Results
        if model_type.lower() == "compare":
            results = fit_all_models(mu_arr, I_norm_arr)
        else:
            results = [fit_model(mu_arr, I_norm_arr, model_type.lower())]
            
        # 3. Build PDF in a thread to prevent blocking
        pdf_bytes_io = await run_in_threadpool(build_pdf_report, mu_arr, I_norm_arr, results)
        
        # Return StreamingResponse
        from fastapi.responses import StreamingResponse
        return StreamingResponse(
            pdf_bytes_io, 
            media_type="application/pdf",
            headers={"Content-Disposition": f"attachment; filename=ANANTA_Limb_Darkening_Report_{model_type}.pdf"}
        )
    except Exception as e:
        logger.exception("PDF report generation failed.")
        raise HTTPException(status_code=500, detail=f"PDF generation failed: {str(e)}")
