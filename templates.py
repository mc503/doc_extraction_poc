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
OWNERSHIP_GRAPH_DESCRIPTION = (
    "Extract the ownership structure as a graph. "
    "CRITICAL: Create a SEPARATE node object for EACH distinct entity (Person or Company) found in the chart. "
    "Do NOT merge a company and its owner into the same object. "
    "1. Identify every distinct box or name. "
    "2. Assign a unique ID to each. "
    "3. Define relationships in 'adj': if A owns B, put B's ID in A's adjacency list. "
    "4. IMPORTANT: If a person is labeled as 'UBO', 'Director', etc., include this in 'entityRoles' within the adjacency object linking to them. "
    "5. 'details' must ONLY contain info specific to that single entity. "
    "6. STRICTLY normalize 'type' in details to 'company' or 'individual'. Never use 'human', 'person', etc."
    "7. Output a flat JSON Array of these node objects."
)

OWNERSHIP_FIELDS = COMMON_FIELDS + [
    FieldDefinition(
        name="ownership_graph", 
        data_type=FieldType.OWNERSHIP_GRAPH, 
        description=OWNERSHIP_GRAPH_DESCRIPTION, 
        length=FieldLength.LONG
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
