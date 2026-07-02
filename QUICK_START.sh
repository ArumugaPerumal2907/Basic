#!/usr/bin/env bash
# QUICK START GUIDE - Sensitive Data Detection & Compliance Assistant
# =====================================================================
# Follow these steps in order. Copy & paste each command one at a time.

# ✅ STEP 1: Download the project
# =============================
# Go to: https://github.com/<your-username>/sensitive-data-compliance-assistant
# Click green "Code" button → "Download ZIP"
# Unzip the file to your Desktop or Downloads folder
# You should see a folder named: sensitive-data-compliance-assistant


# ✅ STEP 2: Open Terminal and navigate to the project
# ======================================================
# macOS / Linux:
cd ~/Desktop/sensitive-data-compliance-assistant
# OR if it's in Downloads:
cd ~/Downloads/sensitive-data-compliance-assistant

# Windows (PowerShell):
cd C:\Users\<YourUsername>\Desktop\sensitive-data-compliance-assistant
# OR
cd C:\Users\<YourUsername>\Downloads\sensitive-data-compliance-assistant


# ✅ STEP 3: Check Python is installed
# =====================================
python3 --version
# Expected output: Python 3.8+ or higher
# If error "python3 not found", try: python --version


# ✅ STEP 4: Create a virtual environment (HIGHLY RECOMMENDED)
# =============================================================
# macOS / Linux:
python3 -m venv venv
source venv/bin/activate

# Windows (Command Prompt):
python -m venv venv
venv\Scripts\activate

# Windows (PowerShell):
python -m venv venv
.\venv\Scripts\Activate.ps1
# If you get a permission error, run PowerShell as Administrator first


# ✅ STEP 5: Upgrade pip (important for Windows)
# ================================================
pip install --upgrade pip


# ✅ STEP 6: Install all dependencies
# =====================================
pip install -r requirements.txt
# This takes 2-3 minutes. You'll see lots of messages. That's normal.
# Wait until you see: "Successfully installed ..."


# ✅ STEP 7: Run the Streamlit app
# ==================================
streamlit run app.py
# The app opens automatically in your browser at: http://localhost:8501


# 🎉 YOU'RE DONE! The app is now running.
# ========================================
# See the next section for what to do next.
