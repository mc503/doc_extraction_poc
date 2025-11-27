import streamlit as st
import pandas as pd
from PIL import Image
import io
import pypdfium2 as pdfium

from backend import DocumentProcessor, FieldDefinition, FieldType, FieldLength

# Page Config
st.set_page_config(
    page_title="Spektr Document OCR",
    page_icon="🔮",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Apple-Inspired Liquid Glass CSS
st.markdown("""
<style>
    /* ============================================
       TYPOGRAPHY & GLOBAL STYLES
       ============================================ */
    
    @import url('https://fonts.googleapis.com/css2?family=SF+Pro+Display:wght@300;400;500;600;700&display=swap');
    
    html, body, [class*="css"] {
        font-family: -apple-system, BlinkMacSystemFont, 'SF Pro Display', 'Segoe UI', 'Helvetica Neue', sans-serif;
        -webkit-font-smoothing: antialiased;
        -moz-osx-font-smoothing: grayscale;
        letter-spacing: -0.01em;
    }

    /* ============================================
       BACKGROUND - Deep Gradient
       ============================================ */
    
    .stApp {
        background: linear-gradient(135deg, 
            #667eea 0%, 
            #764ba2 50%, 
            #f093fb 100%);
        background-attachment: fixed;
        color: white;
    }

    /* ============================================
       SIDEBAR - Premium Glass Effect
       ============================================ */
    
    section[data-testid="stSidebar"] {
        background: linear-gradient(
            180deg,
            rgba(255, 255, 255, 0.15) 0%,
            rgba(255, 255, 255, 0.08) 100%
        );
        backdrop-filter: saturate(180%) blur(40px);
        -webkit-backdrop-filter: saturate(180%) blur(40px);
        border-right: 0.5px solid rgba(255, 255, 255, 0.25);
        box-shadow: 4px 0 24px rgba(0, 0, 0, 0.08);
        width: 380px !important;
        min-width: 380px !important;
    }
    
    section[data-testid="stSidebar"] .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
    }
    
    /* Sidebar Typography - Perfect Contrast */
    section[data-testid="stSidebar"] h1 {
        color: #ffffff !important;
        font-weight: 700 !important;
        font-size: 28px !important;
        letter-spacing: -0.02em !important;
        text-shadow: 0 2px 12px rgba(0, 0, 0, 0.15);
        margin-bottom: 0 !important;
    }
    
    section[data-testid="stSidebar"] .stCaption {
        color: rgba(255, 255, 255, 0.75) !important;
        font-weight: 500 !important;
        font-size: 13px !important;
        letter-spacing: 0.02em !important;
        text-transform: uppercase;
        margin-top: 4px !important;
    }
    
    section[data-testid="stSidebar"] h2, 
    section[data-testid="stSidebar"] h3 {
        color: #ffffff !important;
        font-weight: 600 !important;
        margin-top: 1.5rem !important;
    }
    
    section[data-testid="stSidebar"] label,
    section[data-testid="stSidebar"] span,
    section[data-testid="stSidebar"] p {
        color: rgba(255, 255, 255, 0.95) !important;
        font-weight: 400 !important;
    }

    /* ============================================
       INPUT FIELDS - Glass Morphism
       ============================================ */
    
    .stTextInput>div>div>input {
        background: rgba(255, 255, 255, 0.85) !important;
        border: 1px solid rgba(255, 255, 255, 0.3);
        border-radius: 12px;
        backdrop-filter: blur(10px);
        -webkit-backdrop-filter: blur(10px);
        color: #1d1d1f !important;
        font-weight: 500;
        padding: 12px 16px;
        box-shadow: 
            0 1px 3px rgba(0, 0, 0, 0.06),
            inset 0 1px 2px rgba(255, 255, 255, 0.4);
        transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1);
    }
    
    .stTextInput>div>div>input:focus {
        border-color: rgba(255, 255, 255, 0.6);
        box-shadow: 
            0 0 0 4px rgba(255, 255, 255, 0.1),
            0 4px 12px rgba(0, 0, 0, 0.1),
            inset 0 1px 2px rgba(255, 255, 255, 0.4);
        outline: none;
    }
    
    .stTextInput>div>div>input::placeholder {
        color: rgba(29, 29, 31, 0.5);
        font-weight: 400;
    }

    /* ============================================
       SELECTBOX - Refined Dropdown
       ============================================ */
    
    .stSelectbox div[data-baseweb="select"] > div {
        background: rgba(255, 255, 255, 0.85) !important;
        border: 1px solid rgba(255, 255, 255, 0.3) !important;
        border-radius: 12px !important;
        backdrop-filter: blur(10px) !important;
        -webkit-backdrop-filter: blur(10px) !important;
        color: #1d1d1f !important;
        font-weight: 500 !important;
        padding: 8px 12px !important;
        box-shadow: 
            0 1px 3px rgba(0, 0, 0, 0.06),
            inset 0 1px 2px rgba(255, 255, 255, 0.4) !important;
        transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1);
    }
    
    .stSelectbox div[data-baseweb="select"] > div:hover {
        border-color: rgba(255, 255, 255, 0.5) !important;
    }
    
    .stSelectbox div[data-baseweb="select"] span {
        color: #1d1d1f !important;
        font-weight: 500 !important;
    }
    
    /* Dropdown Menu */
    ul[data-baseweb="menu"] {
        background: rgba(255, 255, 255, 0.95) !important;
        backdrop-filter: blur(40px) !important;
        -webkit-backdrop-filter: blur(40px) !important;
        border: 1px solid rgba(255, 255, 255, 0.3) !important;
        border-radius: 12px !important;
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.12) !important;
        padding: 8px !important;
    }
    
    ul[data-baseweb="menu"] li {
        color: #1d1d1f !important;
        background: transparent !important;
        border-radius: 8px !important;
        font-weight: 500 !important;
        padding: 10px 12px !important;
        margin: 2px 0 !important;
        transition: all 0.15s ease;
    }
    
    ul[data-baseweb="menu"] li:hover {
        background: rgba(102, 126, 234, 0.12) !important;
    }

    /* ============================================
       BUTTONS - Apple Style
       ============================================ */
    
    .stButton>button, .stDownloadButton>button {
        background: rgba(255, 255, 255, 0.9);
        color: #1d1d1f !important;
        border: 0.5px solid rgba(255, 255, 255, 0.4);
        border-radius: 12px;
        height: 48px;
        font-weight: 600;
        font-size: 15px;
        letter-spacing: -0.01em;
        backdrop-filter: blur(20px);
        -webkit-backdrop-filter: blur(20px);
        box-shadow: 
            0 2px 8px rgba(0, 0, 0, 0.08),
            inset 0 1px 0 rgba(255, 255, 255, 0.6);
        transition: all 0.25s cubic-bezier(0.4, 0, 0.2, 1);
        padding: 0 24px;
    }
    
    .stButton>button:hover, .stDownloadButton>button:hover {
        background: rgba(255, 255, 255, 1);
        transform: translateY(-1px);
        box-shadow: 
            0 4px 16px rgba(0, 0, 0, 0.12),
            inset 0 1px 0 rgba(255, 255, 255, 0.8);
        border-color: rgba(255, 255, 255, 0.6);
    }
    
    .stButton>button:active, .stDownloadButton>button:active {
        transform: translateY(0);
        box-shadow: 
            0 1px 4px rgba(0, 0, 0, 0.08),
            inset 0 1px 0 rgba(255, 255, 255, 0.6);
    }

    /* ============================================
       EXPANDER - Accordion Style
       ============================================ */
    
    .streamlit-expanderHeader, details > summary {
        background: rgba(255, 255, 255, 0.85) !important;
        border: 1px solid rgba(255, 255, 255, 0.3) !important;
        border-radius: 12px !important;
        color: #1d1d1f !important;
        font-weight: 600 !important;
        padding: 14px 16px !important;
        box-shadow: 
            0 1px 3px rgba(0, 0, 0, 0.06),
            inset 0 1px 2px rgba(255, 255, 255, 0.4);
        transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1);
    }
    
    .streamlit-expanderHeader:hover, details > summary:hover {
        background: rgba(255, 255, 255, 0.92) !important;
        border-color: rgba(255, 255, 255, 0.5) !important;
    }
    
    .streamlit-expanderHeader p, details > summary p {
        color: #1d1d1f !important;
        font-weight: 600 !important;
        margin: 0 !important;
    }
    
    .streamlit-expanderContent {
        background: rgba(255, 255, 255, 0.75) !important;
        border: 1px solid rgba(255, 255, 255, 0.2) !important;
        border-top: none !important;
        border-radius: 0 0 12px 12px !important;
        padding: 16px !important;
        margin-top: -1px !important;
        backdrop-filter: blur(10px);
        box-shadow: inset 0 1px 2px rgba(0, 0, 0, 0.05);
    }
    
    .streamlit-expanderContent label,
    .streamlit-expanderContent span,
    .streamlit-expanderContent p {
        color: #1d1d1f !important;
    }

    /* ============================================
       ALERTS & INFO BOXES
       ============================================ */
    
    .stAlert {
        background: rgba(255, 255, 255, 0.9) !important;
        border: 1px solid rgba(255, 255, 255, 0.3);
        border-radius: 12px;
        backdrop-filter: blur(20px);
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
    }
    
    .stAlert > div, .stAlert p {
        color: #1d1d1f !important;
        font-weight: 500;
    }
    
    /* Info boxes */
    .stInfo {
        background: rgba(102, 126, 234, 0.15) !important;
        border-left: 4px solid rgba(102, 126, 234, 0.6) !important;
    }
    
    /* Success boxes */
    .stSuccess {
        background: rgba(52, 199, 89, 0.15) !important;
        border-left: 4px solid rgba(52, 199, 89, 0.6) !important;
    }
    
    /* Error boxes */
    .stError {
        background: rgba(255, 59, 48, 0.15) !important;
        border-left: 4px solid rgba(255, 59, 48, 0.6) !important;
    }
    
    /* Warning boxes */
    .stWarning {
        background: rgba(255, 149, 0, 0.15) !important;
        border-left: 4px solid rgba(255, 149, 0, 0.6) !important;
    }

    /* ============================================
       JSON OUTPUT - Code Display
       ============================================ */
    
    .stJson {
        background: rgba(255, 255, 255, 0.9) !important;
        border: 1px solid rgba(255, 255, 255, 0.3);
        border-radius: 12px;
        padding: 20px;
        backdrop-filter: blur(20px);
        box-shadow: 
            0 2px 8px rgba(0, 0, 0, 0.06),
            inset 0 1px 2px rgba(255, 255, 255, 0.4);
        font-family: 'SF Mono', Monaco, 'Cascadia Code', 'Courier New', monospace !important;
        color: #1d1d1f !important;
    }

    /* ============================================
       FILE UPLOADER - Drag & Drop Zone
       ============================================ */
    
    section[data-testid="stFileUploader"] {
        background: rgba(255, 255, 255, 0.85);
        border: 2px dashed rgba(255, 255, 255, 0.4);
        border-radius: 16px;
        padding: 32px 24px;
        backdrop-filter: blur(20px);
        -webkit-backdrop-filter: blur(20px);
        box-shadow: 
            0 2px 8px rgba(0, 0, 0, 0.06),
            inset 0 1px 2px rgba(255, 255, 255, 0.4);
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
    }
    
    section[data-testid="stFileUploader"]:hover {
        border-color: rgba(255, 255, 255, 0.6);
        background: rgba(255, 255, 255, 0.9);
    }
    
    section[data-testid="stFileUploader"] div,
    section[data-testid="stFileUploader"] small,
    section[data-testid="stFileUploader"] span {
        color: #1d1d1f !important;
        font-weight: 500 !important;
    }
    
    section[data-testid="stFileUploader"] button {
        background: linear-gradient(180deg, 
            rgba(102, 126, 234, 1) 0%, 
            rgba(118, 75, 162, 1) 100%) !important;
        color: white !important;
        border: none !important;
        border-radius: 10px;
        font-weight: 600;
        padding: 10px 20px;
        box-shadow: 0 4px 12px rgba(102, 126, 234, 0.3);
        transition: all 0.2s ease;
    }
    
    section[data-testid="stFileUploader"] button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 16px rgba(102, 126, 234, 0.4);
    }

    /* ============================================
       HEADERS - Typography Hierarchy
       ============================================ */
    
    h1 {
        color: #ffffff !important;
        font-weight: 700 !important;
        font-size: 42px !important;
        letter-spacing: -0.03em !important;
        text-shadow: 0 2px 16px rgba(0, 0, 0, 0.2);
        margin-bottom: 8px !important;
    }
    
    h2 {
        color: #ffffff !important;
        font-weight: 600 !important;
        font-size: 28px !important;
        letter-spacing: -0.02em !important;
        text-shadow: 0 2px 12px rgba(0, 0, 0, 0.15);
    }
    
    h3 {
        color: rgba(255, 255, 255, 0.95) !important;
        font-weight: 600 !important;
        font-size: 20px !important;
        letter-spacing: -0.01em !important;
        text-shadow: 0 1px 8px rgba(0, 0, 0, 0.1);
    }

    /* ============================================
       DIVIDERS & SPACING
       ============================================ */
    
    hr {
        border: none;
        height: 1px;
        background: linear-gradient(
            90deg,
            transparent 0%,
            rgba(255, 255, 255, 0.3) 50%,
            transparent 100%
        );
        margin: 24px 0;
    }
    
    /* Main content spacing */
    .block-container {
        padding-top: 3rem !important;
        padding-bottom: 3rem !important;
    }

    /* ============================================
       IMAGE CONTAINERS - Gallery Style
       ============================================ */
    
    [data-testid="stImage"] {
        border-radius: 16px;
        overflow: hidden;
        box-shadow: 
            0 8px 32px rgba(0, 0, 0, 0.15),
            0 0 0 1px rgba(255, 255, 255, 0.1);
    }
    
    [data-testid="stImage"] img {
        border-radius: 16px;
    }

    /* ============================================
       SPINNER - Loading Animation
       ============================================ */
    
    .stSpinner > div {
        border-color: rgba(255, 255, 255, 0.3) !important;
        border-top-color: white !important;
    }

    /* ============================================
       SCROLLBAR - Minimal Design
       ============================================ */
    
    ::-webkit-scrollbar {
        width: 10px;
        height: 10px;
    }
    
    ::-webkit-scrollbar-track {
        background: rgba(255, 255, 255, 0.05);
        border-radius: 10px;
    }
    
    ::-webkit-scrollbar-thumb {
        background: rgba(255, 255, 255, 0.2);
        border-radius: 10px;
        transition: background 0.2s;
    }
    
    ::-webkit-scrollbar-thumb:hover {
        background: rgba(255, 255, 255, 0.3);
    }

</style>
""", unsafe_allow_html=True)

# Initialize Session State with Improved Defaults
if 'fields' not in st.session_state:
    st.session_state.fields = [
        FieldDefinition(
            name="is_ai_generated", 
            data_type=FieldType.BOOLEAN, 
            description="Analyze language style, punctuation, formatting to determine if AI-generated.", 
            length=FieldLength.SHORT
        ),
        FieldDefinition(
            name="review_cycle", 
            data_type=FieldType.STRING, 
            description="Review cycle. STRICTLY normalize to: 'Yearly', 'Quarterly', 'Monthly'. Do NOT output 'annually' or 'every month'.", 
            length=FieldLength.SHORT
        ),
        FieldDefinition(
            name="prepared_by", 
            data_type=FieldType.STRING, 
            description="Author/Owner/Department. If multiple, list the most relevant ones (up to 15 words).", 
            length=FieldLength.MEDIUM
        ),
        FieldDefinition(
            name="company_name", 
            data_type=FieldType.STRING, 
            description="Company name this document is about.", 
            length=FieldLength.SHORT
        ),
        FieldDefinition(
            name="document_date", 
            data_type=FieldType.STRING, 
            description="Creation date. Look for 'Date:', 'Issued:', or the main document date. Format strictly 'ddmmyyyy'.", 
            length=FieldLength.SHORT
        ),
    ]

if 'extraction_result' not in st.session_state:
    st.session_state.extraction_result = None

def add_field():
    if st.session_state.new_field_name and st.session_state.new_field_desc:
        new_field = FieldDefinition(
            name=st.session_state.new_field_name,
            description=st.session_state.new_field_desc,
            data_type=st.session_state.new_field_type,
            length=st.session_state.new_field_length
        )
        st.session_state.fields.append(new_field)
        # Clear inputs
        st.session_state.new_field_name = ""
        st.session_state.new_field_desc = ""

# Sidebar
with st.sidebar:
    st.title("Spektr Document OCR")
    st.caption("v5.0 • Premium Edition")
    
    with st.expander("➕ Add New Field", expanded=False):
        st.text_input("Field Name", key="new_field_name", placeholder="e.g., summary")
        st.text_input("Description", key="new_field_desc", placeholder="e.g., Brief summary of the content")
        
        col_type, col_len = st.columns(2)
        with col_type:
            st.selectbox("Type", [t.value for t in FieldType], key="new_field_type")
        with col_len:
            st.selectbox("Length", [l.value for l in FieldLength], key="new_field_length")
            
        st.button("Add Field", on_click=add_field)

    st.divider()
    st.subheader("Active Fields")
    
    if not st.session_state.fields:
        st.caption("No fields configured.")
    else:
        # Iterate with index to allow editing
        for i, field in enumerate(st.session_state.fields):
            # Use Expander for editing
            with st.expander(f"{field.name} ({field.data_type.value})", expanded=False):
                # We use key=f"field_{i}_name" etc. to bind inputs.
                # However, Streamlit widgets update state on change.
                # We need to manually update the object in the list.
                
                new_name = st.text_input("Name", value=field.name, key=f"edit_name_{i}")
                new_desc = st.text_input("Description", value=field.description, key=f"edit_desc_{i}")
                
                col_e1, col_e2 = st.columns(2)
                with col_e1:
                    # Find index of current value in Enum
                    type_opts = [t.value for t in FieldType]
                    curr_type_idx = type_opts.index(field.data_type.value)
                    new_type_str = st.selectbox("Type", type_opts, index=curr_type_idx, key=f"edit_type_{i}")
                    
                with col_e2:
                    len_opts = [l.value for l in FieldLength]
                    curr_len_idx = len_opts.index(field.length.value)
                    new_len_str = st.selectbox("Length", len_opts, index=curr_len_idx, key=f"edit_len_{i}")

                # Update the field object in session state if changed
                # Note: This runs on every rerun.
                updated_field = FieldDefinition(
                    name=new_name,
                    description=new_desc,
                    data_type=FieldType(new_type_str),
                    length=FieldLength(new_len_str)
                )
                st.session_state.fields[i] = updated_field

                if st.button("Remove Field", key=f"del_{i}"):
                    st.session_state.fields.pop(i)
                    st.rerun()

# Main Area
st.title("Spektr Document OCR")
st.markdown("### Upload & Extract")

uploaded_file = st.file_uploader("Drop your document here", type=['png', 'jpg', 'jpeg', 'pdf'])

if uploaded_file:
    col1, col2 = st.columns(2)
    
    # Display Document
    with col2:
        st.markdown("#### Preview")
        image_to_process = None
        
        if uploaded_file.type == "application/pdf":
            try:
                pdf = pdfium.PdfDocument(uploaded_file.read())
                page = pdf[0]
                bitmap = page.render(scale=2)  # Render at 2x scale for better quality
                image_to_process = bitmap.to_pil()
                
                st.image(image_to_process, caption="Page 1 Preview", use_container_width=True)
                # Reset pointer for processing
                uploaded_file.seek(0)
            except Exception as e:
                st.error(f"Error converting PDF: {e}")
        else:
            image_to_process = Image.open(uploaded_file)
            st.image(image_to_process, caption="Uploaded Image", use_container_width=True)
            uploaded_file.seek(0)

    # Extraction Action
    with col1:
        st.markdown("#### Results")
        
        if st.button("✨ Run Extraction", type="primary"):
            if not st.session_state.fields:
                st.error("Please add at least one field.")
            elif not image_to_process:
                st.error("No valid image to process.")
            else:
                with st.spinner("Analyzing document..."):
                    try:
                        processor = DocumentProcessor()
                        
                        # Convert image to bytes
                        img_byte_arr = io.BytesIO()
                        image_to_process.save(img_byte_arr, format='PNG')
                        img_byte_arr = img_byte_arr.getvalue()
                        
                        result = processor.extract_data(
                            file_bytes=img_byte_arr,
                            file_type='png',
                            fields=st.session_state.fields
                        )
                        
                        st.session_state.extraction_result = result
                        st.success("Extraction Complete!")
                        
                    except Exception as e:
                        st.error(f"An error occurred: {str(e)}")

        if st.session_state.extraction_result:
            st.json(st.session_state.extraction_result)
            
            # Download button
            json_str = pd.Series(st.session_state.extraction_result).to_json(indent=2)
            st.download_button(
                label="Download JSON",
                data=json_str,
                file_name="extracted_data.json",
                mime="application/json"
            )

else:
    st.info("👆 Upload a document to get started.")
