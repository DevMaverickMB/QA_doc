#!/usr/bin/env python3
"""
Script to run the combined agent from code, providing all the files at once.
This demonstrates how to run the agent programmatically.
"""

import os
import sys
import argparse
import traceback
from flow import create_combined_flow

# Import default file patterns from main.py to maintain consistency
try:
    from main import DEFAULT_INCLUDE_PATTERNS, DEFAULT_EXCLUDE_PATTERNS
except ImportError:
    # Fallback if import fails
    DEFAULT_INCLUDE_PATTERNS = {
        "*.py", "*.js", "*.jsx", "*.ts", "*.tsx", "*.go", "*.java", "*.pyi", "*.pyx",
        "*.c", "*.cc", "*.cpp", "*.h", "*.md", "*.rst", "Dockerfile",
        "Makefile", "*.yaml", "*.yml", "*.aspx", "*.aspx.cs", "*.aspx.designer.cs", "*.css",
        "*.sql", "*.proc", "*.stored_procedure"
    }
    
    DEFAULT_EXCLUDE_PATTERNS = {
        "*test*", "tests/*", "docs/*", "examples/*", "v1/*",
        "dist/*", "build/*", "experimental/*", "deprecated/*",
        "legacy/*", ".git/*", ".github/*", ".next/*", ".vscode/*", "obj/*", "bin/*", "node_modules/*", "*.log",
        "*.jpg", "*.png", "*.xlsx", "*.rdlc", "*.pdf"
    }

def run_agent(input_dir, output_dir, include_patterns=None, exclude_patterns=None, verbose=False):
    """
    Run the combined agent on the specified directory.
    
    Args:
        input_dir (str): Directory containing source code to analyze
        output_dir (str): Directory where output files will be saved
        include_patterns (list, optional): File patterns to include (e.g., ["*.py", "*.sql"])
        exclude_patterns (list, optional): File patterns to exclude (e.g., ["tests/*"])
        verbose (bool, optional): Enable verbose output for debugging
    
    Returns:
        dict: Shared data store with results
        
    Raises:
        FileNotFoundError: If the input directory doesn't exist
        Exception: For other errors during processing
    """
    # Validate input directory exists
    if not os.path.exists(input_dir):
        raise FileNotFoundError(f"Input directory not found: {input_dir}")
    
    # Default include patterns if not specified
    if include_patterns is None:
        include_patterns = DEFAULT_INCLUDE_PATTERNS
    
    # Default exclude patterns if not specified
    if exclude_patterns is None:
        exclude_patterns = DEFAULT_EXCLUDE_PATTERNS
    
    # Create output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)
    
    # Initialize shared data store
    shared = {
        "repo_url": None,  # Not using repo URL, only local dir
        "local_dir": input_dir,
        "project_name": os.path.basename(os.path.abspath(input_dir)),  # Derive name from directory
        "github_token": None,  # Not needed for local dir
        "output_dir": output_dir,
        
        # File patterns and size limit
        "include_patterns": set(include_patterns),
        "exclude_patterns": set(exclude_patterns),
        "max_file_size": 200000,  # 200KB limit
        "verbose": verbose,
        
        # These will be populated by nodes
        "files": [],
        "abstractions": [],
        "relationships": {}
    }
    
    # Create and run the combined flow
    print(f"Starting sequential analysis for: {input_dir}")
    print(f"Output will be saved to: {output_dir}")
    print(f"Step 1: Creating component action documentation...")
    print(f"Step 2: Generating CSV file with extracted test cases...")
    print(f"Step 3: Creating business logic files from code and stored procedures...")
    
    if verbose:
        print(f"Include patterns: {', '.join(shared['include_patterns'])}")
        print(f"Exclude patterns: {', '.join(shared['exclude_patterns'])}")
    
    try:
        flow = create_combined_flow()
        flow.run(shared)
        return shared
    except Exception as e:
        print(f"Error during analysis: {e}")
        if verbose:
            traceback.print_exc()
        raise

def main():
    parser = argparse.ArgumentParser(description="Run the combined agent from code")
    parser.add_argument("--input", required=True, help="Input directory with source code")
    parser.add_argument("--output", default="qa_docs", help="Output directory (default: ./qa_docs)")
    parser.add_argument("--include", nargs="+", help="File patterns to include (e.g., '*.py' '*.sql')")
    parser.add_argument("--exclude", nargs="+", help="File patterns to exclude (e.g., 'tests/*')")
    parser.add_argument("--verbose", "-v", action="store_true", help="Enable verbose output for debugging")
    
    args = parser.parse_args()
    
    try:
        # Run the agent
        results = run_agent(
            input_dir=args.input,
            output_dir=args.output,
            include_patterns=args.include,
            exclude_patterns=args.exclude,
            verbose=args.verbose
        )
        
        # Print summary of results
        print("\nAnalysis completed!")
        print("\nSequential processing completed successfully:")
        if "qa_document_path" in results:
            print(f"✅ Step 1: Component action documentation generated: {results['qa_document_path']}")
        
        if "csv_path" in results:
            print(f"✅ Step 2: Test cases extracted to CSV: {results['csv_path']}")
        
        if "business_logic_document" in results:
            if isinstance(results['business_logic_document'], list):
                print(f"✅ Step 3: Business logic documents generated:")
                for doc in results['business_logic_document']:
                    print(f"   - {doc}")
            else:
                print(f"✅ Step 3: Business logic document: {results['business_logic_document']}")
        
        return 0
    except FileNotFoundError as e:
        print(f"Error: {e}")
        return 1
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        if args.verbose:
            traceback.print_exc()
        return 1

if __name__ == "__main__":
    sys.exit(main()) 