# Deployment Guide

## Deploying to Streamlit Community Cloud
1. Create a new GitHub repository for this project.
2. Push this project to GitHub.
3. Sign in to https://share.streamlit.io using GitHub.
4. Click **New app**.
5. Choose your repository, branch, and set the main file to `app.py`.
6. Add the required secrets in Streamlit Cloud settings:
   - `OPENAI_API_KEY`
   - `GROQ_API_KEY`
   - `SARVAM_API_KEY`
   - `GEMINI_API_KEY`
7. Deploy and open the live preview link.

## Deploying locally with Streamlit
```bash
python -m venv venv
venv\Scripts\activate    # Windows
pip install -r requirements.txt
streamlit run app.py
```

Open `http://localhost:8501`.

## Deploying with Docker
```bash
docker build -t compliance-assistant .
docker run -p 8501:8501 compliance-assistant
```

## Notes on this repository
- This repository contains both a Python Streamlit app and a separate React/Node frontend.
- For Streamlit deployment, use the Python app at `app.py` and `requirements.txt`.
- If you want to deploy the alternate React app, use `npm install` and `npm run build`.

## GitHub push checklist
1. Initialize git in this folder if needed:
   ```bash
git init
git add .
git commit -m "Initial commit"
```
2. Add your GitHub remote:
   ```bash
git remote add origin https://github.com/<your-username>/<your-repo>.git
```
3. Push the repository:
   ```bash
git branch -M main
git push -u origin main
```

## What you need to submit
- GitHub repository URL
- Streamlit live deployment URL
- Demo video link (2–5 minutes)
- README with setup, architecture, AI/ML approach, challenges, and future improvements
