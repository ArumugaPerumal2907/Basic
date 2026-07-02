# Setup Instructions

## 1. Prepare the repository
1. Create a new GitHub repository for this project.
2. Clone it locally or initialize a git repository inside this folder:

```bash
cd sensitive-data-compliance-assistant
git init
git add .
git commit -m "Initial commit"
```

3. Add the remote repository URL and push:

```bash
git remote add origin https://github.com/<your-username>/<your-repo>.git
git branch -M main
git push -u origin main
```

## 2. Run locally (Python/Streamlit)
This repository includes a Streamlit-based app at `app.py`.

```bash
python -m venv venv
venv\Scripts\activate      # Windows
# OR
source venv/bin/activate    # macOS/Linux

pip install -r requirements.txt
python -m spacy download en_core_web_sm
pip install git+https://github.com/sarvamai/python-sdk.git
streamlit run app.py
```

Open the app at `http://localhost:8501`.

## 3. Optional Node/React frontend build
This repository also includes a React + Node frontend, which can be built separately:

```bash
npm install
npm run build
```

## 4. Required environment variables
For full AI and OCR support, set:

- `OPENAI_API_KEY`
- `GROQ_API_KEY`
- `SARVAM_API_KEY`
- `GEMINI_API_KEY` (if using Gemini via the current Node backend)

You can also paste API keys into the UI if the app supports it.

## 5. Notes
- Detection and risk scoring work without API keys.
- Only AI summary, Q&A, and OCR for scanned documents require keys.
- Do not commit real API keys to GitHub.
