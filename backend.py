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
    OWNERSHIP_GRAPH = "Ownership Graph"

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
    include_reasoning: bool = False

# --- Ownership Models ---
class OwnershipShareholding(BaseModel):
    role: str
    percentage: str

class OwnershipAdjacency(BaseModel):
    spektrId: str
    directOrIndirect: str
    shareholding: OwnershipShareholding
    entityPositions: List[str]
    entityRoles: List[str]

class OwnershipDetails(BaseModel):
    name: str
    customer_type: str # company/individual
    ownership: float
    isBeneficiary: bool
    company_name: Optional[str] = None
    full_name: Optional[str] = None

class OwnershipNode(BaseModel):
    spektrId: str
    status: str = "pending"
    details: OwnershipDetails
    adj: List[OwnershipAdjacency]

class DynamicSchemaGenerator:
    @staticmethod
    def generate_model(fields: List[FieldDefinition]) -> Type[BaseModel]:
        """
        Dynamically creates a Pydantic model based on user-defined fields.
        """
        field_definitions = {}
        
        for field in fields:
            if field.data_type == FieldType.STRING:
                base_type = str
            elif field.data_type == FieldType.INTEGER:
                base_type = int
            elif field.data_type == FieldType.LIST_STRINGS:
                base_type = List[str]
            elif field.data_type == FieldType.BOOLEAN:
                base_type = bool
            elif field.data_type == FieldType.OWNERSHIP_GRAPH:
                base_type = List[OwnershipNode]
            else:
                base_type = str # Default
            
            # Append length instruction if not Auto
            description = field.description
            if field.length != FieldLength.AUTO:
                description += f" [Output Length: {field.length.value}]"

            if field.include_reasoning and field.data_type != FieldType.OWNERSHIP_GRAPH:
                # Create a nested model for this field
                nested_model_name = f"{field.name.capitalize()}WithReasoning"
                nested_fields = {
                    "value": (base_type, Field(description="The extracted value.")),
                    "reason": (str, Field(description="A 1-2 sentence explanation of why this value was extracted."))
                }
                field_type = create_model(nested_model_name, **nested_fields)
                field_definitions[field.name] = (
                    field_type,
                    Field(description=description)
                )
            else:
                # Standard field (or complex graph which handles its own structure)
                field_definitions[field.name] = (
                    base_type, 
                    Field(description=description)
                )
            
        return create_model('ExtractedData', **field_definitions)

class DocumentProcessor:
    def __init__(self, api_key: Optional[str] = None):
        self.client = OpenAI(api_key=api_key or get_api_key())

    def _encode_image(self, image_bytes: bytes) -> str:
        return base64.b64encode(image_bytes).decode('utf-8')

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
    def extract_data(self, file_bytes_list: List[bytes], file_type: str, fields: List[FieldDefinition]) -> Dict[str, Any]:
        """
        Extracts data from the document using OpenAI GPT-4o with a dynamic schema.
        Accepts a list of file bytes (one per page/image).
        """
        # Note: We allow empty 'fields' list because we have default fields now.
        # if not fields:
        #    return {"error": "No fields defined for extraction."}

        # 1. Generate the dynamic Pydantic model
        DynamicModel = DynamicSchemaGenerator.generate_model(fields)

        # 2. Prepare the images for the API
        content_list = [
            {
                "type": "text", 
                "text": "Extract the following information from this document."
            }
        ]

        # Determine media type
        media_type = "image/jpeg"
        if file_type == "png":
            media_type = "image/png"
        
        # Add each image to the content list
        for file_bytes in file_bytes_list:
            base64_image = self._encode_image(file_bytes)
            content_list.append({
                "type": "image_url",
                "image_url": {
                    "url": f"data:{media_type};base64,{base64_image}"
                }
            })

        # 3. Call OpenAI API
        response = self.client.beta.chat.completions.parse(
            model="gpt-4o",
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are an expert document extraction AI. "
                        "Analyze the provided image(s) and extract the requested fields. "
                        "If the image is rotated or blurry, try to detect and correct orientation mentally before extracting. "
                        "Return the data strictly in the requested JSON format."
                        "Do not make up data that is not in the document."
                        "For any fields asking to assess authorship, authenticity, or AI generation: "
                        "Look for specific artifacts: hallucinated details, perfect but empty grammar, lack of specific real-world context, "
                        "inconsistent formatting typical of LLM outputs, or generic 'lorem ipsum' style content. "
                        "CRITICAL: Do NOT cite 'professional formatting', 'legal language', 'detailed structure', or 'compliance terminology' "
                        "as evidence of human authorship. AI models (like GPT-4) generate highly professional, structured, and legalistic text. "
                        "To conclude a document is human-written, look for: specific nuances, inconsistencies, human errors, or deep context "
                        "that an AI is unlikely to know. If the document is simply 'professional', acknowledge that it could be AI-generated."
                        "Provide specific evidence in your reasoning."
                    )
                },
                {
                    "role": "user",
                    "content": content_list
                }
            ],
            response_format=DynamicModel,
        )

        # 4. Parse and return result
        return response.choices[0].message.parsed.model_dump()
