"""
Spektr Template Definitions

This module contains all field and template definitions for document extraction.
Single source of truth for common fields and default templates.
"""

from backend import FieldDefinition, FieldType, FieldLength


# Common fields shared across all templates
COMMON_FIELDS = [
    FieldDefinition(
        name="is_ai_generated", 
        data_type=FieldType.BOOLEAN, 
        description="Is this document AI-generated? Look for lack of specific details, generic fillers, or 'perfect' but empty language. Do NOT assume human authorship just because it looks professional.", 
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
        description="Author/Owner/Department. Extract ONLY names and titles (e.g. 'Natasja Michaela Alexander, LL.M.'). STRICTLY EXCLUDE any descriptive text such as 'a civil law notary...'. Truncate after the title.", 
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


# AML Template Fields
AML_FIELDS = COMMON_FIELDS + [
    FieldDefinition(name="roles_responsibilities", data_type=FieldType.BOOLEAN, description="Is there any chapter or other mention of policy cover roles and responsibilities?", include_reasoning=True),
    FieldDefinition(name="risk_appetite", data_type=FieldType.BOOLEAN, description="Is there a risk appetite statement / customer acceptance policy?", include_reasoning=True),
    FieldDefinition(name="cdd", data_type=FieldType.BOOLEAN, description="Is there any chapter or mentioning of a process for customer due diligence and enhanced customer due diligence as well as ongoing due diligence?", include_reasoning=True),
    FieldDefinition(name="customer_risk", data_type=FieldType.BOOLEAN, description="Is there any chapter or mentioning of a process for customer risk classification?", include_reasoning=True),
    FieldDefinition(name="monitoring_reporting", data_type=FieldType.BOOLEAN, description="Is there any chapter or mention of a process for monitoring and reporting?", include_reasoning=True),
    FieldDefinition(name="record_retention", data_type=FieldType.BOOLEAN, description="Is there any chapter or mentioning of a process for record retention and data privacy?", include_reasoning=True),
    FieldDefinition(name="employee_due_diligence", data_type=FieldType.BOOLEAN, description="Is there any chapter or mention of a process for employee due diligence?", include_reasoning=True),
    FieldDefinition(name="training", data_type=FieldType.BOOLEAN, description="Is the any chapter or mention of any training for employees", include_reasoning=True),
    FieldDefinition(name="internal_reporting", data_type=FieldType.BOOLEAN, description="Is there any chapter or mention of a process for internal / management reporting?", include_reasoning=True),
    FieldDefinition(name="internal_control", data_type=FieldType.BOOLEAN, description="Is there any chapter or mentioning of a process for internal control?", include_reasoning=True),
    FieldDefinition(name="risk_based_approach", data_type=FieldType.BOOLEAN, description="Is there any chapter or other mention of a risk-based approach?", include_reasoning=True),
]


# BRA Template Fields
BRA_FIELDS = COMMON_FIELDS + [
    FieldDefinition(name="customer_risk_assessment", data_type=FieldType.BOOLEAN, description="Is there any chapter or mention of the risks of their customers?", include_reasoning=True),
    FieldDefinition(name="distribution_channel_risk", data_type=FieldType.BOOLEAN, description="Is there any chapter or mention of a risks of its distribution channels or similar?", include_reasoning=True),
    FieldDefinition(name="geographical_risk", data_type=FieldType.BOOLEAN, description="Is there any chapter or mention of the risks of geographical factors connected to the company?", include_reasoning=True),
    FieldDefinition(name="product_risk_assessment", data_type=FieldType.BOOLEAN, description="Is there any chapter or mention of the risks of the products and services they offer to their customers?", include_reasoning=True),
]


# Ownership Template Fields
OWNERSHIP_STRUCTURE_INSTRUCTIONS = """
Extract the complete ownership structure from the document.

STEP-BY-STEP PROCESS:
1. IDENTIFY the main/subject company - this is the company being OWNED, at the END of the ownership chain (the subsidiary, not the parent). In org charts, this is typically at the BOTTOM.
   - Assign this main company "Level 0".
2. IDENTIFY direct shareholders/owners of the main company.
   - Assign these "Level 1".
3. IDENTIFY owners of the Level 1 entities.
   - Assign these "Level 2".
4. Continue upward until you reach the Ultimate Beneficial Owners (UBOs) or top-level parent companies.
5. ASSIGN a unique temp_id to each entity (e.g., "entity_1", "entity_2").

EXTRACTION RULES:
- "type" MUST be exactly "company" or "individual".
- ONLY extract information EXPLICITLY shown.
- Extract company numbers (registration IDs), country codes, and addresses when visible.
- For ownership percentages, use exact values (e.g., 20.97).
- "main_company_id" MUST be the temp_id of the Level 0 subject company.

RELATIONSHIP DIRECTION:
- Relationships go FROM the owner TO the owned entity.
- Example: If Company A owns Company B, relation is A -> B.

RELATIONSHIP TYPES:
- "ownership": Entity holds shares/stake.

OUTPUT FORMAT:
Return a structured JSON with:
- main_company_id: temp_id of the subject company (Level 0)
- entities: Array of all entities with details and level
- relationships: Array of all relationships
"""

OWNERSHIP_STRUCTURE_INSTRUCTIONS_WITH_NON_EQUITY = """
Extract the complete ownership structure from the document.

STEP-BY-STEP PROCESS:
1. IDENTIFY the main/subject company - this is the company being OWNED, at the END of the ownership chain (the subsidiary, not the parent). In org charts, this is typically at the BOTTOM.
   - Assign this main company "Level 0".
2. IDENTIFY direct shareholders/owners of the main company.
   - Assign these "Level 1".
3. IDENTIFY owners of the Level 1 entities.
   - Assign these "Level 2".
4. Continue upward until you reach the Ultimate Beneficial Owners (UBOs) or top-level parent companies.
5. ASSIGN a unique temp_id to each entity (e.g., "entity_1", "entity_2").

EXTRACTION RULES:
- "type" MUST be exactly "company" or "individual".
- ONLY extract information EXPLICITLY shown.
- Extract company numbers (registration IDs), country codes, and addresses when visible.
- For ownership percentages, use exact values (e.g., 20.97).
- "main_company_id" MUST be the temp_id of the Level 0 subject company.

RELATIONSHIP DIRECTION:
- Relationships go FROM the owner TO the owned entity.
- Example: If Company A owns Company B, relation is A -> B.

RELATIONSHIP TYPES (include ALL that apply):
- "ownership": Entity holds shares/stake
- "director": Entity is a director
- "auditor": Entity is an auditor
- "secretary": Entity is a company secretary
- "other": Other non-equity roles

OUTPUT FORMAT:
Return a structured JSON with:
- main_company_id: temp_id of the subject company (Level 0)
- entities: Array of all entities with details and level
- relationships: Array of all relationships
"""

OWNERSHIP_FIELDS = COMMON_FIELDS + [
    FieldDefinition(
        name="ownership_structure",
        data_type=FieldType.OWNERSHIP_STRUCTURE,
        description=OWNERSHIP_STRUCTURE_INSTRUCTIONS,
        length=FieldLength.LONG,
        include_non_equity_roles=False
    )
]


# Default templates dictionary
DEFAULT_TEMPLATES = {
    "AML": AML_FIELDS,
    "BRA": BRA_FIELDS,
    "Ownership": OWNERSHIP_FIELDS,
}


def get_default_templates():
    """
    Returns a fresh copy of the default templates.
    Use this to initialize session state to avoid reference issues.
    """
    return {
        name: list(fields) 
        for name, fields in DEFAULT_TEMPLATES.items()
    }
