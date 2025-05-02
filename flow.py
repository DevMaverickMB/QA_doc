from pocketflow import Flow
# Import only component action documentation related nodes
from nodes import (
    FetchRepo,
    IdentifyAbstractions,
    AnalyzeRelationships,
    ComponentActionDocumentation,
    ConvertDocToCSV,
    # Import the new nodes for stored procedure analysis
    ExtractStoredProcedures,
    AnalyzeBusinessLogic,
    GenerateBusinessLogicDocument
)

def create_component_action_flow():
    """Create a flow that generates component action documentation."""
    # Create nodes
    fetch_repo = FetchRepo()
    identify_abstractions = IdentifyAbstractions()
    analyze_relationships = AnalyzeRelationships()
    component_action_documentation = ComponentActionDocumentation()
    convert_doc_to_csv = ConvertDocToCSV()
    
    # Connect nodes in sequence
    fetch_repo >> identify_abstractions >> analyze_relationships >> component_action_documentation >> convert_doc_to_csv
    
    # Create flow starting with the fetch repo node
    return Flow(start=fetch_repo)

def create_business_logic_flow():
    """Create a flow that extracts business logic from stored procedures."""
    # Create nodes
    fetch_repo = FetchRepo()
    extract_procedures = ExtractStoredProcedures()
    analyze_logic = AnalyzeBusinessLogic()
    generate_document = GenerateBusinessLogicDocument()
    
    # Connect nodes in sequence
    fetch_repo >> extract_procedures >> analyze_logic >> generate_document
    
    # Create flow starting with the fetch repo node
    return Flow(start=fetch_repo)

def create_combined_flow():
    """Create a sequential flow that:
    1. First creates component action documentation
    2. Then generates CSV file with extracted test cases
    3. Finally creates business logic files from code files and stored procedures
    
    This sequential approach ensures each step completes fully before the next begins,
    allowing each stage to build on the results of the previous one.
    """
    # Create nodes
    fetch_repo = FetchRepo()
    
    # Component action documentation nodes
    identify_abstractions = IdentifyAbstractions()
    analyze_relationships = AnalyzeRelationships()
    component_action_documentation = ComponentActionDocumentation()
    convert_doc_to_csv = ConvertDocToCSV()
    
    # Business logic analysis nodes
    extract_procedures = ExtractStoredProcedures()
    analyze_logic = AnalyzeBusinessLogic()
    generate_document = GenerateBusinessLogicDocument()
    
    # Connect nodes in sequence - first component action documentation
    fetch_repo >> identify_abstractions >> analyze_relationships >> component_action_documentation
    
    # Then CSV extraction
    component_action_documentation >> convert_doc_to_csv
    
    # Finally business logic analysis
    convert_doc_to_csv >> extract_procedures >> analyze_logic >> generate_document
    
    # Create flow starting with the fetch repo node
    return Flow(start=fetch_repo)