import streamlit as st
import pandas as pd
from PIL import Image
import io
import pypdfium2 as pdfium

from backend import DocumentProcessor, FieldDefinition, FieldType, FieldLength

# Page Config
st.set_page_config(
    page_title="Spektr",
    page_icon="🔮",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Spektr "Liquid Glass" CSS
st.markdown("""
<style>
    /* Global Font */
    html, body, [class*="css"] {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    }

    /* Background Gradient - Vibrant & Deep */
    .stApp {
        background: radial-gradient(circle at 10% 20%, rgb(69, 86, 255) 0%, rgb(100, 22, 195) 90%);
        color: white;
    }
    
    /* Header Bar - Translucent Purple */
    header[data-testid="stHeader"] {
        background: linear-gradient(90deg, rgba(100, 22, 195, 0.3) 0%, rgba(69, 86, 255, 0.3) 100%) !important;
        backdrop-filter: blur(20px) !important;
        -webkit-backdrop-filter: blur(20px) !important;
        border-bottom: 1px solid rgba(255, 255, 255, 0.1) !important;
    }

    /* Sidebar Liquid Glass */
    section[data-testid="stSidebar"] {
        background-color: rgba(255, 255, 255, 0.1);
        backdrop-filter: blur(30px);
        -webkit-backdrop-filter: blur(30px);
        border-right: 1px solid rgba(255, 255, 255, 0.1);
        width: 350px !important;
        min-width: 350px !important;
    }
    
    /* Sidebar Content Color */
    section[data-testid="stSidebar"] h1, section[data-testid="stSidebar"] h2, section[data-testid="stSidebar"] h3, section[data-testid="stSidebar"] span, section[data-testid="stSidebar"] div, section[data-testid="stSidebar"] label {
        color: white !important;
    }

    /* Input Fields - Translucent & Black Text */
    .stTextInput>div>div>input {
        background-color: rgba(255, 255, 255, 0.9); /* Increased opacity for readability */
        border: 1px solid rgba(255, 255, 255, 0.5);
        border-radius: 12px;
        backdrop-filter: blur(20px);
        color: #000000 !important;
        font-weight: 500;
    }
    .stTextInput>div>div>input::placeholder {
        color: rgba(0, 0, 0, 0.5);
    }
    
    /* Sidebar Text Inputs */
    section[data-testid="stSidebar"] .stTextInput>div>div>input {
        background-color: rgba(255, 255, 255, 0.8) !important; /* High opacity for readability */
        border: 1px solid rgba(255, 255, 255, 0.5) !important;
        border-radius: 12px !important;
        backdrop-filter: blur(20px) !important;
        color: #000000 !important; /* Black text */
        font-weight: 500 !important;
    }
    section[data-testid="stSidebar"] .stTextInput>div>div>input::placeholder {
        color: rgba(0, 0, 0, 0.6) !important;
    }

    /* Selectbox */
    .stSelectbox div[data-baseweb="select"] > div {
        background-color: rgba(255, 255, 255, 0.2) !important;
        border: 1px solid rgba(255, 255, 255, 0.3) !important;
        border-radius: 12px !important;
        backdrop-filter: blur(20px) !important;
        color: white !important;
    }
    .stSelectbox div[data-baseweb="select"] span {
        color: white !important;
    }
    /* Dropdown options */
    ul[data-baseweb="menu"] li {
        color: #000000 !important;
        background-color: rgba(255, 255, 255, 0.95) !important;
    }
    
    /* Buttons - Liquid & Readable */
    .stButton>button, .stDownloadButton>button {
        background: rgba(255, 255, 255, 0.2);
        color: white !important;
        border: 1px solid rgba(255, 255, 255, 0.4);
        border-radius: 12px;
        height: 45px;
        font-weight: 600;
        backdrop-filter: blur(10px);
        transition: all 0.3s cubic-bezier(0.25, 0.8, 0.25, 1);
        box-shadow: 0 4px 15px rgba(0,0,0,0.1);
    }
    .stButton>button:hover, .stDownloadButton>button:hover {
        background: rgba(255, 255, 255, 0.4);
        transform: translateY(-2px);
        box-shadow: 0 8px 25px rgba(0,0,0,0.2);
        border-color: rgba(255, 255, 255, 0.6);
        color: white !important;
    }
    /* Primary Button */
    .stButton>button[kind="primary"] {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        border: none;
        box-shadow: 0 4px 15px rgba(118, 75, 162, 0.4);
    }

    /* Expander */
    .streamlit-expanderHeader, details > summary {
        background-color: rgba(255, 255, 255, 0.1) !important;
        border-radius: 12px;
        color: white !important;
        border: 1px solid rgba(255, 255, 255, 0.1);
    }
    .streamlit-expanderHeader p, details > summary p {
        color: white !important;
        font-weight: 600;
    }
    .streamlit-expanderHeader:hover, details > summary:hover {
        background-color: rgba(255, 255, 255, 0.15) !important;
        color: white !important;
    }
    .streamlit-expanderContent {
        background-color: rgba(0, 0, 0, 0.1) !important;
        border-radius: 0 0 12px 12px;
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-top: none;
        color: white !important;
    }
    
    /* Alerts & Info */
    .stAlert {
        background-color: rgba(255, 255, 255, 0.9);
        color: #000000 !important;
        border-radius: 12px;
    }
    .stAlert > div {
        color: #000000 !important;
    }
    .stAlert p {
        color: #000000 !important;
    }
    
    /* JSON Output */
    .stJson {
        background-color: rgba(0, 0, 0, 0.2);
        border-radius: 16px;
        padding: 20px;
        backdrop-filter: blur(20px);
        color: white !important;
    }
    
    /* File Uploader */
    section[data-testid="stFileUploader"] {
        background-color: rgba(255, 255, 255, 0.1);
        border-radius: 16px;
        padding: 20px;
        backdrop-filter: blur(20px);
        border: 2px dashed rgba(255, 255, 255, 0.3);
    }
    section[data-testid="stFileUploader"] div {
        color: white !important;
    }
    section[data-testid="stFileUploader"] small {
        color: rgba(255, 255, 255, 0.8) !important;
    }

    /* Headers */
    h1, h2, h3, h4, h5, h6 {
        color: white !important;
        text-shadow: 0 2px 10px rgba(0,0,0,0.1);
    }
    
    /* Dividers */
    hr {
        border-color: rgba(255, 255, 255, 0.2);
    }
    
    /* Checkbox */
    .stCheckbox label span {
        color: white !important;
    }
</style>
""", unsafe_allow_html=True)

# Initialize Session State with Improved Defaults
if 'templates' not in st.session_state:
    st.session_state.templates = {
        "AML": [
            FieldDefinition(
                name="is_ai_generated", 
                data_type=FieldType.BOOLEAN, 
                description="Analyze language style, punctuation, formatting to determine if AI-generated.", 
                length=FieldLength.SHORT,
                include_reasoning=True
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
    }

if 'selected_template' not in st.session_state:
    st.session_state.selected_template = "AML"

if 'fields' not in st.session_state:
    # Deep copy to avoid reference issues
    st.session_state.fields = list(st.session_state.templates["AML"])

if 'extraction_result' not in st.session_state:
    st.session_state.extraction_result = None

def load_template():
    """Load fields from the selected template."""
    template_name = st.session_state.template_selector
    st.session_state.selected_template = template_name
    st.session_state.fields = list(st.session_state.templates[template_name])

def add_field():
    if st.session_state.new_field_name and st.session_state.new_field_desc:
        new_field = FieldDefinition(
            name=st.session_state.new_field_name,
            description=st.session_state.new_field_desc,
            data_type=st.session_state.new_field_type,
            length=st.session_state.new_field_length,
            include_reasoning=st.session_state.new_field_reasoning
        )
        st.session_state.fields.append(new_field)
        # Clear inputs
        st.session_state.new_field_name = ""
        st.session_state.new_field_desc = ""
        st.session_state.new_field_reasoning = False

# Sidebar
with st.sidebar:
    st.title("Spektr")
    st.caption("v4.2 • Liquid Intelligence")
    
    # Template Selection
    st.subheader("Templates")
    
    # Ensure selected_template is valid
    template_options = list(st.session_state.templates.keys())
    if st.session_state.selected_template not in template_options:
        st.session_state.selected_template = template_options[0] if template_options else "AML"
        
    idx = template_options.index(st.session_state.selected_template)
    
    selected = st.selectbox(
        "Choose Template", 
        template_options, 
        index=idx, 
        key="template_selector", 
        on_change=load_template
    )
    
    # Template Actions
    col_t1, col_t2 = st.columns(2)
    
    with col_t1:
        if st.button("💾 Save Changes", use_container_width=True, help="Update the current template with active fields"):
            st.session_state.templates[st.session_state.selected_template] = list(st.session_state.fields)
            st.success("Saved!")
            
    with col_t2:
        if st.button("🗑️ Delete", use_container_width=True, help="Delete the current template"):
            if len(st.session_state.templates) > 1:
                del st.session_state.templates[st.session_state.selected_template]
                # Reset to first available
                st.session_state.selected_template = list(st.session_state.templates.keys())[0]
                st.session_state.fields = list(st.session_state.templates[st.session_state.selected_template])
                st.rerun()
            else:
                st.error("Cannot delete the last template.")

    with st.expander("Save as New Template", expanded=False):
        new_template_name = st.text_input("New Name", placeholder="e.g., Invoices")
        if st.button("Create Template"):
            if new_template_name and new_template_name not in st.session_state.templates:
                st.session_state.templates[new_template_name] = list(st.session_state.fields)
                st.session_state.selected_template = new_template_name
                st.success(f"Created '{new_template_name}'!")
                st.rerun()
            elif new_template_name in st.session_state.templates:
                st.error("Name exists.")
            else:
                st.error("Enter a name.")

    st.divider()
    
    with st.expander("➕ Add New Field", expanded=False):
        st.text_input("Field Name", key="new_field_name", placeholder="e.g., summary")
        st.text_input("Description", key="new_field_desc", placeholder="e.g., Brief summary of the content")
        
        col_type, col_len = st.columns(2)
        with col_type:
            st.selectbox("Type", [t.value for t in FieldType], key="new_field_type")
        with col_len:
            st.selectbox("Length", [l.value for l in FieldLength], key="new_field_length")
            
        st.checkbox("Include Reasoning", key="new_field_reasoning", help="AI will explain why it extracted this value.")
            
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

                new_reasoning = st.checkbox("Include Reasoning", value=field.include_reasoning, key=f"edit_reason_{i}")

                # Update the field object in session state if changed
                # Note: This runs on every rerun.
                updated_field = FieldDefinition(
                    name=new_name,
                    description=new_desc,
                    data_type=FieldType(new_type_str),
                    length=FieldLength(new_len_str),
                    include_reasoning=new_reasoning
                )
                st.session_state.fields[i] = updated_field

                if st.button("Remove Field", key=f"del_{i}"):
                    st.session_state.fields.pop(i)
                    st.rerun()

# Main Area
st.title("Spektr")
st.markdown("### Upload & Extract")

uploaded_file = st.file_uploader("Drop your document here", type=['png', 'jpg', 'jpeg', 'pdf'])

if uploaded_file:
    col1, col2 = st.columns(2)
    
    # Display Document
    with col2:
        st.markdown("#### Preview")
        images_to_process = []
        
        if uploaded_file.type == "application/pdf":
            try:
                pdf = pdfium.PdfDocument(uploaded_file.read())
                num_pages = len(pdf)
                st.caption(f"Processing {num_pages} page(s)")
                
                # Create a container for the carousel/list of images
                with st.container(height=600):
                    for i in range(num_pages):
                        page = pdf[i]
                        bitmap = page.render(scale=2)  # Render at 2x scale for better quality
                        pil_image = bitmap.to_pil()
                        images_to_process.append(pil_image)
                        
                        st.image(pil_image, caption=f"Page {i+1}", use_container_width=True)
                        st.divider()
                
                # Reset pointer for processing
                uploaded_file.seek(0)
            except Exception as e:
                st.error(f"Error converting PDF: {e}")
        else:
            image = Image.open(uploaded_file)
            images_to_process.append(image)
            st.image(image, caption="Uploaded Image", use_container_width=True)
            uploaded_file.seek(0)

    # Extraction Action
    with col1:
        st.markdown("#### Results")
        
        if st.button("✨ Run Extraction", type="primary"):
            if not st.session_state.fields:
                st.error("Please add at least one field.")
            elif not images_to_process:
                st.error("No valid image to process.")
            else:
                with st.spinner("Analyzing document..."):
                    try:
                        processor = DocumentProcessor()
                        
                        # Convert images to bytes
                        img_bytes_list = []
                        for img in images_to_process:
                            img_byte_arr = io.BytesIO()
                            img.save(img_byte_arr, format='PNG')
                            img_bytes_list.append(img_byte_arr.getvalue())
                        
                        result = processor.extract_data(
                            file_bytes_list=img_bytes_list,
                            file_type='png', # We convert everything to PNG bytes
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
