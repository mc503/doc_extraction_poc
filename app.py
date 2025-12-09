import streamlit as st
from PIL import Image
import io
import json
from pathlib import Path
import pypdfium2 as pdfium

from backend import DocumentProcessor, FieldDefinition, FieldType, FieldLength
from templates import get_default_templates, OWNERSHIP_STRUCTURE_INSTRUCTIONS, OWNERSHIP_STRUCTURE_INSTRUCTIONS_WITH_NON_EQUITY

# Page Config
st.set_page_config(
    page_title="Spektr",
    page_icon="🔮",
    layout="wide",
    initial_sidebar_state="expanded"
)


def load_css():
    """Load CSS from external stylesheet."""
    css_path = Path(__file__).parent / ".streamlit" / "style.css"
    if css_path.exists():
        st.markdown(f"<style>{css_path.read_text()}</style>", unsafe_allow_html=True)


# Apply CSS
load_css()

# Handle URL-based session reset (add ?reset=1 to URL to clear session state)
query_params = st.query_params
if query_params.get("reset") == "1":
    for key in list(st.session_state.keys()):
        del st.session_state[key]
    st.query_params.clear()
    st.rerun()


# Initialize Session State with Templates
if 'templates' not in st.session_state:
    st.session_state.templates = get_default_templates()

# Migration check: Ensure Ownership template uses new ownership_structure field
# (handles stale session state from previous app versions)
if 'Ownership' in st.session_state.templates:
    ownership_template = st.session_state.templates['Ownership']
    ownership_field_names = [f.name for f in ownership_template]
    if 'ownership_graph' in ownership_field_names or 'ownership_structure' not in ownership_field_names:
        # Migrate to new schema by refreshing templates
        fresh_templates = get_default_templates()
        st.session_state.templates['Ownership'] = fresh_templates['Ownership']

if 'selected_template' not in st.session_state:
    st.session_state.selected_template = "AML"

if 'fields' not in st.session_state:
    # Deep copy to avoid reference issues
    st.session_state.fields = list(st.session_state.templates["AML"])

# Track original state for change detection
if 'original_template_fields' not in st.session_state:
    st.session_state.original_template_fields = list(st.session_state.templates["AML"])

if 'extraction_result' not in st.session_state:
    st.session_state.extraction_result = None

# If currently viewing Ownership template with stale fields, refresh them
if st.session_state.selected_template == "Ownership":
    current_field_names = [f.name for f in st.session_state.fields]
    if 'ownership_graph' in current_field_names or 'ownership_structure' not in current_field_names:
        st.session_state.fields = list(st.session_state.templates["Ownership"])
        st.session_state.original_template_fields = list(st.session_state.templates["Ownership"])


