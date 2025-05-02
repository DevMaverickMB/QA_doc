# Component Action Documentation Generator

A specialized tool that automatically generates comprehensive component action documentation from codebases, making it easier for QA testers to understand and test applications effectively.

## Features

- **Component Action Documentation**: Create detailed mapping of UI components to their actions, effects, validation rules, and error scenarios
- **Function Documentation**: Extract and document important functions, including parameters, return values, and dependencies
- **UI Element Analysis**: Identify and document UI elements and their functionality
- **Behavior Analysis**: Map out key system behaviors and the abstractions involved
- **Dependency Tracking**: Document internal and external dependencies and their impact
- **Visual Representation**: Generate Mermaid diagrams showing the connections between components and workflows
- **CSV Export**: Extract test case tables from QA documentation to CSV files for easy import into test management tools
- **Business Logic Extraction**: Extract and document business logic from SQL stored procedures to understand application functionality
- **Combined Processing**: Process all three functionalities (component action, CSV extraction, business logic) sequentially with a single command
- **Sequential Execution**: The combined flow processes each step in sequence - first component actions, then CSV extraction, and finally business logic extraction
- **Error Handling**: Robust error handling with detailed error messages and stack traces in verbose mode
- **Programmatic API**: Use the tool programmatically in your own Python applications

## Usage

For component action documentation generation:
```bash
python main.py --repo https://github.com/username/repository
```

For business logic extraction from stored procedures:
```bash
python main.py --repo https://github.com/username/repository --business-logic
```

For combined processing of component actions, CSV extraction, and business logic:
```bash
python main.py --repo https://github.com/username/repository --combined
```

For verbose output with detailed logging (helpful for troubleshooting):
```bash
python main.py --repo https://github.com/username/repository --combined --verbose
```

Or for local directories:

```bash
python main.py --dir /path/to/local/directory
```

### Programmatic Usage

The tool can also be used programmatically through the provided `run_agent.py` script:

```bash
python run_agent.py --input /path/to/source/code --output /path/to/output/directory
```

Or imported and used in your own Python code:

```python
from run_agent import run_agent

# Run the agent on a source directory
try:
    results = run_agent(
        input_dir="/path/to/source/code",
        output_dir="/path/to/output",
        include_patterns=["*.py", "*.sql", "*.js"],
        exclude_patterns=["tests/*", "node_modules/*"],
        verbose=True  # Set to True for detailed logging
    )

    # Access the results
    print(f"Documentation generated at: {results.get('qa_document_path')}")
    print(f"CSV file generated at: {results.get('csv_path')}")
    print(f"Business logic document: {results.get('business_logic_document')}")
except Exception as e:
    print(f"Error running the agent: {e}")
```

### Optional Arguments

```
--name          Project name (derived from repo/directory if not provided)
--token         GitHub personal access token (reads from GITHUB_TOKEN env var if not provided)
--output        Base directory for output (default: qa_docs)
--max-size      Maximum file size in bytes (default: 100000, about 100KB)
--include       Include file patterns (e.g., '*.py' '*.js')
--exclude       Exclude file patterns (e.g., 'tests/*' 'docs/*')
--csharp-web    Use C# web application specific patterns
--csv           Extract test case tables to CSV files for easy import into test management tools
--business-logic Extract business logic from SQL stored procedures
--combined      Run all processing modes (component action, CSV extraction, and business logic) in one go
--verbose, -v   Enable verbose output for debugging
```

## Output

The tool generates:

1. **QA_Testing_Documentation.md**: Main document containing:
   - Application overview
   - System architecture
   - Technology stack
   - Component action mapping
   - User interaction flows
   - Acceptance criteria
   - Error handling and edge cases
   - Integration points
   - State management
   - Configuration dependencies

2. **Component_Action_Reference.md**: Comprehensive action reference tables, including:
   - Component inventory with detailed properties
   - Trigger/event documentation
   - Data elements
   - Validation rules
   - Error scenarios
   - Test priority
   - Expected performance metrics

3. **Project_Business_Logic.md**: (When --business-logic or --combined is used) Business logic documentation including:
   - Overview of the application's purpose
   - Core business domains and their relationships
   - Key business processes implemented in the database
   - Business rules enforced through stored procedures
   - Data flow through the application
   - Business entities and their relationships

4. **test_cases.csv**: (When --csv or --combined is used) CSV file containing extracted test cases for import into test management tools

## Requirements

- Python 3.6+
- Google Gemini API key or other LLM provider API key (set in .env file)

## Installation

```bash
git clone https://github.com/username/repository.git
cd repository
pip install -r requirements.txt
cp .env.example .env
# Edit .env with your API keys
```

## How It Works

The tool uses an efficient flow-based architecture:

1. **Repository Analysis**: Fetches and analyzes the codebase structure
2. **Sequential Processing**: When using combined mode, processes:
   1. First, component action documentation 
   2. Then, CSV extraction
   3. Finally, business logic extraction
3. **LLM-Powered Analysis**: Utilizes LLMs to intelligently extract:
   - Code abstractions and relationships
   - Component actions and behaviors
   - Business logic from stored procedures
4. **Output Generation**: Creates detailed documentation in markdown format and CSV exports

## Error Handling

The tool includes robust error handling:

- Input validation to ensure directories exist
- Exception catching with informative error messages
- Stack trace output in verbose mode
- Proper exit codes for CI/CD pipelines

# Agent for QA

An AI-powered tool for generating QA testing documentation from code.

## Features

- Analyzes codebases to understand components, actions, and data elements
- Automatically creates QA documentation including test cases and acceptance criteria
- Exports test cases to CSV format for easy import into test management systems
- Extracts business logic from stored procedures to understand database-level functionality
- Customizable to various frameworks and project types
- Template-driven approach for consistent documentation style
- Combined mode for processing all documentation types at once

## Installation

1. Clone this repository
2. Create a virtual environment: `python -m venv env`
3. Activate the environment:
   - Windows: `env\Scripts\activate`
   - Mac/Linux: `source env/bin/activate`
4. Install dependencies: `pip install -r requirements.txt`
5. Copy `.env.example` to `.env` and set your API keys

## Usage

### Basic Usage

```bash
python main.py --repo <github-repo-url>
```

or for a local directory:

```bash
python main.py --dir <path-to-directory>
```

### Combined Processing

Process component actions, CSV extraction, and business logic all at once:

```bash
python main.py --dir ./my-project --combined
```

### Verbose Mode

Enable detailed logging for troubleshooting:

```bash
python main.py --dir ./my-project --combined --verbose
```

### Additional Options

```bash
python main.py --dir ./my-project \
  --name "My Project Name" \
  --output ./documentation \
  --include "*.js" "*.jsx" "*.sql" \
  --exclude "node_modules/*" "tests/*" \
  --max-size 200000 \
  --combined \
  --verbose
```

### Using Custom Templates

The QA documentation generation supports custom templates for consistent formatting:

1. **Default Template**: The system includes a default template at `utils/qa_template.md`
2. **Custom Template**: You can create your own template with the exact structure you want

To use a custom template:

1. Create your markdown template file with the desired structure
2. Place it at `utils/qa_template.md` to replace the default template
3. Run the documentation generator as usual

The AI will follow the exact structure, headings, tables, and formatting of your template while filling in content specific to the analyzed code.

## Output

The documentation is generated in markdown format and saved to the specified output directory (default: `./qa_docs`). 

When using the combined mode (--combined flag):
- Component action documentation is generated
- Test cases are exported to CSV for easy import into test management tools
- Business logic documentation is generated from SQL stored procedures

This provides a comprehensive documentation suite covering both frontend and backend aspects of the application. 