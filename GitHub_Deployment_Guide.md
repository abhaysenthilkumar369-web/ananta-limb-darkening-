# ANANTA Limb Darkening Analyser
## Hosting on GitHub & Deployment to Google Cloud Run

This document serves as the guide for connecting the codebase to GitHub and deploying the application as a production-grade scientific instrument on Google Cloud Run.

### 1. Repository Structure
The project is strictly separated into `frontend/` (React+Vite) and `backend/` (FastAPI).

### 2. Pushing to GitHub
If you haven't already initialized git:
```bash
git init
git add .
git commit -m "Initial commit of ANANTA Analyser"
git branch -M main
git remote add origin https://github.com/USERNAME/REPO_NAME.git
git push -u origin main
```

### 3. Google Cloud Run Deployment
Because the tool relies on heavy image processing and fitting, it needs sufficient memory allocated.

1. Ensure the `Dockerfile` is at `backend/Dockerfile`
2. Use the Google Cloud CLI (`gcloud`) or the Console.
3. Deploy command:
```bash
cd backend
gcloud run deploy ananta-backend \
  --source . \
  --region us-central1 \
  --allow-unauthenticated \
  --memory 1Gi \
  --cpu 1 \
  --timeout 300s \
  --min-instances 0 \
  --max-instances 10
```

### 4. Updating the Frontend
Once Cloud Run provides a URL (e.g., `https://ananta-backend-...-uc.a.run.app`), you must update the frontend React application to point to the live server.

In `frontend/.env`:
`VITE_API_URL=https://ananta-backend-...-uc.a.run.app`

Build the frontend for production:
```bash
cd frontend
npm ci
npm run build
```

You can then host the `dist/` directory via Firebase Hosting, Vercel, or GitHub Pages.

### 5. Debugging Production Issues
To intercept backend logs (which are structured internally using `logging.getLogger`):
```bash
gcloud logs tail --service=ananta-backend
```
Look for `Analysis failed` or `Exception` to trace CORS, missing CV2 dependencies, or out-of-bounds math errors.
