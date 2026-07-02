# 🚀 HOW TO RUN THIS PROJECT - Complete Guide

This guide will get you from zero to running the app in **10 minutes**.

---

## 📋 Prerequisites (Check These First)

Before you start, make sure you have:

- ✅ **Python 3.8+** installed on your computer
- ✅ A **terminal/command prompt** (we'll use it to run commands)
- ✅ **~500MB free disk space** (for dependencies)

### Check if Python is installed:

**macOS / Linux:**
```bash
python3 --version
```

**Windows:**
```bash
python --version
```

You should see something like `Python 3.10.5` or higher.

**If not installed**, download from [python.org](https://www.python.org/downloads/) and install it.

---

## 🎯 STEP-BY-STEP INSTALLATION

### **STEP 1: Extract the Project**

1. Download `sensitive-data-compliance-assistant.zip` from the GitHub repo
2. Right-click → "Extract All" (or use your favorite unzip tool)
3. You now have a folder: `sensitive-data-compliance-assistant/`

**On your computer, it looks like:**
```
Desktop/
├── sensitive-data-compliance-assistant/  ← This folder
│   ├── app.py
│   ├── requirements.txt
│   ├── sample_data/
│   ├── README.md
│   └── (other .py files)
```

---

### **STEP 2: Open a Terminal in This Folder**

**macOS:**
```
1. Open Terminal (Cmd + Space, type "Terminal", hit Enter)
2. Type: cd ~/Desktop/sensitive-data-compliance-assistant
3. Press Enter
```

**Windows (PowerShell):**
```
1. Right-click the folder → "Open with PowerShell"
   OR
   Open PowerShell → type: cd C:\Users\YourName\Desktop\sensitive-data-compliance-assistant
2. Press Enter
```

**Windows (Command Prompt):**
```
1. Right-click the folder → "Open Command Prompt Here"
   OR
   cmd → cd C:\Users\YourName\Desktop\sensitive-data-compliance-assistant
2. Press Enter
```

**Linux:**
```bash
cd ~/Desktop/sensitive-data-compliance-assistant
```

✅ **You should now see:**
```
(base) user@computer sensitive-data-compliance-assistant %
```
Or on Windows:
```
PS C:\Users\YourName\Desktop\sensitive-data-compliance-assistant>
```

---

### **STEP 3: Create a Virtual Environment (IMPORTANT)**

This isolates the project's dependencies so they don't interfere with your system Python.

**macOS / Linux:**
```bash
python3 -m venv venv
source venv/bin/activate
```

**Windows (PowerShell):**
```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

**Windows (Command Prompt):**
```cmd
python -m venv venv
venv\Scripts\activate
```

✅ **Your terminal should now show:**
```
(venv) user@computer sensitive-data-compliance-assistant %
```
Notice the `(venv)` at the start — this means the virtual environment is **active**.

---

### **STEP 4: Upgrade pip**

Pip is Python's package manager. Let's make sure it's up to date:

```bash
pip install --upgrade pip
```

You'll see messages like:
```
Collecting pip
  Downloading pip-24.0-py3-none-any.whl (2.1 MB)
Installing collected packages: pip
Successfully installed pip-24.0
```

✅ Done!

---

### **STEP 5: Install All Dependencies**

This is the big one. It downloads and installs all the libraries the app needs.

```bash
pip install -r requirements.txt
```

**What you'll see:**
```
Collecting streamlit>=1.0.0
  Downloading streamlit-1.36.0-py2.py3-none-any.whl (8.9 MB)
Collecting pandas>=1.5.0
  Downloading pandas-2.2.0-cp311-cp311-win_amd64.whl (11.6 MB)
...
Successfully installed streamlit pandas pypdf openai numpy python-dotenv spacy python-docx openpyxl pytesseract Pillow pyarrow scikit-learn
```

This takes **2-5 minutes** depending on your internet speed. Lots of messages are normal.

✅ **Installation is complete when you see:**
```
Successfully installed ...
```

---

### **STEP 6: Run the App**

Now for the magic moment:

```bash
streamlit run app.py
```

**What happens next:**
```
  You can now view your Streamlit app in your browser.

  Local URL: http://localhost:8501
  Network URL: http://192.168.x.x:8501

  For better performance, install pyarrow: pip install --upgrade pyarrow

  (Press Ctrl+C to stop the server)
```

Your **web browser automatically opens** at `http://localhost:8501`

✅ **The app is now running!** You should see:
- A sidebar on the left with upload buttons
- 7 tabs: Overview, Findings, AI Summary, Ask Questions, Redacted View, Dashboard, Audit Log

---

## ✨ Testing the App (First Run)

### **Upload the Sample Document:**

1. In the **sidebar**, you'll see a file upload box
2. Click "Browse files"
3. Select: `sample_data/sample_document.txt`
4. The app **automatically scans** the file

### **What you'll see:**

**Overview Tab:**
```
Total Findings: 18
High Severity: 6
Medium Severity: 12
Overall Risk: High Risk
```

**Findings Tab:**
- List of detected PII (Aadhaar, PAN, emails, phone numbers, etc.)
- Each one shows context and position in the document

**Dashboard Tab:**
- Cross-document metrics
- Charts of sensitive data types

**Audit Log Tab:**
- Timestamped log of every action
- You can download as Excel/CSV

✅ **Everything working?** You're done! The app is fully functional.

---

## 🔑 Optional: Add AI Features

The app works perfectly **without API keys**. But if you want AI-powered summaries and chatbot Q&A:

### **Option A: Use OpenAI (Recommended for quality)**

1. Go to [platform.openai.com/api-keys](https://platform.openai.com/api-keys)
2. Sign up (free $5 trial credit)
3. Create a new API key (it starts with `sk-`)
4. Copy the key
5. In the app sidebar, paste it into **"OpenAI API Key"** box
6. Click the **"📝 AI Summary"** tab → **"Generate Summary"** button
7. Click the **"💬 Ask Questions"** tab → ask a question about the document

### **Option B: Use Groq (Faster & Cheaper)**

1. Go to [console.groq.com/keys](https://console.groq.com/keys)
2. Sign up (free account, very generous limits)
3. Create API key (starts with `gsk_`)
4. Copy the key
5. In the app sidebar, select **"Groq"** from the radio button
6. Paste the key into **"Groq API Key"** box
7. Same as above — summaries and Q&A work identically

---

## 🛑 Stopping the App

In your terminal, press:
```
Ctrl + C
```

You'll see:
```
Shutdown complete
(venv) user@computer sensitive-data-compliance-assistant %
```

---

## 🔄 Running It Again

Next time you want to run the app, just do:

```bash
# Navigate to the folder (if you closed the terminal)
cd ~/Desktop/sensitive-data-compliance-assistant

# Activate virtual environment
source venv/bin/activate          # macOS/Linux
# OR
.\venv\Scripts\Activate.ps1       # Windows PowerShell
# OR
venv\Scripts\activate             # Windows CMD

# Run the app
streamlit run app.py
```

---

## ⚠️ Common Issues & Fixes

### **Issue: "python3 not found" or "python not found"**
**Solution:** Install Python from [python.org](https://www.python.org/downloads)
- Make sure you check **"Add Python to PATH"** during installation
- Restart terminal after installing

---

### **Issue: "No module named streamlit"**
**Solution:** You probably skipped STEP 5. Run:
```bash
pip install -r requirements.txt
```

---

### **Issue: "Permission denied" on macOS/Linux**
**Solution:** Use `sudo` for the venv activation:
```bash
python3 -m venv venv
source venv/bin/activate
```
Or try with `python` instead of `python3`.

---

### **Issue: PowerShell says "cannot be loaded because running scripts is disabled"**
**Solution:** Open PowerShell as Administrator, then run:
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```
Then try `.\venv\Scripts\Activate.ps1` again.

---

### **Issue: Port 8501 is already in use**
**Solution:** Either close the other app using it, or run on a different port:
```bash
streamlit run app.py --server.port 8502
```

---

### **Issue: App opens but sidebar is blank**
**Solution:** Refresh the browser (Ctrl+R or Cmd+R)

---

### **Issue: Upload fails with "Unsupported file type"**
**Solution:** The app supports: PDF, TXT, MD, CSV, DOCX, XLSX, JSON, PNG, JPG, JPEG
Make sure your file has one of these extensions.

---

## 📚 What Each Tab Does

| Tab | What It Shows | Needs API Key? |
|-----|---------------|---|
| **Overview** | Risk level, finding counts, bar chart | ❌ No |
| **Findings** | List of all detected PII with context | ❌ No |
| **AI Summary** | Compliance observations & risks (AI-generated) | ✅ OpenAI/Groq |
| **Ask Questions** | Chat with the document using natural language | ✅ OpenAI/Groq |
| **Redacted View** | Document with sensitive values masked | ❌ No |
| **Dashboard** | Cross-document metrics & aggregations | ❌ No |
| **Audit Log** | Timestamped log of every action | ❌ No |

---

## 🎓 Learning Resources

- **Streamlit docs**: [streamlit.io/docs](https://streamlit.io/docs)
- **Python beginners**: [python.org/about/gettingstarted](https://www.python.org/about/gettingstarted/)
- **Virtual environments**: [docs.python.org/3/tutorial/venv.html](https://docs.python.org/3/tutorial/venv.html)

---

## ✅ Checklist: You're Ready When...

- [x] Python 3.8+ is installed
- [x] Project is extracted
- [x] Terminal is open in the project folder
- [x] Virtual environment is activated (you see `(venv)` in the prompt)
- [x] `pip install -r requirements.txt` completed successfully
- [x] `streamlit run app.py` started the app
- [x] Browser opened to `http://localhost:8501`
- [x] You uploaded `sample_document.txt` and saw results

---

## 🎉 Next Steps

1. **Play with the sample document** — upload it, explore all 7 tabs
2. **Upload your own files** — PDF, CSV, DOCX, XLSX, JSON, TXT, images
3. **Add an API key** (optional) — enable AI summaries and Q&A chat
4. **Push to GitHub** — when ready to submit
5. **Deploy to Streamlit Cloud** — share the live app with anyone

---

**You're all set! Happy scanning! 🛡️**

If you hit any errors, check the "Common Issues" section above, or open an issue on GitHub.
