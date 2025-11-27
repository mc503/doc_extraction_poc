# Spektr - Document Extraction Walkthrough (macOS Guide)

Welcome to **Spektr**! This application allows you to extract structured data from documents (PDFs and Images) using the power of AI (OpenAI GPT-4o).

This guide is designed for **macOS users** setting up their machine from scratch.

## 1. Prerequisites & System Setup

If you have a fresh Mac, you might need to install a few tools first.

### Step 1: Install Homebrew
Homebrew is the standard package manager for macOS. It allows you to easily install other software.

1.  Open your **Terminal** (Command + Space, type "Terminal", and hit Enter).
2.  Check if you have Homebrew installed by typing:
    ```bash
    brew --version
    ```
3.  **If it says "command not found"**, copy and paste this command into your terminal and hit Enter:
    ```bash
    /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
    ```
    *Follow the on-screen instructions (you may need to enter your Mac password).*

### Step 2: Install Python
macOS comes with a system Python, but it's best to install a fresh version for development.

1.  In your terminal, run:
    ```bash
    brew install python
    ```
2.  Verify it's installed:
    ```bash
    python3 --version
    ```



### Step 4: Get an OpenAI API Key
You need a valid API key from OpenAI to power the extraction engine.
*   Go to [platform.openai.com/api-keys](https://platform.openai.com/api-keys).
*   Sign up/Log in and create a new secret key.
*   **Copy it immediately** (you won't be able to see it again).

## 2. Project Installation

Now that your system is ready, let's set up the Spektr project.

### Step 1: Navigate to the project directory
In your terminal, navigate to the folder where you have this code.
*(Tip: You can type `cd ` (with a space) and then drag the folder from Finder into the terminal window).*

```bash
cd /path/to/doc_extraction_poc
```

### Step 2: Create a Virtual Environment
This keeps the project's libraries separate from your system.

```bash
python3 -m venv venv
```

### Step 3: Activate the Virtual Environment
You need to do this every time you open a new terminal to work on this project.

```bash
source venv/bin/activate
```
*(You should see `(venv)` appear at the start of your command prompt).*

### Step 4: Install Dependencies
Install the required libraries.

```bash
pip3 install -r requirements.txt
```

## 3. Configuration

1.  Find the file named `.env.example` in the project folder.
2.  Rename it to `.env`.
3.  Open `.env` in a text editor (like TextEdit, VS Code, or Nano).
4.  Paste your OpenAI API Key after the equals sign:

```env
OPENAI_API_KEY=sk-proj-xxxxxxxxxxxxxxxxxxxxxxxx
```

## 4. Running the Application

Now you are ready to launch Spektr!

1.  Ensure your virtual environment is active (look for `(venv)`).
2.  Run the command:

```bash
python3 -m streamlit run app.py
```

This will automatically open the application in your default web browser (usually at `http://localhost:8501`).

## 5. Using Spektr

1.  **Upload a Document**: Drag and drop a PDF or Image (PNG/JPG) into the "Upload & Extract" area.
2.  **Preview**: You will see a preview of the document on the right side.
3.  **Configure Fields (Optional)**:
    *   Open the sidebar (arrow on the top left if closed).
    *   You can see the "Active Fields" that will be extracted.
    *   You can **Add New Fields** or **Edit/Remove** existing ones.
4.  **Run Extraction**: Click the **✨ Run Extraction** button.
5.  **View & Download**:
    *   Wait a few seconds for the AI to process.
    *   The results will appear as a JSON object.
    *   Click **Download JSON** to save the data.

## Troubleshooting

*   **"command not found: brew"**: You might need to add Homebrew to your PATH. The installation script usually tells you how to do this at the end (look for "Next steps").

*   **OpenAI API Error**: Check your `.env` file and ensure you have credits in your OpenAI account.