def load_template():
    """Load fields from the selected template."""
    template_name = st.session_state.template_selector
    st.session_state.selected_template = template_name
    st.session_state.fields = list(st.session_state.templates[template_name])
    st.session_state.original_template_fields = list(st.session_state.templates[template_name])



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
    st.caption("v4.3 • Liquid Intelligence")
    
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
    
    # Template Actions Placeholder
    actions_placeholder = st.empty()

    with st.expander("Save as New Template", expanded=False):
        new_template_name = st.text_input("New Name", placeholder="e.g., Invoices")
        if st.button("Create Template"):
            if new_template_name and new_template_name not in st.session_state.templates:
                st.session_state.templates[new_template_name] = list(st.session_state.fields)
                st.session_state.selected_template = new_template_name
                st.session_state.original_template_fields = list(st.session_state.fields)
                st.success(f"Created '{new_template_name}'!")
                st.rerun()
            elif new_template_name in st.session_state.templates:
                st.error("Name exists.")
            else:
                st.error("Enter a name.")

    st.divider()
    
    with st.expander("➕ Add New Field", expanded=False):
        st.text_input("Field Name", key="new_field_name", placeholder="e.g., summary")
        st.text_area("Description", key="new_field_desc", placeholder="e.g., Brief summary of the content", height=100)
        
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
                is_ownership_field = field.data_type == FieldType.OWNERSHIP_STRUCTURE
                
                new_name = st.text_input("Name", value=field.name, key=f"edit_name_{i}")
                
                # For ownership structure fields, show read-only description
                if is_ownership_field:
                    st.caption("AI Instructions (built-in):")
                    st.code(field.description[:200] + "..." if len(field.description) > 200 else field.description, language=None)
                    new_desc = field.description  # Keep existing
                else:
                    new_desc = st.text_area("Description", value=field.description, key=f"edit_desc_{i}", height=100)
                
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

                # Show different options based on field type
                if is_ownership_field:
                    new_non_equity = st.checkbox(
                        "Include Non-Equity Roles", 
                        value=field.include_non_equity_roles, 
                        key=f"edit_non_equity_{i}",
                        help="Extract directors, auditors, secretaries in addition to ownership relationships"
                    )
                    new_reasoning = False  # Not applicable
                    # Update description based on checkbox
                    if new_non_equity:
                        new_desc = OWNERSHIP_STRUCTURE_INSTRUCTIONS_WITH_NON_EQUITY
                    else:
                        new_desc = OWNERSHIP_STRUCTURE_INSTRUCTIONS
                else:
                    new_non_equity = False  # Not applicable
                    new_reasoning = st.checkbox("Include Reasoning", value=field.include_reasoning, key=f"edit_reason_{i}")

                # Update the field object in session state if changed
                updated_field = FieldDefinition(
                    name=new_name,
                    description=new_desc,
                    data_type=FieldType(new_type_str),
                    length=FieldLength(new_len_str),
                    include_reasoning=new_reasoning,
                    include_non_equity_roles=new_non_equity
                )
                st.session_state.fields[i] = updated_field

                if st.button("Remove Field", key=f"del_{i}"):
                    st.session_state.fields.pop(i)
                    st.rerun()

    # Render Template Actions (after fields update)
    with actions_placeholder.container():
        col_t1, col_t2 = st.columns(2)
        
        # Check for changes
        has_changes = st.session_state.fields != st.session_state.original_template_fields
        
        with col_t1:
            if has_changes:
                if st.button("💾 Save Changes", use_container_width=True):
                    st.session_state.templates[st.session_state.selected_template] = list(st.session_state.fields)
                    st.session_state.original_template_fields = list(st.session_state.fields)
                    st.success("Saved!")
                    st.rerun()
            else:
                st.button("💾 Saved", disabled=True, use_container_width=True)
                
        with col_t2:
            if st.button("🗑️ Delete", use_container_width=True):
                if len(st.session_state.templates) > 1:
                    del st.session_state.templates[st.session_state.selected_template]
                    # Reset to first available
                    st.session_state.selected_template = list(st.session_state.templates.keys())[0]
                    st.session_state.fields = list(st.session_state.templates[st.session_state.selected_template])
                    st.session_state.original_template_fields = list(st.session_state.fields)
                    st.rerun()
                else:
                    st.error("Cannot delete the last template.")

# Main Area
st.title("Spektr")
st.markdown("### Upload & Extract")

uploaded_file = st.file_uploader("Drop your document here", type=['png', 'jpg', 'jpeg', 'pdf'], key="main_file_uploader")

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
                            file_type='png',  # We convert everything to PNG bytes
                            fields=st.session_state.fields
                        )
                        
                        st.session_state.extraction_result = result
                        st.success("Extraction Complete!")
                        
                    except Exception as e:
                        st.error(f"An error occurred: {str(e)}")

        if st.session_state.extraction_result:
            st.json(st.session_state.extraction_result)
            
            # Download button - using stdlib json instead of pandas
            json_str = json.dumps(st.session_state.extraction_result, indent=2)
            st.download_button(
                label="Download JSON",
                data=json_str,
                file_name="extracted_data.json",
                mime="application/json"
            )

else:
    st.info("👆 Upload a document to get started.")
