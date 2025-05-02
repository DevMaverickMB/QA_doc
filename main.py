import argparse
import os
import dotenv
from flow import create_component_action_flow, create_business_logic_flow, create_combined_flow

# Load environment variables
dotenv.load_dotenv()

# Default file patterns
DEFAULT_INCLUDE_PATTERNS = {
    "*.py", "*.js", "*.jsx", "*.ts", "*.tsx", "*.go", "*.java", "*.pyi", "*.pyx",
    "*.c", "*.cc", "*.cpp", "*.h", "*.md", "*.rst", "Dockerfile",
    "Makefile", "*.yaml", "*.yml", "*.aspx", "*.aspx.cs", "*.aspx.designer.cs", "*.css",
    "*.sql", "*.proc", "*.stored_procedure"  # Added SQL-specific patterns
}

DEFAULT_EXCLUDE_PATTERNS = {
    "*test*", "tests/*", "docs/*", "examples/*", "v1/*",
    "dist/*", "build/*", "experimental/*", "deprecated/*",
    "legacy/*", ".git/*", ".github/*", ".next/*", ".vscode/*", "obj/*", "bin/*", "node_modules/*", "*.log",
    "*.jpg", "*.png", "*.xlsx", "*.rdlc", "*.pdf"
}

def main():
    parser = argparse.ArgumentParser(description="QA Documentation Generator")
    
    # Create mutually exclusive group for source
    source_group = parser.add_mutually_exclusive_group(required=True)
    source_group.add_argument("--repo", help="URL of the GitHub repository.")
    source_group.add_argument("--dir", help="Path to local directory.")
    
    # Add other arguments
    parser.add_argument("-n", "--name", help="Project name (optional, derived from repo/directory if omitted).")
    parser.add_argument("-t", "--token", help="GitHub personal access token (optional, reads from GITHUB_TOKEN env var if not provided).")
    parser.add_argument("-o", "--output", default="qa_docs", help="Base directory for output (default: ./qa_docs).")
    parser.add_argument("-i", "--include", nargs="+", help="Include file patterns (e.g. '*.py' '*.js'). Defaults to common code files if not specified.")
    parser.add_argument("-e", "--exclude", nargs="+", help="Exclude file patterns (e.g. 'tests/*' 'docs/*'). Defaults to test/build directories if not specified.")
    parser.add_argument("-s", "--max-size", type=int, default=100000, help="Maximum file size in bytes (default: 100000, about 100KB).")
    parser.add_argument("-v", "--verbose", action="store_true", help="Enable verbose output for debugging.")
    
    # Processing mode flags - fixed to use mutually exclusive group properly
    mode_group = parser.add_mutually_exclusive_group()
    mode_group.add_argument("--component-action", action="store_true", help="Generate component action documentation")
    mode_group.add_argument("--csv", action="store_true", help="Extract test case tables to CSV files for easy import into test management tools")
    mode_group.add_argument("--business-logic", action="store_true", help="Extract business logic from SQL stored procedures")
    mode_group.add_argument("--combined", action="store_true", help="Run all processing modes (component action, CSV extraction, and business logic) in one go")
    
    args = parser.parse_args()
    
    # Get GitHub token from argument or environment variable if using repo
    github_token = None
    if args.repo:
        github_token = args.token or os.environ.get('GITHUB_TOKEN')
        if not github_token:
            print("Warning: No GitHub token provided. You might hit rate limits for public repositories.")
    
    # Create the output directory if it doesn't exist
    os.makedirs(args.output, exist_ok=True)
    
    # Initialize shared store with all parameters
    shared = {
        "repo_url": args.repo,
        "local_dir": args.dir,
        "project_name": args.name,  # Can be None, FetchRepo will derive it
        "github_token": github_token,
        "output_dir": args.output,
        
        # Add include/exclude patterns and max file size
        "include_patterns": set(args.include) if args.include else DEFAULT_INCLUDE_PATTERNS,
        "exclude_patterns": set(args.exclude) if args.exclude else DEFAULT_EXCLUDE_PATTERNS,
        "max_file_size": args.max_size,
        "verbose": args.verbose,
        
        # These will be populated by nodes
        "files": [],
        "abstractions": [],
        "relationships": {}
    }
    
    # Display starting message
    source_path = args.repo or args.dir
    print(f"Starting documentation generation for: {source_path}")
    print(f"Include patterns: {', '.join(shared['include_patterns'])}")
    print(f"Exclude patterns: {', '.join(shared['exclude_patterns'])}")
    print(f"Max file size: {shared['max_file_size']} bytes")
    
    try:
        # Run the appropriate flow based on the arguments
        if args.combined:
            # Run the combined flow that processes all tasks sequentially
            print("Running sequential processing:")
            print("Step 1: Creating component action documentation...")
            print("Step 2: Generating CSV file with extracted test cases...")
            print("Step 3: Creating business logic files from code and stored procedures...")
            
            flow = create_combined_flow()
            flow.run(shared)
            
            # Output success messages for each component
            print("\nSequential processing completed successfully:")
            if "qa_document_path" in shared:
                print(f"✅ Step 1: Component action documentation generated: {shared['qa_document_path']}")
            
            if "csv_path" in shared:
                print(f"✅ Step 2: Test cases extracted to CSV file: {shared['csv_path']}")
            
            if "business_logic_document" in shared:
                if isinstance(shared["business_logic_document"], list):
                    print(f"✅ Step 3: Business logic documents generated:")
                    for doc in shared["business_logic_document"]:
                        print(f"   - {doc}")
                else:
                    print(f"✅ Step 3: Business logic document generated: {shared['business_logic_document']}")
        elif args.business_logic:
            # Run the business logic extraction flow
            print("Extracting business logic from SQL stored procedures...")
            flow = create_business_logic_flow()
            flow.run(shared)
            
            if "business_logic_document" in shared:
                if isinstance(shared["business_logic_document"], list):
                    print(f"Business logic documents generated successfully:")
                    for doc in shared["business_logic_document"]:
                        print(f" - {doc}")
                else:
                    print(f"Business logic document generated successfully: {shared['business_logic_document']}")
            else:
                print("No business logic document was generated. Check if any SQL stored procedures were found.")
        elif args.csv:
            # Run the component action documentation flow with CSV extraction focus
            print("Generating component action documentation with CSV test case extraction...")
            flow = create_component_action_flow()
            flow.run(shared)
            
            if "csv_path" in shared:
                print(f"Test cases extracted to CSV file: {shared['csv_path']}")
                print(f"This CSV file can be imported into your test management tool.")
            else:
                print("No CSV file was generated. Check if any test cases were found.")
        else:  # Default to component action if no specific flag or component-action is set
            # Run the component action documentation flow
            print("Generating component action documentation...")
            flow = create_component_action_flow()
            flow.run(shared)
            print(f"QA documentation generated successfully in {args.output}/")
    except Exception as e:
        print(f"Error during documentation generation: {e}")
        if args.verbose:
            import traceback
            traceback.print_exc()
        return 1
        
    return 0

if __name__ == "__main__":
    exit_code = main()
    exit(exit_code)
