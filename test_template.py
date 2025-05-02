#!/usr/bin/env python3
"""
Test script to demonstrate the template-based QA documentation generation
"""

import os
import sys
import argparse
from utils.call_llm import call_llm
from nodes import ComponentActionDocumentation

def main():
    parser = argparse.ArgumentParser(description="Test template-based QA documentation")
    parser.add_argument("--template", help="Path to a custom template file", default=None)
    args = parser.parse_args()
    
    # Prepare a simple test context
    test_context = {
        "project_name": "Template Test Project",
        "ui_files": [("ui/Login.jsx", "// Component for user login\nfunction Login() { /* login code */ }")],
        "service_files": [("services/auth.js", "// Authentication service\nexport function login() { /* auth code */ }")],
        "component_files": [("components/Button.js", "// Custom button component\nexport default Button = () => { /* button code */ }")],
        "ui_elements": [{"name": "Login Form", "description": "User authentication form"}],
        "behaviors": [{"name": "Form Validation", "description": "Validates user input"}],
        "functions": [{"name": "authenticateUser", "description": "Verifies credentials"}],
        "abstractions": [{"name": "User Authentication", "description": "Handles user login/logout", "files": [0]}],
        "files_data": [("ui/Login.jsx", "// Login component")],
        "base_name": "Template_Test"
    }
    
    # Create the ComponentActionDocumentation node
    doc_node = ComponentActionDocumentation()
    
    # If a custom template was provided, load it
    if args.template:
        if os.path.exists(args.template):
            with open(args.template, "r", encoding="utf-8") as f:
                template_content = f.read()
                print(f"Loaded custom template from {args.template}")
                # Set the template content directly
                doc_node.template_content = template_content
        else:
            print(f"Error: Template file {args.template} not found")
            return 1
    
    # Execute the node
    try:
        document = doc_node.exec(test_context)
        
        # Save the output
        output_dir = "template_test"
        os.makedirs(output_dir, exist_ok=True)
        output_file = os.path.join(output_dir, "Test_QA_Document.md")
        
        with open(output_file, "w", encoding="utf-8") as f:
            f.write(document)
        
        print(f"Generated test document saved to {output_file}")
        return 0
    except Exception as e:
        print(f"Error generating documentation: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main()) 