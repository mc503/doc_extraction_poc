
from enum import Enum

class FieldType(str, Enum):
    STRING = "String"
    OWNERSHIP_GRAPH = "Ownership Graph"

print(f"str(FieldType.OWNERSHIP_GRAPH) = '{str(FieldType.OWNERSHIP_GRAPH)}'")
print(f"FieldType.OWNERSHIP_GRAPH.value = '{FieldType.OWNERSHIP_GRAPH.value}'")
print(f"Identity check: {str(FieldType.OWNERSHIP_GRAPH) == FieldType.OWNERSHIP_GRAPH.value}")
