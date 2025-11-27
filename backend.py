import os
import base64
from typing import List, Dict, Any, Type, Optional
from enum import Enum
import json

from pydantic import BaseModel, create_model, Field
from openai import OpenAI
from tenacity import retry, stop_after_attempt, wait_exponential
from dotenv import load_dotenv

# Try to import streamlit for secrets (cloud deployment)
try:
    import streamlit as st
    HAS_STREAMLIT = True
except ImportError:
    HAS_STREAMLIT = False

load_dotenv()

def get_api_key() -> Optional[str]:
    """Get API key from Streamlit secrets (cloud) or .env file (local)."""
    # First, try Streamlit secrets (for cloud deployment)
    if HAS_STREAMLIT:
        try:
            return st.secrets.get("OPENAI_API_KEY")
        except (KeyError, FileNotFoundError):
            pass
    
    # Fall back to environment variable (from .env file)
    return os.getenv("OPENAI_API_KEY")

class FieldType(str, Enum):
    STRING = "String"
    INTEGER = "Integer"
    LIST_STRINGS = "List of Strings"
    BOOLEAN = "Boolean"

class FieldLength(str, Enum):
    AUTO = "Auto"
    SHORT = "Short (1-5 words)"
    MEDIUM = "Medium (1-2 sentences)"
    LONG = "Long (Paragraph/Summary)"

class FieldDefinition(BaseModel):
    name: str
    description: str
    data_type: FieldType
    length: FieldLength = FieldLength.AUTO

class DynamicSchemaGenerator:
    @staticmethod
    def generate_model(fields: List[FieldDefinition]) -> Type[BaseModel]:
        """
        Dynamically creates a Pydantic model based on user-defined fields.
        """
        field_definitions = {}
        
        for field in fields:
            if field.data_type == FieldType.STRING:
                field_type = str
            elif field.data_type == FieldType.INTEGER:
                field_type = int
            elif field.data_type == FieldType.LIST_STRINGS:
                field_type = List[str]
            elif field.data_type == FieldType.BOOLEAN:
                field_type = bool
            else:
                field_type = str # Default
            
            # Append length instruction if not Auto
            description = field.description
            if field.length != FieldLength.AUTO:
                description += f" [Output Length: {field.length.value}]"

            # Create the field definition tuple: (type, Field(description=...))
            field_definitions[field.name] = (
                field_type, 
                Field(description=description)
            )
            
        return create_model('ExtractedData', **field_definitions)

class DocumentProcessor:
    def __init__(self, api_key: Optional[str] = None):
        self.client = OpenAI(api_key=api_key or get_api_key())

    def _encode_image(self, image_bytes: bytes) -> str:
        return base64.b64encode(image_bytes).decode('utf-8')

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
    def extract_data(self, file_bytes: bytes, file_type: str, fields: List[FieldDefinition]) -> Dict[str, Any]:
        """
        Extracts data from the document using OpenAI GPT-4o with a dynamic schema.
        """
        # Note: We allow empty 'fields' list because we have default fields now.
        # if not fields:
        #    return {"error": "No fields defined for extraction."}

        # 1. Generate the dynamic Pydantic model
        DynamicModel = DynamicSchemaGenerator.generate_model(fields)

        # 2. Prepare the image for the API
        base64_image = self._encode_image(file_bytes)
        
        # Determine media type
        media_type = "image/jpeg"
        if file_type == "png":
            media_type = "image/png"
        elif file_type == "pdf":
             # Note: For PDF, in a real app we might convert to image first using pdf2image.
             # For this POC, we'll assume the user uploads an image or we handle PDF conversion in app.py
             # Or we can try to send it if OpenAI supports it (currently vision supports images).
             # Let's assume we receive image bytes here.
             pass

        # 3. Call OpenAI API
        response = self.client.beta.chat.completions.parse(
            model="gpt-4o",
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are an expert document extraction AI. "
                        "Analyze the provided image and extract the requested fields. "
                        "If the image is rotated or blurry, try to detect and correct orientation mentally before extracting. "
                        "Return the data strictly in the requested JSON format."
                        "Do not make up data that is not in the document."
                    )
                },
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text", 
                            "text": "Extract the following information from this document."
                        },
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:{media_type};base64,{base64_image}"
                            }
                        }
                    ]
                }
            ],
            response_format=DynamicModel,
        )

        # 4. Parse and return result
        return response.choices[0].message.parsed.model_dump()
