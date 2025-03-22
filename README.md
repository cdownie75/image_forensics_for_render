
# Image Forensics API (Render Deployment)

This project contains:
- Flask API for image analysis
- Pipeline that scans images for manipulation
- Render-ready `render.yaml` config

## Deploy to Render

1. Push this folder to a GitHub repo.
2. Go to https://render.com/new/web
3. Connect your repo and deploy.

Make sure `start command` is:
```
gunicorn image_analysis_api:app
```

## Endpoints

- `POST /upload` — Upload a new image
- `POST /analyze` — Run pipeline
- `GET /report` — Get forensic report
- `GET /images/<filename>` — Get individual image
