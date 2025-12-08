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

### Option A: Using `.env` file (Local Development)

1.  Find the file named `.env.example` in the project folder.
2.  Rename it to `.env`.
3.  Open `.env` in a text editor (like TextEdit, VS Code, or Nano).
4.  Paste your OpenAI API Key after the equals sign:

```env
OPENAI_API_KEY=sk-proj-xxxxxxxxxxxxxxxxxxxxxxxx
```

### Option B: Using Streamlit Secrets (Local or Cloud)

You can also use Streamlit's built-in secrets management, which works both locally and on Streamlit Community Cloud:

1.  Navigate to the `.streamlit` folder in the project directory.
2.  Copy `.streamlit/secrets.toml.example` to `.streamlit/secrets.toml`.
3.  Open `.streamlit/secrets.toml` and paste your API key:

```toml
OPENAI_API_KEY = "sk-proj-xxxxxxxxxxxxxxxxxxxxxxxx"
```

> **Note:** Both methods work. The app will check Streamlit secrets first, then fall back to `.env` if not found.

## 4. Running the Application

Now you are ready to launch Spektr!

1.  Ensure your virtual environment is active (look for `(venv)`).
2.  Run the command:

```bash
python3 -m streamlit run app.py
```

This will automatically open the application in your default web browser (usually at `http://localhost:8501`).

### Manual Verification Steps
To verify the changes yourself:
1.  **Run the App**: `streamlit run app.py`
2.  **Check Templates**: Confirm "AML" is selected and fields are populated.
3.  **Reasoning V2 (Generalized)**:
    -   Run extraction on a field like "is_ai_generated" or create a new one like "authenticity_check".
    -   Verify that the reasoning does *not* cite "professional formatting" or "legal language" as a reason for human authorship.
    -   It should focus on specific details, inconsistencies, or lack thereof.
4.  **Save Template**:
    -   Add some fields.
    -   Enter a name in "Save as Template" and click Save.
    -   Refresh or switch templates to verify persistence (in session).

### Fix Verification (v4.2)
1.  **Sidebar Visibility**: Check that input text in the sidebar is now black and clearly visible against the background.
2.  **Template Management**:
    -   **Save Changes**: Modify the "AML" template (add a field), click "Save Changes", switch to another template and back. The change should persist.
    -   **Delete**: Create a dummy template, select it, and click "Delete". It should disappear.
    -   **No Errors**: Verify that saving/deleting does not trigger "Calling st.rerun() within a callback" errors.
3.  **Reasoning Logic**:
    -   The AI is now instructed to look for specific artifacts (hallucinations, empty grammar) when determining if a document is AI-generated.

### Refinement Verification (v4.3)
1.  **Conditional Save**:
    -   Load a template. The "Save Changes" button should be disabled/hidden or show "Saved".
    -   Modify a field. The "Save Changes" button should become active.
    -   Save. The button should revert to "Saved".
### Final Polish Verification (v4.4)
1.  **Button Visibility**:
    -   Verify that "Save Changes" and "Delete" buttons have black text on a readable background in their default state.
    -   Verify that hovering over them maintains readability (black text).
    -   Verify that they look consistent with "Add Field" and "Remove Field".
    -   *Note*: Help tooltips were removed from these buttons to ensure consistent styling.
2.  **Custom Field Reasoning**:
    -   Add a new field using the "Add New Field" form.
    -   Check "Include Reasoning".
    -   Verify that the new field appears in "Active Fields" with the "Include Reasoning" checkbox checked.
    -   Run extraction and verify the output includes reasoning for this custom field.
3.  **State Tracking**:
    -   **Include Reasoning**: Toggle "Include Reasoning" for an active field. The "Save Changes" button should immediately become active.
    -   **Revert Changes**: Modify a field name (Save Changes appears), then change it back to the original name. The "Save Changes" button should revert to "Saved".
4.  **New Templates**:
    -   **AML**: Verify it now includes fields like "roles_responsibilities", "risk_appetite", etc.
    -   **BRA**: Verify there is a new "BRA" template in the dropdown, containing the common fields plus "customer_risk_assessment", "geographical_risk", etc.
5.  **Ownership Analysis**:
    -   Select the "Ownership" template.
    -   **Verify Field Type**: Ensure the "ownership_graph" field shows "Ownership Graph" as its type in the sidebar (not Boolean).
    -   Upload an ownership chart (e.g., an image of a corporate structure).
    -   Run extraction.
    -   Verify the output JSON contains a list of nodes with `spektrId`, `details` (including `company_name`, `ownership`, `isBeneficiary`), and `adj` (adjacency list) representing the graph structure.
    -   Verify that it captures the complex relationships as shown in the example.

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

## 6. Deploying to Streamlit Community Cloud

To share Spektr with your team, you can deploy it to Streamlit Community Cloud for free:

### Prerequisites
1.  Push your code to a GitHub repository.
2.  **Important:** Make sure `.env` and `.streamlit/secrets.toml` are in your `.gitignore` (they already are if you're using the provided `.gitignore` file).

### Deployment Steps
1.  Go to [share.streamlit.io](https://share.streamlit.io).
2.  Sign in with your GitHub account.
3.  Click **"New app"**.
4.  Select your repository, branch, and set the main file to `app.py`.
5.  Click **"Advanced settings"** and add your secrets:
    ```toml
    OPENAI_API_KEY = "sk-proj-your-actual-key-here"
    ```
6.  Click **"Deploy"**.

Your app will be live in a few minutes and accessible via a public URL that you can share with your team!

### Updating Secrets on Streamlit Cloud
If you need to update your API key later:
1. Go to your app's settings on [share.streamlit.io](https://share.streamlit.io).
2. Navigate to **"Secrets"** section.
3. Update the `OPENAI_API_KEY` value.
4. Save and reboot the app.

## Troubleshooting

*   **"command not found: brew"**: You might need to add Homebrew to your PATH. The installation script usually tells you how to do this at the end (look for "Next steps").

*   **OpenAI API Error**: Check your `.env` file or `.streamlit/secrets.toml` and ensure you have credits in your OpenAI account.

