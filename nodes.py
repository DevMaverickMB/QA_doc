import os
import re
import json
import yaml
import csv
import time
import datetime
from pocketflow import Node
from utils.crawl_github_files import crawl_github_files
from utils.call_llm import call_llm
from utils.crawl_local_files import crawl_local_files

# Helper to get content for specific file indices
def get_content_for_indices(files_data, indices):
    content_map = {}
    for i in indices:
        if 0 <= i < len(files_data):
            path, content = files_data[i]
            content_map[f"{i} # {path}"] = content # Use index + path as key for context
    return content_map

class FetchRepo(Node):
    def prep(self, shared):
        repo_url = shared.get("repo_url")
        local_dir = shared.get("local_dir")
        project_name = shared.get("project_name")
        
        if not project_name:
            # Basic name derivation from URL or directory
            if repo_url:
                project_name = repo_url.split('/')[-1].replace('.git', '')
            else:
                project_name = os.path.basename(os.path.abspath(local_dir))
            shared["project_name"] = project_name

        # Get file patterns directly from shared
        include_patterns = shared["include_patterns"]
        exclude_patterns = shared["exclude_patterns"]
        max_file_size = shared["max_file_size"]

        return {
            "repo_url": repo_url,
            "local_dir": local_dir,
            "token": shared.get("github_token"),
            "include_patterns": include_patterns,
            "exclude_patterns": exclude_patterns,
            "max_file_size": max_file_size,
            "use_relative_paths": True
        }

    def exec(self, prep_res):
        if prep_res["repo_url"]:
            print(f"Crawling repository: {prep_res['repo_url']}...")
            result = crawl_github_files(
                repo_url=prep_res["repo_url"],
                token=prep_res["token"],
                include_patterns=prep_res["include_patterns"],
                exclude_patterns=prep_res["exclude_patterns"],
                max_file_size=prep_res["max_file_size"],
                use_relative_paths=prep_res["use_relative_paths"]
            )
        else:
            print(f"Crawling directory: {prep_res['local_dir']}...")
            result = crawl_local_files(
                directory=prep_res["local_dir"],
                include_patterns=prep_res["include_patterns"],
                exclude_patterns=prep_res["exclude_patterns"],
                max_file_size=prep_res["max_file_size"],
                use_relative_paths=prep_res["use_relative_paths"]
            )
            
        # Convert dict to list of tuples: [(path, content), ...]
        files_list = list(result.get("files", {}).items())
        print(f"Fetched {len(files_list)} files.")
        return files_list

    def post(self, shared, prep_res, exec_res):
        shared["files"] = exec_res # List of (path, content) tuples

class IdentifyAbstractions(Node):
    def prep(self, shared):
        files_data = shared["files"]
        project_name = shared["project_name"]  # Get project name
        
        # Helper to create context from files, respecting limits (basic example)
        def create_llm_context(files_data):
            context = ""
            file_info = [] # Store tuples of (index, path)
            for i, (path, content) in enumerate(files_data):
                entry = f"--- File Index {i}: {path} ---\n{content}\n\n"
                context += entry
                file_info.append((i, path))

            return context, file_info # file_info is list of (index, path)

        context, file_info = create_llm_context(files_data)
        # Format file info for the prompt (comment is just a hint for LLM)
        file_listing_for_prompt = "\n".join([f"- {idx} # {path}" for idx, path in file_info])
        return context, file_listing_for_prompt, len(files_data), project_name  # Return project name

    def exec(self, prep_res):
        context, file_listing_for_prompt, file_count, project_name = prep_res
        print("Identifying abstractions using LLM...")
        prompt = f"""
For the project `{project_name}`:

Codebase Context:
{context}

Analyze the codebase context.
Identify the top 5-10 core most important abstractions to help those new to the codebase.

For each abstraction, provide:
1. A concise `name`.
2. A beginner-friendly `description` explaining what it is with a simple analogy, in around 100 words.
3. A list of relevant `file_indices` (integers) using the format `idx # path/comment`.

List of file indices and paths present in the context:
{file_listing_for_prompt}

Format the output as a YAML list of dictionaries:

```yaml
- name: Query Processing
  description: | 
    Explains what the abstraction does.
    It's like a central dispatcher routing requests.
  file_indices:
    - 0 # path/to/file1.py
    - 3 # path/to/related.py
- name: Query Optimization
  description: |
    Another core concept, similar to a blueprint for objects.
  file_indices:
    - 5 # path/to/another.js
# ... up to 10 abstractions
```"""
        response = call_llm(prompt)

        # --- Validation ---
        yaml_str = response.strip().split("```yaml")[1].split("```")[0].strip()
        abstractions = yaml.safe_load(yaml_str)

        if not isinstance(abstractions, list):
            raise ValueError("LLM Output is not a list")

        validated_abstractions = []
        for item in abstractions:
            if not isinstance(item, dict) or not all(k in item for k in ["name", "description", "file_indices"]):
                raise ValueError(f"Missing keys in abstraction item: {item}")
            if not isinstance(item["description"], str):
                 raise ValueError(f"description is not a string in item: {item}")
            if not isinstance(item["file_indices"], list):
                 raise ValueError(f"file_indices is not a list in item: {item}")

            # Validate indices
            validated_indices = []
            for idx_entry in item["file_indices"]:
                 try:
                     if isinstance(idx_entry, int):
                         idx = idx_entry
                     elif isinstance(idx_entry, str) and '#' in idx_entry:
                          idx = int(idx_entry.split('#')[0].strip())
                     else:
                          idx = int(str(idx_entry).strip())

                     if not (0 <= idx < file_count):
                         raise ValueError(f"Invalid file index {idx} found in item {item['name']}. Max index is {file_count - 1}.")
                     validated_indices.append(idx)
                 except (ValueError, TypeError):
                      raise ValueError(f"Could not parse index from entry: {idx_entry} in item {item['name']}")

            item["files"] = sorted(list(set(validated_indices)))
            # Store only the required fields
            validated_abstractions.append({
                "name": item["name"],
                "description": item["description"],
                "files": item["files"]
            })

        print(f"Identified {len(validated_abstractions)} abstractions.")
        return validated_abstractions

    def post(self, shared, prep_res, exec_res):
        shared["abstractions"] = exec_res # List of {"name": str, "description": str, "files": [int]}

class AnalyzeRelationships(Node):
    def __init__(self, max_retries=3, wait=10):
        # Add more retries with wait time
        super().__init__(max_retries=max_retries, wait=wait)
        
    def prep(self, shared):
        abstractions = shared["abstractions"] # Now contains 'files' list of indices
        files_data = shared["files"]
        project_name = shared["project_name"]  # Get project name

        # Create context with abstraction names, indices, descriptions, and relevant file snippets
        context = "Identified Abstractions:\n"
        all_relevant_indices = set()
        abstraction_info_for_prompt = []
        for i, abstr in enumerate(abstractions):
            # Use 'files' which contains indices directly
            file_indices_str = ", ".join(map(str, abstr['files']))
            info_line = f"- Index {i}: {abstr['name']} (Relevant file indices: [{file_indices_str}])\n  Description: {abstr['description']}"
            context += info_line + "\n"
            abstraction_info_for_prompt.append(f"{i} # {abstr['name']}")
            all_relevant_indices.update(abstr['files'])

        context += "\nRelevant File Snippets (Referenced by Index and Path):\n"
        # Get content for relevant files using helper
        relevant_files_content_map = get_content_for_indices(
            files_data,
            sorted(list(all_relevant_indices))
        )
        # Format file content for context
        file_context_str = "\n\n".join(
            f"--- File: {idx_path} ---\n{content}"
            for idx_path, content in relevant_files_content_map.items()
        )
        context += file_context_str

        return context, "\n".join(abstraction_info_for_prompt), project_name  # Return project name

    def exec_fallback(self, prep_res, exc):
        """Provide fallback when relationship analysis fails"""
        print(f"Warning: Relationship analysis failed with error: {exc}")
        print("Generating fallback relationships...")
        
        context, abstraction_listing, project_name = prep_res
        
        # Extract the number of abstractions from the listing
        num_abstractions = len(abstraction_listing.split("\n"))
        
        # Create basic relationships that ensure every abstraction is connected
        summary = f"**{project_name}** is a web application that helps users with career-related tasks."
        
        # Create simple chain of relationships
        relationships = []
        for i in range(num_abstractions - 1):
            relationships.append({
                "from": i,
                "to": i + 1,
                "label": "Connects to"
            })
        
        # Add one relationship from last to first to create a cycle
        relationships.append({
            "from": num_abstractions - 1, 
            "to": 0,
            "label": "Provides data to"
        })
        
        # Create basic function and UI data structures for fallback
        functions = []
        ui_elements = []
        behaviors = []
        dependencies = []
        
        return {
            "summary": summary,
            "details": relationships,
            "functions": functions,
            "ui_elements": ui_elements,
            "behaviors": behaviors,
            "dependencies": dependencies
        }
        
    def exec(self, prep_res):
        context, abstraction_listing, project_name = prep_res
        print("Analyzing relationships using LLM...")
        prompt = f"""
Based on the following abstractions and relevant code snippets from the project `{project_name}`:

List of Abstraction Indices and Names:
{abstraction_listing}

Context (Abstractions, Descriptions, Code):
{context}

Please provide a comprehensive analysis of the repository with the following sections:

1. A high-level `summary` of the project's main purpose and functionality in a few beginner-friendly sentences. Use markdown formatting with **bold** and *italic* text to highlight important concepts.

2. Core Relationships (`relationships`): A list describing the key interactions between these abstractions. For each relationship, specify:
    - `from_abstraction`: Index of the source abstraction (e.g., `0 # AbstractionName1`)
    - `to_abstraction`: Index of the target abstraction (e.g., `1 # AbstractionName2`)
    - `label`: A brief label for the interaction **in just a few words** (e.g., "Manages", "Inherits", "Uses").
    Ideally the relationship should be backed by one abstraction calling or passing parameters to another.
    Simplify the relationship and exclude those non-important ones.

3. Functions (`functions`): Identify major functions in the codebase, for each function provide:
    - `name`: The name of the function (e.g., "createTutorialFlow")
    - `abstraction_index`: Index of the abstraction this function belongs to
    - `description`: A clear description of what the function does
    - `parameters`: List of parameters (if clearly identified)
    - `return_value`: What the function returns (if clearly identified)
    - `called_by`: Names of functions or components that call this function
    - `calls`: Names of other functions that this function calls

4. UI Elements (`ui_elements`): Identify UI elements if present, for each element provide:
    - `name`: The name of the UI element
    - `abstraction_index`: Index of the abstraction this UI element belongs to
    - `type`: Type of UI element (e.g., "Button", "Form", "Dropdown")
    - `description`: Description of the UI element's purpose
    - `functionality`: What happens when the user interacts with it
    - `related_functions`: Functions that this UI element triggers or is related to

5. Behaviors (`behaviors`): Identify key behaviors of the system, for each behavior provide:
    - `name`: Name of the behavior
    - `description`: Description of the behavior
    - `abstractions_involved`: List of abstraction indices involved in this behavior
    - `trigger`: What triggers this behavior
    - `outcome`: What is the outcome of this behavior
    - `sequence`: Brief sequence of steps that occur during this behavior

6. Dependencies (`dependencies`): Identify key external and internal dependencies, for each dependency provide:
    - `name`: Name of the dependency
    - `type`: Type ("external" or "internal")
    - `used_by`: List of abstraction indices that use this dependency
    - `purpose`: Why this dependency is used
    - `impact`: How critical this dependency is to the system

IMPORTANT: Make sure EVERY abstraction is involved in at least ONE relationship (either as source or target). Each abstraction index must appear at least once across all relationships.

Format the output as YAML:

```yaml
summary: |
  A brief, simple explanation of the project.
  Can span multiple lines with **bold** and *italic* for emphasis.
relationships:
  - from_abstraction: 0 # AbstractionName1
    to_abstraction: 1 # AbstractionName2
    label: "Manages"
  - from_abstraction: 2 # AbstractionName3
    to_abstraction: 0 # AbstractionName1
    label: "Provides config"
  # ... other relationships
functions:
  - name: "functionName"
    abstraction_index: 0
    description: "What this function does"
    parameters: ["param1", "param2"]
    return_value: "What it returns"
    called_by: ["callerFunction1", "callerFunction2"]
    calls: ["calledFunction1", "calledFunction2"]
  # ... other functions
ui_elements:
  - name: "elementName"
    abstraction_index: 1
    type: "Button"
    description: "Purpose of this element"
    functionality: "What happens on interaction"
    related_functions: ["function1", "function2"]
  # ... other UI elements
behaviors:
  - name: "behaviorName"
    description: "Description of this behavior"
    abstractions_involved: [0, 1, 2]
    trigger: "What causes this behavior"
    outcome: "Result of this behavior"
    sequence: "Step 1 -> Step 2 -> Step 3"
  # ... other behaviors
dependencies:
  - name: "dependencyName"
    type: "external"
    used_by: [0, 1]
    purpose: "Why this dependency is used"
    impact: "How critical it is for the system"
  # ... other dependencies
```

Now, provide the YAML output:
"""
        response = call_llm(prompt)

        # --- Validation ---
        yaml_str = response.strip().split("```yaml")[1].split("```")[0].strip()
        analysis_data = yaml.safe_load(yaml_str)

        if not isinstance(analysis_data, dict) or not all(k in analysis_data for k in ["summary", "relationships"]):
            raise ValueError("LLM output is not a dict or missing keys ('summary', 'relationships')")
        if not isinstance(analysis_data["summary"], str):
             raise ValueError("summary is not a string")
        if not isinstance(analysis_data["relationships"], list):
             raise ValueError("relationships is not a list")

        # Validate relationships have required fields
        seen_abstractions = set()
        for i, rel in enumerate(analysis_data["relationships"]):
            # Convert the from_abstraction field if it's a string with comments
            if isinstance(rel.get("from_abstraction"), str) and '#' in rel["from_abstraction"]:
                 # Extract just the number
                 rel["from"] = int(rel["from_abstraction"].split('#')[0].strip())
            elif isinstance(rel.get("from_abstraction"), int):
                 rel["from"] = rel["from_abstraction"]
            elif "from" not in rel:
                 raise ValueError(f"relationship at index {i} missing 'from' or 'from_abstraction'")

            # Convert the to_abstraction field if it's a string with comments
            if isinstance(rel.get("to_abstraction"), str) and '#' in rel["to_abstraction"]:
                 # Extract just the number
                 rel["to"] = int(rel["to_abstraction"].split('#')[0].strip())
            elif isinstance(rel.get("to_abstraction"), int):
                 rel["to"] = rel["to_abstraction"]
            elif "to" not in rel:
                 raise ValueError(f"relationship at index {i} missing 'to' or 'to_abstraction'")

            # Ensure 'label' is present
            if "label" not in rel:
                 rel["label"] = "Related to"

            seen_abstractions.add(rel["from"])
            seen_abstractions.add(rel["to"])

        # Add functions, UI elements, and behaviors if present
        analysis_data["functions"] = analysis_data.get("functions", [])
        analysis_data["ui_elements"] = analysis_data.get("ui_elements", [])
        analysis_data["behaviors"] = analysis_data.get("behaviors", [])
        analysis_data["dependencies"] = analysis_data.get("dependencies", [])

        # Log the analysis
        num_abstractions = len(abstraction_listing.split("\n"))
        print(f"Project summary: {analysis_data['summary'][:50]}...")
        print(f"Identified {len(analysis_data['relationships'])} relationships")
        print(f"Identified {len(analysis_data['functions'])} functions")
        print(f"Identified {len(analysis_data['ui_elements'])} UI elements")
        print(f"Identified {len(analysis_data['behaviors'])} behaviors")
        print(f"Identified {len(analysis_data['dependencies'])} dependencies")

        # Return the validated analysis data
        return {
            "summary": analysis_data["summary"],
            "details": analysis_data["relationships"],
            "functions": analysis_data["functions"],
            "ui_elements": analysis_data["ui_elements"],
            "behaviors": analysis_data["behaviors"],
            "dependencies": analysis_data["dependencies"]
        }

    def post(self, shared, prep_res, exec_res):
        # Structure is now {"summary": str, "details": [...], "functions": [...], "ui_elements": [...], 
        # "behaviors": [...], "dependencies": [...]}
        shared["relationships"] = exec_res

class ComponentActionDocumentation(Node):
    def __init__(self, max_retries=3, wait=10):
        super().__init__(max_retries=max_retries, wait=wait)
        # Load template file if it exists
        self.template_file = os.path.join(os.path.dirname(os.path.dirname(__file__)), "utils", "qa_template.md")
        self.template_content = None
        if os.path.exists(self.template_file):
            try:
                with open(self.template_file, "r", encoding="utf-8") as f:
                    self.template_content = f.read()
                print(f"QA template loaded from {self.template_file}")
            except Exception as e:
                print(f"Error loading template file: {e}")
    
    def prep(self, shared):
        project_name = shared["project_name"]
        files_data = shared["files"]
        abstractions = shared.get("abstractions", [])
        relationships_data = shared.get("relationships", {})
        output_base_dir = shared.get("output_dir", "output")

        # --- New: Determine base name from input files ---
        base_name = None
        if files_data:
            # Get all base names without extension
            base_names = [os.path.splitext(os.path.basename(path))[0] for path, _ in files_data]
            # If all base names are the same, use that; else use the first one
            if len(set(base_names)) == 1:
                base_name = base_names[0]
            else:
                # Look for common patterns like numbers in filenames that identify a component
                # Find any numeric patterns in filenames (e.g. "1455.aspx", "1455.js" -> "1455")
                number_patterns = []
                for path, _ in files_data:
                    filename = os.path.basename(path)
                    number_matches = re.findall(r'\d+', filename)
                    number_patterns.extend(number_matches)
                
                # Use the most common number pattern as the folder name if found
                if number_patterns:
                    from collections import Counter
                    most_common = Counter(number_patterns).most_common(1)
                    if most_common:
                        base_name = most_common[0][0]
                    else:
                        # Fallback to common prefix if no numbers found
                        base_name = os.path.commonprefix(base_names).rstrip('_-.') or base_names[0]
                else:
                    # Optionally, find common prefix
                    base_name = os.path.commonprefix(base_names).rstrip('_-.') or base_names[0]
        else:
            base_name = project_name or "QA_Document"

        # Create a dedicated output folder with the base name
        output_path = os.path.join(output_base_dir, base_name)
        
        # Filter UI and service-related files
        ui_files = []
        service_files = []
        component_files = []
        
        for i, (path, content) in enumerate(files_data):
            file_ext = os.path.splitext(path)[1].lower()
            filename = os.path.basename(path).lower()
            
            # Identify UI files
            if any(x in path.lower() for x in ['component', 'view', 'page', 'screen', 'ui']):
                if file_ext in ['.tsx', '.jsx', '.vue', '.svelte', '.razor', '.cshtml', '.aspx', '.html']:
                    ui_files.append((i, path, content))
                elif file_ext in ['.ts', '.js', '.cs', '.java']:
                    component_files.append((i, path, content))
            
            # Identify component files
            elif file_ext in ['.tsx', '.jsx', '.vue', '.svelte']:
                component_files.append((i, path, content))
            
            # Identify service files
            elif any(x in path.lower() for x in ['service', 'provider', 'store', 'api', 'controller']):
                service_files.append((i, path, content))
        
        # Get already processed UI elements
        ui_elements = relationships_data.get("ui_elements", [])
        behaviors = relationships_data.get("behaviors", [])
        functions = relationships_data.get("functions", [])
        
        return {
            "project_name": project_name,
            "output_path": output_path,
            "ui_files": ui_files,
            "service_files": service_files,
            "component_files": component_files,
            "ui_elements": ui_elements,
            "behaviors": behaviors,
            "functions": functions,
            "abstractions": abstractions,
            "files_data": files_data,
            "base_name": base_name  # Pass base_name forward
        }
    
    def exec(self, prep_res):
        print("Generating Component Action Documentation...")
        project_name = prep_res["project_name"]
        ui_files = prep_res["ui_files"]
        service_files = prep_res["service_files"]
        component_files = prep_res["component_files"]
        ui_elements = prep_res["ui_elements"]
        behaviors = prep_res["behaviors"]
        functions = prep_res["functions"]
        abstractions = prep_res["abstractions"]
        files_data = prep_res["files_data"]
        
        # Sample code for context
        ui_context = self._prepare_file_context(ui_files[:5])
        component_context = self._prepare_file_context(component_files[:5])
        service_context = self._prepare_file_context(service_files[:5])
        
        # Create abstraction context
        abstraction_context = self._create_abstraction_context(abstractions)
        
        # Prepare additional context from existing analysis
        ui_elements_context = self._create_ui_elements_context(ui_elements)
        behaviors_context = self._create_behaviors_context(behaviors)
        functions_context = self._create_functions_context(functions)
        
        # Prepare the overall context
        combined_context = f"""
UI Components:
{ui_context}

Component Files:
{component_context}

Service Files:
{service_context}

Abstractions:
{abstraction_context}

UI Elements:
{ui_elements_context}

Behaviors:
{behaviors_context}

Functions:
{functions_context}
"""
        
        base_name = prep_res.get("base_name", "QA_Document")
        
        # Check if a template is available in the Node or shared store
        template_content = None
        if hasattr(self, 'template_content') and self.template_content:
            template_content = self.template_content
            print(f"Using built-in template from file: {self.template_file}")
        
        # Modify the prompt based on whether we have a template
        if template_content:
            prompt = f"""
You are a senior QA tester and expert documentation writer tasked with developing comprehensive documentation for a software application specifically designed for QA testers.

Application Information:
Project Name: {project_name}

IMPORTANT: I'm providing you with a TEMPLATE document that follows the structure I want for the documentation. 
You MUST follow the EXACT same format, headings, sections, and table structure as this template. 
Do not add or remove sections - maintain the exact same structure but fill in with content relevant to the current codebase.

TEMPLATE DOCUMENT:
```
{template_content}
```

Available Context About Current Project:
{combined_context}

Instructions:
1. Study the template document carefully, noting its structure, headings, formatting, and table layouts
2. Generate a new document for the current project ({project_name}) that follows EXACTLY the same structure
3. Fill in the content based on the available context about the current project
4. Keep all headings, table formats, and section organization identical to the template
5. The ONLY thing that should change is the specific content about the components, test cases, etc.
6. Preserve all numbering schemes, bullet points, and formatting from the template

Format as a professional markdown document. DO NOT wrap your response in ```markdown code fences. Provide the content directly as it will be saved as a .md file.
"""
        else:
            # Use the original prompt if no template is available
            prompt = f"""
You are a senior QA tester and expert documentation writer tasked with developing comprehensive documentation for a software application specifically designed for QA testers. This documentation will serve as a critical resource that enables testers to thoroughly understand the application's architecture, components, functionality, and expected behaviors, leading to more effective and intelligent testing strategies.

Application Information:
Project Name: {project_name}

Available Context:
{combined_context}

Required Documentation Structure:

# {base_name} QA Document

1. Application Overview
   - Provide a clear, concise description of the application's purpose and primary functions
   - Document the technology stack, frameworks, and key dependencies

2. Component Action Mapping Documentation
   For each identified component in the application, create detailed action mapping tables with the following structure:
   
   ## [Component Name]
   | Trigger/Event | Action | Target/Effect | Data Elements | Validation Rules | Error Scenarios | Test Priority | Expected Performance |
   | ------------- | ------ | ------------- | ------------- | ---------------- | --------------- | ------------- | -------------------- |
   | [Specific event that initiates action] | [Method/function called] | [Resulting change] | [All affected data fields] | [All validation logic] | [Potential failures and handling] | [Priority level] | [Performance expectations] |


3. Acceptance Criteria and Test Cases
   - Create tables for EACH identified component in the appllication
   - For each component, provide: 
     * Clear, measurable acceptance criteria defining when the component works correctly
     * Comprehensive test cases covering all possible interactions, states, and edge cases
   - Test cases must cover:
     * All possible user inputs (valid, invalid, boundary conditions)
     * All possible component states
     * Interactions with other components
     * Performance under different conditions
   - Each test case must include:
     * Unique ID
     * Preconditions
     * Detailed steps to execute with expected result at each step
     * Expected final result
     * Severity/Priority
   
   For each component, follow this format:
    
   ## Acceptance Criteria: [Component Name]
   [Clear, measurable criteria that define when this component can be considered complete and working correctly]
   
   ## Test Cases: [Component Name]
   | Test ID | Description | Preconditions | Steps to Execute | Expected Final Result | Severity/Priority |
   | :------ | :---------- | :------------ | :--------------- | :-------------------- | :---------------- |
   | [Unique identifier] | [Brief description of what the test case is verifying] | [Required state before test execution] | [Numbered, specific actions for tester to perform] | [Overall outcome when test completes] | [High/Medium/Low] |

4. Testing Strategy and Requirements
   - Provide a comprehensive testing strategy for the application, including:
     * Types of testing to be performed (unit, integration, system, acceptance, etc.)
     * Key business requirements and how they are validated by the tests
     * Risk-based prioritization of test areas
     * Any special considerations for the application's domain or architecture
   - This section should be based on the AI agent's understanding of the code context, business logic, and requirements inferred from the codebase.

5. Error Handling and Edge Cases
   - Create comprehensive catalog of possible error conditions
   - Document expected system behavior for each error type
   - Include recovery mechanisms and fallback behaviors
   - For each error condition, provide:
     * How to reproduce the error
     * Expected error message or system behavior
     * Proper recovery steps
     * How to verify the system recovered correctly

Analysis Requirements:
Based on the provided codebase context, you must:
- Conduct thorough analysis of the actual components, methods, and behaviors present in the code
- Extract accurate component names, events, actions and data elements directly from the code
- Identify validation rules by examining form handling logic and data processing
- Determine error handling mechanisms implemented in the codebase
- Assess the relative importance of features to assign appropriate test priorities

Your documentation must be technically precise, using the exact terminology found in the codebase while remaining accessible to QA professionals who may not have deep programming expertise in the specific technology stack.

Deliverable Format:
The final documentation should be delivered as a professional markdown document with:
- Hierarchical structure using appropriate heading levels
- Tables for component action mapping
- Comprehensive test cases for each component with clear steps and expected results
- Code examples where relevant
- Cross-referencing between related sections
- A comprehensive table of contents

This documentation will serve as the authoritative reference for QA testing, enabling comprehensive test coverage and a shared understanding between development and QA teams.

Format as a professional markdown document. IMPORTANT: DO NOT wrap your response in ```markdown code fences. Provide the content directly as it will be saved as a .md file.
"""
        
        main_document = call_llm(prompt)
        
        return {
            "output_path": prep_res["output_path"],
            "main_document": main_document,
            "base_name": base_name
        }
    
    def _prepare_file_context(self, files):
        """Helper to prepare file context for the LLM"""
        if not files:
            return "No relevant files found."
        
        context = ""
        for i, path, content in files:
            # Truncate very long files
            content_lines = content.split('\n')
            if len(content_lines) > 100:
                content = '\n'.join(content_lines[:100]) + "\n... (truncated)"
            context += f"--- File: {path} ---\n{content}\n\n"
        return context
    
    def _create_abstraction_context(self, abstractions):
        """Helper to create context from abstractions"""
        if not abstractions:
            return "No abstractions identified."
        
        context = ""
        for i, abstr in enumerate(abstractions):
            context += f"Abstraction {i}: {abstr.get('name', 'Unnamed')}\n"
            context += f"Description: {abstr.get('description', 'No description')}\n\n"
        return context
    
    def _create_ui_elements_context(self, ui_elements):
        """Helper to create context from UI elements"""
        if not ui_elements:
            return "No UI elements identified."
        
        context = ""
        for ui in ui_elements:
            context += f"- {ui.get('name', 'Unnamed')} ({ui.get('type', 'UI Element')}): {ui.get('description', 'No description')}\n"
            if ui.get('functionality'):
                context += f"  Functionality: {ui['functionality']}\n"
        return context
    
    def _create_behaviors_context(self, behaviors):
        """Helper to create context from behaviors"""
        if not behaviors:
            return "No behaviors identified."
        
        context = ""
        for behavior in behaviors:
            context += f"- {behavior.get('name', 'Unnamed')}: {behavior.get('description', 'No description')}\n"
            if behavior.get('trigger'):
                context += f"  Trigger: {behavior['trigger']}\n"
            if behavior.get('outcome'):
                context += f"  Outcome: {behavior['outcome']}\n"
            if behavior.get('sequence'):
                context += f"  Sequence: {behavior['sequence']}\n"
        return context
    
    def _create_functions_context(self, functions):
        """Helper to create context from functions"""
        if not functions:
            return "No functions identified."
        
        context = ""
        for func in functions:
            context += f"- {func.get('name', 'Unnamed')}: {func.get('description', 'No description')}\n"
            if func.get('parameters'):
                context += f"  Parameters: {', '.join(func['parameters'])}\n"
            if func.get('return_value'):
                context += f"  Returns: {func['return_value']}\n"
            if func.get('called_by'):
                context += f"  Called by: {', '.join(func['called_by'])}\n"
            if func.get('calls'):
                context += f"  Calls: {', '.join(func['calls'])}\n"
        return context
    
    def post(self, shared, prep_res, exec_res):
        output_path = exec_res["output_path"]
        base_name = exec_res.get("base_name", "QA_Document")
        
        # Create output directory if it doesn't exist
        os.makedirs(output_path, exist_ok=True)
        
        # Clean markdown content
        def clean_markdown(content):
            cleaned_content = content
            if cleaned_content.strip().startswith("```markdown"):
                parts = cleaned_content.split("```", 2)
                if len(parts) >= 3:
                    cleaned_content = parts[2].strip()
            elif cleaned_content.strip().startswith("```"):
                parts = cleaned_content.split("```", 2)
                if len(parts) >= 3:
                    cleaned_content = parts[2].strip()
                    
            if cleaned_content.strip().endswith("```"):
                cleaned_content = cleaned_content.strip()[:-3].strip()
                
            return cleaned_content
        
        # Write main documentation file
        doc_filename = f"{base_name}_QA_Document.md"
        doc_path = os.path.join(output_path, doc_filename)
        with open(doc_path, "w", encoding="utf-8") as f:
            f.write(clean_markdown(exec_res["main_document"]))
            
        # Store the output path and doc filename for downstream nodes
        shared["component_action_doc_dir"] = output_path
        shared["component_action_doc_filename"] = doc_filename
        shared["base_name"] = base_name  # Store base_name in shared for downstream nodes
        
        print(f"🎉 QA Documentation successfully generated at: {output_path}")
        print(f"✨ Open {doc_path} to view the comprehensive QA documentation")
        
        return "default"

class ConvertDocToCSV(Node):
    """Node to convert test case tables to CSV file for easy import into test management tools"""
    
    def prep(self, shared):
        doc_dir = shared.get("component_action_doc_dir", "qa_docs")
        doc_filename = shared.get("component_action_doc_filename", "")
        base_name = shared.get("base_name", "")
        output_dir = shared.get("output_dir", "qa_docs")
        
        # If we have both directory and filename, construct the full path
        doc_path = None
        if doc_dir and doc_filename:
            doc_path = os.path.join(doc_dir, doc_filename)
        
        return doc_path, output_dir, base_name
        
    def exec(self, prep_res):
        doc_path, output_dir, base_name = prep_res
        
        # Create the output directory path
        # Use the base_name as part of the directory if available
        if base_name:
            output_dir = os.path.join(output_dir, base_name)
        
        os.makedirs(output_dir, exist_ok=True)
        csv_path = os.path.join(output_dir, "test_cases.csv")
        
        # Define the exact columns we want to use - add Serial Number as the first column
        standardized_columns = ['Serial Number', 'Test ID', 'Description', 'Preconditions', 'Steps to Execute', 'Expected Final Result', 'Severity/Priority']
        
        # If no doc_path is provided, create a minimal CSV with headers
        if not doc_path or not os.path.exists(doc_path):
            print(f"QA document not found at {doc_path}. Creating a placeholder CSV file.")
            with open(csv_path, 'w', newline='', encoding='utf-8') as csvfile:
                writer = csv.writer(csvfile)
                writer.writerow(standardized_columns)
                writer.writerow(['1', 'TC-DEFAULT', 'No test cases were found in the documentation', 
                                'Check the documentation for more information', 
                                'N/A', 'Low'])
            
            return {
                "csv_path": csv_path,
                "test_case_count": 0,
                "message": "Created a placeholder CSV file as no test cases were found."
            }
        
        # Read the QA document and extract test cases
        with open(doc_path, 'r', encoding='utf-8') as f:
            doc_content = f.read()
        
        print(f"Extracting test cases from {doc_path}...")
        
        # Extract test case tables using regex patterns
        # Look for tables that follow a "Test Cases" heading
        test_case_sections = []
        
        # Try to find sections with test cases
        section_patterns = [
            r'### \d+\.\d+\. Test Cases: ([^\n]+)',  # Pattern like "### 3.1. Test Cases: Component Name"
            r'### Test Cases: ([^\n]+)',             # Simpler pattern like "### Test Cases: Component Name"
            r'## Test Cases[:\s]*([^\n]+)',          # Level 2 heading like "## Test Cases: Component Name"
            r'# Test Cases[:\s]*([^\n]+)',           # Level 1 heading like "# Test Cases: Component Name"
        ]
        
        # Try each pattern
        section_matches = []
        for pattern in section_patterns:
            matches = list(re.finditer(pattern, doc_content, re.MULTILINE))
            if matches:
                section_matches = matches
                break
        
        # Process each section with test cases
        if section_matches:
            for i, match in enumerate(section_matches):
                section_title = match.group(1).strip()
                section_start = match.end()
                
                # Find end of section (next section or end of file)
                if i < len(section_matches) - 1:
                    section_end = section_matches[i+1].start()
                else:
                    section_end = len(doc_content)
                
                # Extract the section content
                section_content = doc_content[section_start:section_end]
                
                # Look for markdown tables in this section
                table_match = re.search(r'(\|[^\n]+\|(?:\n\|[^\n]+\|)+)', section_content)
                if table_match:
                    table_content = table_match.group(1)
                    test_case_sections.append((section_title, table_content))
        
        # If no sections found by headings, try to directly extract tables
        if not test_case_sections:
            # Look for markdown tables with test case headers
            all_tables = re.findall(r'(\|[^\n]+\|(?:\n\|[^\n]+\|)+)', doc_content)
            for i, table in enumerate(all_tables):
                # Extract headers
                header_match = re.match(r'\|([^\n]+)\|', table)
                if header_match:
                    headers = [h.strip() for h in header_match.group(1).split('|')]
                    # Check if this might be a test case table
                    test_headers = ['test', 'case', 'step', 'expect', 'precond', 'prior']
                    if any(any(test_h in h.lower() for test_h in test_headers) for h in headers):
                        section_title = f"Table {i+1}"
                        test_case_sections.append((section_title, table))
        
        # Process the test case sections and extract test cases
        all_test_cases = []
        
        for section_title, table_content in test_case_sections:
            # Parse the table rows
            rows = []
            for line in table_content.split('\n'):
                if line.strip() and line.strip().startswith('|') and line.strip().endswith('|'):
                    rows.append(line.strip())
            
            if len(rows) < 3:  # Need at least header, separator, and one data row
                continue
            
            # Extract headers
            header_row = rows[0]
            headers = [cell.strip() for cell in header_row.split('|')[1:-1]]
            
            # Extract data rows (skip header and separator)
            for row in rows[2:]:
                cells = [cell.strip() for cell in row.split('|')[1:-1]]
                if len(cells) == len(headers):
                    # Create dictionary mapping headers to values
                    test_case = {headers[i]: cells[i] for i in range(len(headers))}
                    test_case['Component'] = section_title  # Add component/section info
                    all_test_cases.append(test_case)
        
        # Process test cases for CSV output
        if all_test_cases:
            # Define column mappings to standardize the field names
            column_mappings = {
                'Test ID': 'Test ID',
                'Test Case ID': 'Test ID',
                'TestID': 'Test ID',
                'ID': 'Test ID',
                'Description': 'Description',
                'Test Description': 'Description',
                'Test Case Description': 'Description',
                'Preconditions': 'Preconditions',
                'Precondition': 'Preconditions',
                'Steps to Execute': 'Steps to Execute',
                'Steps': 'Steps to Execute',
                'Expected Final Result': 'Expected Final Result',
                'Expected Result': 'Expected Final Result',
                'Expected Results': 'Expected Final Result',
                'Severity/Priority': 'Severity/Priority',
                'Priority': 'Severity/Priority',
                'Severity': 'Severity/Priority'
            }
            
            # Write to CSV
            with open(csv_path, 'w', newline='', encoding='utf-8') as csvfile:
                writer = csv.DictWriter(csvfile, fieldnames=standardized_columns)
                writer.writeheader()
                
                # Track serial number for each row
                serial_number = 1
                
                for tc in all_test_cases:
                    # Create a standardized row with just our required columns
                    row = {col: '' for col in standardized_columns}
                    
                    # Add serial number to the row
                    row['Serial Number'] = str(serial_number)
                    serial_number += 1
                    
                    # Map values from original test case to our standardized columns
                    for orig_col, value in tc.items():
                        # Find the standardized column name for this original column
                        std_col = None
                        if orig_col in column_mappings:
                            std_col = column_mappings[orig_col]
                        else:
                            # Try case-insensitive match
                            for col_pattern, std_name in column_mappings.items():
                                if col_pattern.lower() == orig_col.lower():
                                    std_col = std_name
                                    break
                        
                        # If we found a mapping and it's one of our required columns, use it
                        if std_col and std_col in standardized_columns:
                            row[std_col] = value
                        # Otherwise, try to intelligently map based on column name patterns
                        elif 'id' in orig_col.lower() and 'Test ID' in standardized_columns:
                            row['Test ID'] = value
                        elif any(x in orig_col.lower() for x in ['step', 'execute', 'action']) and 'Steps to Execute' in standardized_columns:
                            row['Steps to Execute'] = value
                        elif any(x in orig_col.lower() for x in ['precond']) and 'Preconditions' in standardized_columns:
                            row['Preconditions'] = value
                        elif any(x in orig_col.lower() for x in ['result', 'expect']) and 'Expected Final Result' in standardized_columns:
                            row['Expected Final Result'] = value
                        elif any(x in orig_col.lower() for x in ['prior', 'severity']) and 'Severity/Priority' in standardized_columns:
                            row['Severity/Priority'] = value
                    
                    # If Test ID is empty, generate one from component name
                    if not row['Test ID']:
                        component_name = tc.get('Component', 'TC')
                        component_abbr = ''.join(c for c in component_name if c.isupper() or c.isdigit())
                        if not component_abbr:
                            component_abbr = ''.join(w[0] for w in component_name.split() if w)
                        if not component_abbr:
                            component_abbr = 'TC'
                        row['Test ID'] = f"{component_abbr}-{all_test_cases.index(tc) + 1:03d}"
                    
                    writer.writerow(row)
            
            print(f"✅ Extracted {len(all_test_cases)} test cases to {csv_path}")
            return {
                "csv_path": csv_path,
                "test_case_count": len(all_test_cases),
                "message": f"Successfully extracted {len(all_test_cases)} test cases from {len(test_case_sections)} sections."
            }
        else:
            # Create a placeholder CSV if no test cases were found
            with open(csv_path, 'w', newline='', encoding='utf-8') as csvfile:
                writer = csv.writer(csvfile)
                writer.writerow(standardized_columns)
                writer.writerow(['1', 'TC-DEFAULT', 'No test cases were found in the documentation', 
                                'Check the documentation for more information', 
                                'N/A', 'Low'])
            
            print(f"⚠️ No test cases extracted. Created placeholder file at {csv_path}")
            return {
                "csv_path": csv_path,
                "test_case_count": 0,
                "message": "No test cases found in the QA document. Created a placeholder CSV file."
            }
    
    def post(self, shared, prep_res, exec_res):
        shared["csv_path"] = exec_res["csv_path"]
        shared["test_case_count"] = exec_res["test_case_count"]
        print(exec_res["message"])
        return "default"

class ExtractStoredProcedures(Node):
    """Node to extract SQL stored procedures from the codebase."""
    
    def __init__(self, max_retries=3, wait=10):
        # Add more retries with wait time for robust LLM processing
        super().__init__(max_retries=max_retries, wait=wait)
    
    def prep(self, shared):
        files_data = shared["files"]
        
        # Filter for SQL files containing stored procedures
        sql_file_indices = []
        for i, (path, content) in enumerate(files_data):
            # Check if it's a SQL file or might contain stored procedures
            if path.lower().endswith('.sql') or 'proc' in path.lower() or 'procedure' in path.lower() or 'sp_' in path.lower():
                sql_file_indices.append(i)
        
        # Create context of all potential SQL files
        sql_files_context = {}
        for idx in sql_file_indices:
            path, content = files_data[idx]
            sql_files_context[f"{idx} # {path}"] = content
            
        return sql_files_context, files_data, sql_file_indices
    
    def exec(self, prep_res):
        sql_files_context, files_data, sql_file_indices = prep_res
        
        if not sql_files_context:
            return {"stored_procedures": [], "message": "No SQL stored procedure files found in the codebase."}
        
        # For each SQL file, extract stored procedures
        stored_procedures = []
        file_to_procs = {}  # Track procedures per file
        
        for file_key, content in sql_files_context.items():
            idx = int(file_key.split('#')[0].strip())
            path = file_key.split('#')[1].strip()
            
            # Get both the base filename and original path
            filename = os.path.basename(path)
            file_basename = os.path.splitext(filename)[0]  # Just the name without extension
            
            print(f"Processing SQL file: {path} (basename: {file_basename})")
            
            # Extract stored procedures using LLM - with improved structure
            prompt = f"""
Analyze the following SQL file that contains stored procedures:

```sql
{content}
```

Extract all stored procedures from this file. For each stored procedure:
1. Identify the name of the procedure
2. Extract the complete procedure code
3. Analyze what business logic it implements
4. Identify parameters and return values
5. Identify any tables it interacts with
6. Identify the business processes it supports

Format your output as a YAML list:

```yaml
- name: "ProcedureName"
  code: |
    CREATE PROCEDURE ProcedureName ...
    ...
  business_logic: "This procedure handles..."
  parameters:
    - name: "param1"
      type: "int"
      purpose: "Identifies the customer"
  tables:
    - name: "Customers"
      operation: "SELECT/UPDATE/INSERT/DELETE"
  business_process: "Customer management"
```

Only include actual stored procedures (e.g., CREATE PROCEDURE, CREATE PROC) from the file.
Make sure to format your YAML properly - use spaces instead of tabs for indentation.
Ensure all multi-line values use proper YAML block syntax with the pipe character '|' followed by indented text.
"""
            try:
                response = call_llm(prompt)
                
                # Extract YAML from the response
                if "```yaml" in response:
                    yaml_content = response.split("```yaml")[1].split("```")[0].strip()
                elif "```" in response:
                    yaml_content = response.split("```")[1].split("```")[0].strip()
                else:
                    yaml_content = response
                
                # Replace tabs with spaces to avoid YAML parsing errors
                yaml_content = yaml_content.replace("\t", "  ")
                
                # Make a more robust attempt to parse YAML
                try:
                    procs_in_file = yaml.safe_load(yaml_content)
                except yaml.YAMLError as e:
                    print(f"YAML parsing error for {path}: {e}")
                    # Try a fallback approach: extract procedure data manually
                    procs_in_file = self._extract_procedures_fallback(yaml_content, file_basename)
                
                # Verify and clean up the data
                if isinstance(procs_in_file, list):
                    file_procs = []  # Procedures in this file
                    for proc in procs_in_file:
                        if isinstance(proc, dict) and "name" in proc:
                            # Ensure business_logic exists
                            if "business_logic" not in proc or not proc["business_logic"]:
                                proc["business_logic"] = f"Procedure {proc['name']} from {file_basename}"
                                
                            proc["file_path"] = path
                            proc["file_index"] = idx
                            proc["file_basename"] = file_basename  # Just the filename without extension
                            stored_procedures.append(proc)
                            file_procs.append(proc)
                    
                    if file_procs:
                        # Use the original file basename for the mapping key
                        file_to_procs[file_basename] = file_procs
                        print(f"Found {len(file_procs)} procedures in {file_basename}")
                elif isinstance(procs_in_file, dict) and "name" in procs_in_file:
                    # Handle case where the LLM returned a single procedure as a dict instead of a list
                    if "business_logic" not in procs_in_file or not procs_in_file["business_logic"]:
                        procs_in_file["business_logic"] = f"Procedure {procs_in_file['name']} from {file_basename}"
                        
                    procs_in_file["file_path"] = path
                    procs_in_file["file_index"] = idx
                    procs_in_file["file_basename"] = file_basename
                    stored_procedures.append(procs_in_file)
                    file_to_procs[file_basename] = [procs_in_file]
                    print(f"Found 1 procedure in {file_basename}")
            except Exception as e:
                print(f"Error processing file {path}: {e}")
                # Try direct SQL parsing as a fallback
                try:
                    extracted_procs = self._extract_procedures_sql(content, path, idx, file_basename)
                    if extracted_procs:
                        stored_procedures.extend(extracted_procs)
                        file_to_procs[file_basename] = extracted_procs
                        print(f"Found {len(extracted_procs)} procedures in {file_basename} using SQL parsing")
                except Exception as fallback_err:
                    print(f"Fallback extraction failed for {path}: {fallback_err}")
        
        return {
            "stored_procedures": stored_procedures,
            "count": len(stored_procedures),
            "file_to_procs": file_to_procs,  # Map of filename to procedures
            "message": f"Successfully extracted {len(stored_procedures)} stored procedures from {len(sql_files_context)} SQL files."
        }
    
    def _extract_procedures_fallback(self, yaml_content, file_basename):
        """Attempt to parse procedure data from malformed YAML"""
        procedures = []
        
        # Look for procedure entries that start with "- name:"
        procedure_blocks = yaml_content.split("- name:")
        
        for i, block in enumerate(procedure_blocks):
            if i == 0:  # Skip the first split which is before the first "- name:"
                continue
                
            try:
                # Extract the name
                name_line = block.split("\n")[0].strip()
                name = name_line.strip('"\'')
                
                # Create a minimal procedure object
                proc = {
                    "name": name,
                    "business_logic": f"Procedure extracted from {file_basename}",
                    "parameters": [],
                    "tables": [],
                    "business_process": "Unknown"
                }
                
                # Try to extract code if it exists
                if "code: |" in block:
                    code_section = block.split("code: |")[1].split("business_logic:")[0]
                    proc["code"] = code_section.strip()
                
                # Try to extract business logic if it exists
                if "business_logic:" in block:
                    logic_line = block.split("business_logic:")[1].split("\n")[0]
                    proc["business_logic"] = logic_line.strip('"\'')
                
                procedures.append(proc)
            except Exception as e:
                print(f"Error parsing procedure block: {e}")
        
        return procedures
    
    def _extract_procedures_sql(self, sql_content, path, idx, file_basename):
        """Direct SQL parsing fallback method to extract procedure metadata"""
        procedures = []
        
        # Simple regex to find CREATE PROCEDURE statements
        procedure_matches = re.finditer(r'CREATE\s+(?:PROC|PROCEDURE)\s+(\w+)', sql_content, re.IGNORECASE)
        
        for match in procedure_matches:
            proc_name = match.group(1)
            # Get procedure code - from CREATE PROCEDURE until the next procedure or end of file
            start_pos = match.start()
            
            # Find where this procedure ends
            next_proc = re.search(r'CREATE\s+(?:PROC|PROCEDURE)', sql_content[start_pos+10:], re.IGNORECASE)
            if next_proc:
                end_pos = start_pos + 10 + next_proc.start()
                code = sql_content[start_pos:end_pos]
            else:
                code = sql_content[start_pos:]
            
            # Find table operations
            tables = []
            table_ops = re.finditer(r'(FROM|JOIN|UPDATE|INSERT\s+INTO|DELETE\s+FROM)\s+(\w+)', code, re.IGNORECASE)
            for t_match in table_ops:
                op = t_match.group(1).upper()
                table = t_match.group(2)
                if op == "FROM" or op == "JOIN":
                    op = "SELECT"
                elif op == "INSERT INTO":
                    op = "INSERT"
                tables.append({"name": table, "operation": op})
            
            # Create procedure object
            proc = {
                "name": proc_name,
                "code": code,
                "business_logic": f"SQL procedure {proc_name} in {file_basename}",
                "parameters": [],  # Would need more complex parsing to extract parameters
                "tables": tables,
                "business_process": "Database Operations", 
                "file_path": path,
                "file_index": idx,
                "file_basename": file_basename
            }
            
            procedures.append(proc)
        
        return procedures
    
    def post(self, shared, prep_res, exec_res):
        shared["stored_procedures"] = exec_res["stored_procedures"]
        shared["file_to_procs"] = exec_res.get("file_to_procs", {})  # Store the file-to-procs mapping
        print(exec_res["message"])
        return "default"

class AnalyzeBusinessLogic(Node):
    """Node to analyze business logic from the extracted stored procedures."""
    
    def prep(self, shared):
        stored_procedures = shared.get("stored_procedures", [])
        file_to_procs = shared.get("file_to_procs", {})
        project_name = shared.get("project_name", "Unknown Project")
        
        return stored_procedures, file_to_procs, project_name
    
    def exec(self, prep_res):
        # Make the extraction of tuple values more robust
        if isinstance(prep_res, tuple) and len(prep_res) >= 3:
            stored_procedures, file_to_procs, project_name = prep_res
        elif isinstance(prep_res, tuple) and len(prep_res) == 2:
            # If we only have 2 values, use defaults for the missing one
            stored_procedures, file_to_procs = prep_res
            project_name = "Unknown Project"
        else:
            # Fallback to handle unexpected input structure
            stored_procedures = prep_res[0] if isinstance(prep_res, tuple) and len(prep_res) > 0 else []
            file_to_procs = {}
            project_name = "Unknown Project"
        
        if not stored_procedures:
            return {"message": "No stored procedures found to analyze.", "business_logic": {}}
        
        # Group procedures by business process
        business_processes = {}
        for proc in stored_procedures:
            process = proc.get("business_process", "Other")
            if process not in business_processes:
                business_processes[process] = []
            business_processes[process].append(proc)
        
        # Create file-specific business logic analyses
        file_business_logic = {}
        
        # Analyze overall business logic for the entire application
        overall_prompt = f"""
For the project '{project_name}', I have analyzed these stored procedures grouped by business process:

{json.dumps(business_processes, indent=2)}

Based on these stored procedures, create a comprehensive analysis of the business logic of the application. Include:

1. A high-level overview of the application's purpose
2. Core business domains and their relationships
3. Key business processes implemented in the database
4. Business rules enforced through stored procedures
5. Data flow through the application
6. Business entities and their relationships

Format your response as markdown with clear sections and headings.
"""
        
        overall_business_logic_analysis = call_llm(overall_prompt)
        
        # For each file, create a specific analysis
        for filename, file_procedures in file_to_procs.items():
            # Group procedures in this file by business process
            file_business_processes = {}
            for proc in file_procedures:
                process = proc.get("business_process", "Other")
                if process not in file_business_processes:
                    file_business_processes[process] = []
                file_business_processes[process].append(proc)
            
            # Create file-specific prompt
            file_prompt = f"""
For the file '{filename}' in project '{project_name}', I have analyzed these stored procedures grouped by business process:

{json.dumps(file_business_processes, indent=2)}

Based on these stored procedures, create a focused analysis of the business logic implemented in this specific file. Include:

1. A high-level overview of what this file's procedures handle
2. Business domains these procedures belong to
3. Key business processes implemented by these procedures
4. Business rules enforced by these procedures
5. Data flow through these procedures
6. Business entities and their relationships

Format your response as markdown with clear sections and headings.
"""
            
            file_business_logic_analysis = call_llm(file_prompt)
            
            # Store the file-specific analysis
            file_business_logic[filename] = {
                "overview": file_business_logic_analysis,
                "business_processes": file_business_processes,
                "stored_procedures_count": len(file_procedures)
            }
        
        # Create a structured business logic document
        business_logic = {
            "project_name": project_name,
            "overview": overall_business_logic_analysis,
            "business_processes": business_processes,
            "stored_procedures_count": len(stored_procedures),
            "file_business_logic": file_business_logic
        }
        
        return {
            "business_logic": business_logic,
            "message": f"Successfully analyzed business logic for {len(stored_procedures)} stored procedures across {len(business_processes)} business processes in {len(file_to_procs)} files."
        }
    
    def post(self, shared, prep_res, exec_res):
        shared["business_logic"] = exec_res["business_logic"]
        print(exec_res["message"])
        return "default"

class GenerateBusinessLogicDocument(Node):
    """Node to generate a business logic document from the analysis."""
    
    def prep(self, shared):
        business_logic = shared.get("business_logic", {})
        output_dir = shared.get("output_dir", "qa_docs")
        project_name = shared.get("project_name", "Unknown Project")
        base_name = shared.get("base_name", "")
        
        # If base_name is available, use it to create a folder
        if base_name:
            output_dir = os.path.join(output_dir, base_name)
        
        return business_logic, output_dir, project_name
    
    def exec(self, prep_res):
        # Make the extraction of tuple values more robust
        if isinstance(prep_res, tuple) and len(prep_res) >= 3:
            business_logic, output_dir, project_name = prep_res
        elif isinstance(prep_res, tuple) and len(prep_res) == 2:
            # If we only have 2 values, use defaults for the missing one
            business_logic, output_dir = prep_res
            project_name = "Unknown Project"
        else:
            # Fallback to handle unexpected input structure
            business_logic = prep_res[0] if isinstance(prep_res, tuple) and len(prep_res) > 0 else {}
            output_dir = "qa_docs"
            project_name = "Unknown Project"
        
        # Create the output directory if it doesn't exist
        os.makedirs(output_dir, exist_ok=True)
        
        if not business_logic:
            # Generate a default document when no procedures were found
            default_path = os.path.join(output_dir, "Business_Logic_Overview.md")
            with open(default_path, 'w', encoding='utf-8') as f:
                f.write(f"# Business Logic Overview for {project_name}\n\n")
                f.write("## Executive Summary\n\n")
                f.write("No SQL stored procedures were found or successfully analyzed in this codebase.\n\n")
                f.write("This could be due to one of the following reasons:\n\n")
                f.write("1. The codebase does not contain SQL stored procedures\n")
                f.write("2. The SQL files present use a syntax that could not be parsed\n")
                f.write("3. The stored procedures may be defined in a different format or location\n\n")
                f.write("## Recommendations\n\n")
                f.write("Consider the following approaches to documentation:\n\n")
                f.write("1. If the application uses an ORM (Object-Relational Mapping) instead of stored procedures, focus on documenting the data access layer in the code\n")
                f.write("2. If stored procedures exist but weren't detected, ensure they follow standard SQL syntax and are located in .sql files\n")
                f.write("3. Check for other database objects like functions, triggers, or views that may contain business logic\n")
            
            return {"message": "Generated a default business logic document as no procedures were found.", 
                    "file_path": default_path}
        
        # Generate document for each file that has stored procedures
        file_business_logic = business_logic.get("file_business_logic", {})
        
        print(f"Files with business logic: {list(file_business_logic.keys())}")
        
        file_paths = []
        
        # If we have file-specific analyses, generate a document for each file
        if file_business_logic:
            for filename, file_data in file_business_logic.items():
                # Create a safe filename for the output document
                # Use only the base filename without path or extension
                basename = os.path.basename(filename)
                safe_filename = re.sub(r'[^\w\-_]', '_', basename)
                output_filename = f"{safe_filename}_Business_Logic.md"
                file_path = os.path.join(output_dir, output_filename)
                
                print(f"Generating document for {filename} at {file_path}")
                
                file_paths.append((filename, file_path))
                
                # Generate test cases for this file's business processes
                test_cases_by_process = {}
                for process_name, procedures in file_data.get("business_processes", {}).items():
                    proc_descriptions = []
                    for proc in procedures:
                        proc_name = proc.get('name', 'Unnamed Procedure')
                        proc_logic = proc.get('business_logic', 'No business logic description available.')
                        tables_info = []
                        if "tables" in proc and proc["tables"]:
                            for table in proc["tables"]:
                                tables_info.append(f"{table.get('name', 'Unknown')} ({table.get('operation', 'Unknown')})")
                        
                        proc_descriptions.append(f"- **{proc_name}**: {proc_logic}\n  Tables: {', '.join(tables_info) if tables_info else 'None'}")
                    
                    proc_descriptions_str = "\n".join(proc_descriptions)
                    
                    # Generate test cases for this business process
                    test_cases_prompt = f"""
For the business process '{process_name}' in the file '{filename}' of project '{project_name}', create comprehensive test cases based on the following stored procedures:

{proc_descriptions_str}

Generate 3-5 detailed test cases that validate the business logic. Each test case should include:
1. A descriptive test case ID (e.g., "{process_name.replace(' ', '')}_TC001")
2. Test case description
3. Preconditions
4. Test steps with expected results
5. Expected final result
6. Priority (High/Medium/Low)

DO NOT include any code or technical implementation details. Focus only on business logic validation.

Format your response as YAML:

```yaml
test_cases:
  - id: "TestCaseID001"
    description: "Verify that..."
    preconditions: "Customer exists and is active..."
    steps:
      - step: "Perform action X"
        expected: "System responds with Y"
      - step: "Check condition Z"
        expected: "Value should be W"
    final_result: "The order is successfully created with status 'New'"
    priority: "High"
```
"""
                    try:
                        response = call_llm(test_cases_prompt)
                        
                        # Extract YAML from the response
                        if "```yaml" in response:
                            yaml_content = response.split("```yaml")[1].split("```")[0].strip()
                        elif "```" in response:
                            yaml_content = response.split("```")[1].split("```")[0].strip()
                        else:
                            yaml_content = response
                        
                        # Replace tabs with spaces to avoid YAML parsing errors
                        yaml_content = yaml_content.replace("\t", "  ")
                        
                        # Parse the YAML
                        try:
                            test_cases_data = yaml.safe_load(yaml_content)
                            if isinstance(test_cases_data, dict) and "test_cases" in test_cases_data:
                                test_cases_by_process[process_name] = test_cases_data["test_cases"]
                            else:
                                test_cases_by_process[process_name] = []
                        except yaml.YAMLError as e:
                            print(f"YAML parsing error for test cases in {process_name}: {e}")
                            test_cases_by_process[process_name] = []
                    except Exception as e:
                        print(f"Error generating test cases for {process_name} in {filename}: {e}")
                        test_cases_by_process[process_name] = []
                
                # Write the document for this file
                with open(file_path, 'w', encoding='utf-8') as f:
                    # Document header
                    f.write(f"# {basename} Business Logic Analysis\n\n")
                    
                    # Table of Contents
                    f.write("## Table of Contents\n\n")
                    f.write("1. [Executive Summary](#executive-summary)\n")
                    f.write("2. [Business Domains and Relationships](#business-domains-and-relationships)\n")
                    f.write("3. [Business Processes](#business-processes)\n")
                    business_proc_count = 1
                    for process_name in file_data.get("business_processes", {}).keys():
                        safe_link = process_name.lower().replace(' ', '-').replace('/', '-')
                        f.write(f"   {business_proc_count}. [{process_name}](#{safe_link})\n")
                        business_proc_count += 1
                    f.write("4. [Business Rules](#business-rules)\n")
                    f.write("5. [Data Flow](#data-flow)\n")
                    f.write("6. [Business Entities](#business-entities)\n")
                    f.write("7. [Test Cases](#test-cases)\n")
                    test_case_count = 1
                    for process_name in file_data.get("business_processes", {}).keys():
                        if process_name in test_cases_by_process and test_cases_by_process[process_name]:
                            safe_link = f"test-cases-{process_name.lower().replace(' ', '-').replace('/', '-')}"
                            f.write(f"   {test_case_count}. [{process_name} Test Cases](#{safe_link})\n")
                            test_case_count += 1
                    
                    # Executive Summary (overview)
                    f.write("\n## Executive Summary\n\n")
                    f.write(file_data.get("overview", "No overview available for this file."))
                    f.write("\n\n")
                    
                    # Extract sections from the overview
                    overview_text = file_data.get("overview", "")
                    
                    # Domains Section
                    f.write("## Business Domains and Relationships\n\n")
                    if "business domain" in overview_text.lower():
                        pattern = r"(?i)(?:business domain|domain).*?(?:\n##|\Z)"
                        matches = re.search(pattern, overview_text, re.DOTALL)
                        if matches:
                            domain_text = matches.group(0)
                            domain_text = re.sub(r"(?i)(?:business domain|domain)[^\n]*\n", "", domain_text)
                            domain_text = re.sub(r"\n##.*\Z", "", domain_text)
                            f.write(domain_text.strip())
                        else:
                            f.write("*Business domains information extracted from the analysis*\n\n")
                    else:
                        f.write("*Business domains information extracted from the analysis*\n\n")
                    f.write("\n\n")
                    
                    # Business Processes section
                    f.write("## Business Processes\n\n")
                    f.write(f"This section details the key business processes implemented in {filename}.\n\n")
                    
                    for process_name, procedures in file_data.get("business_processes", {}).items():
                        safe_link = process_name.lower().replace(' ', '-').replace('/', '-')
                        f.write(f"### {process_name}\n\n")
                        
                        # Process description
                        f.write("#### Process Overview\n\n")
                        f.write(f"*{process_name}* process handles the following business functions:\n\n")
                        
                        # List procedures in this process
                        for proc in procedures:
                            proc_name = proc.get('name', 'Unnamed Procedure')
                            proc_logic = proc.get('business_logic', 'No business logic description available.')
                            f.write(f"- **{proc_name}**: {proc_logic}\n\n")
                        
                        # Tables affected by this process
                        f.write("#### Database Entities Involved\n\n")
                        all_tables = set()
                        for proc in procedures:
                            if "tables" in proc and proc["tables"]:
                                for table in proc["tables"]:
                                    table_name = table.get('name', 'N/A')
                                    table_op = table.get('operation', 'N/A')
                                    all_tables.add(f"{table_name} ({table_op})")
                        
                        if all_tables:
                            f.write("This process interacts with the following database entities:\n\n")
                            for table in sorted(all_tables):
                                f.write(f"- {table}\n")
                        else:
                            f.write("No specific database entities identified for this process.\n")
                        f.write("\n")
                        
                        # Parameters for this process
                        f.write("#### Process Inputs\n\n")
                        all_params = []
                        for proc in procedures:
                            if "parameters" in proc and proc["parameters"]:
                                for param in proc["parameters"]:
                                    param_name = param.get('name', 'N/A')
                                    param_type = param.get('type', 'N/A')
                                    param_purpose = param.get('purpose', 'N/A')
                                    all_params.append((proc.get('name', 'Unnamed'), param_name, param_type, param_purpose))
                        
                        if all_params:
                            f.write("The process accepts the following inputs:\n\n")
                            f.write("| Procedure | Parameter | Type | Purpose |\n")
                            f.write("|-----------|-----------|------|--------|\n")
                            for proc_name, param_name, param_type, param_purpose in all_params:
                                f.write(f"| {proc_name} | {param_name} | {param_type} | {param_purpose} |\n")
                        else:
                            f.write("No specific inputs identified for this process.\n")
                        f.write("\n")
                        
                        f.write("---\n\n")
                    
                    # Business Rules section
                    f.write("## Business Rules\n\n")
                    if "business rule" in overview_text.lower():
                        pattern = r"(?i)(?:business rule).*?(?:\n##|\Z)"
                        matches = re.search(pattern, overview_text, re.DOTALL)
                        if matches:
                            rules_text = matches.group(0)
                            rules_text = re.sub(r"(?i)(?:business rule)[^\n]*\n", "", rules_text)
                            rules_text = re.sub(r"\n##.*\Z", "", rules_text)
                            f.write(rules_text.strip())
                        else:
                            f.write("*Business rules information extracted from the analysis*\n\n")
                    else:
                        f.write("*Business rules information extracted from the analysis*\n\n")
                    f.write("\n\n")
                    
                    # Data Flow section
                    f.write("## Data Flow\n\n")
                    if "data flow" in overview_text.lower():
                        pattern = r"(?i)(?:data flow).*?(?:\n##|\Z)"
                        matches = re.search(pattern, overview_text, re.DOTALL)
                        if matches:
                            flow_text = matches.group(0)
                            flow_text = re.sub(r"(?i)(?:data flow)[^\n]*\n", "", flow_text)
                            flow_text = re.sub(r"\n##.*\Z", "", flow_text)
                            f.write(flow_text.strip())
                        else:
                            f.write("*Data flow information extracted from the analysis*\n\n")
                    else:
                        f.write("*Data flow information extracted from the analysis*\n\n")
                    f.write("\n\n")
                    
                    # Business Entities section
                    f.write("## Business Entities\n\n")
                    if "business entit" in overview_text.lower():
                        pattern = r"(?i)(?:business entit).*?(?:\n##|\Z)"
                        matches = re.search(pattern, overview_text, re.DOTALL)
                        if matches:
                            entities_text = matches.group(0)
                            entities_text = re.sub(r"(?i)(?:business entit)[^\n]*\n", "", entities_text)
                            entities_text = re.sub(r"\n##.*\Z", "", entities_text)
                            f.write(entities_text.strip())
                        else:
                            f.write("*Business entities information extracted from the analysis*\n\n")
                    else:
                        f.write("*Business entities information extracted from the analysis*\n\n")
                    f.write("\n\n")
                    
                    # Test Cases section
                    f.write("## Test Cases\n\n")
                    f.write(f"The following test cases validate the business logic implemented in {filename}.\n\n")
                    
                    has_test_cases = False
                    for process_name, test_cases in test_cases_by_process.items():
                        if test_cases:
                            has_test_cases = True
                            safe_link = f"test-cases-{process_name.lower().replace(' ', '-').replace('/', '-')}"
                            f.write(f"### {process_name} Test Cases\n\n")
                            
                            for tc in test_cases:
                                tc_id = tc.get('id', 'Unknown')
                                tc_desc = tc.get('description', 'No description')
                                tc_priority = tc.get('priority', 'Medium')
                                
                                f.write(f"#### {tc_id}: {tc_desc}\n\n")
                                f.write(f"**Priority**: {tc_priority}\n\n")
                                
                                if 'preconditions' in tc:
                                    f.write("**Preconditions**:\n")
                                    f.write(f"{tc['preconditions']}\n\n")
                                
                                if 'steps' in tc and tc['steps']:
                                    f.write("**Test Steps**:\n\n")
                                    f.write("| Step | Expected Result |\n")
                                    f.write("|------|----------------|\n")
                                    for i, step_info in enumerate(tc['steps'], 1):
                                        step_desc = step_info.get('step', 'Unknown step')
                                        step_expected = step_info.get('expected', 'Unknown expected result')
                                        f.write(f"| {i}. {step_desc} | {step_expected} |\n")
                                    f.write("\n")
                                
                                if 'final_result' in tc:
                                    f.write("**Expected Final Result**:\n")
                                    f.write(f"{tc['final_result']}\n\n")
                                
                                f.write("---\n\n")
                    
                    if not has_test_cases:
                        f.write("No test cases were generated for the analyzed business processes.\n\n")
            
        # If we have file paths, convert to a list for return
        if file_paths:
            result_file_paths = [path for _, path in file_paths]
            return {
                "message": f"Successfully generated {len(result_file_paths)} business logic documents.",
                "file_path": result_file_paths[0] if len(result_file_paths) == 1 else None,
                "file_paths": result_file_paths
            }
        else:
            # If no specific file documents were generated but we have business logic,
            # generate an overall summary document
            output_filename = "Project_Business_Logic.md"
            file_path = os.path.join(output_dir, output_filename)
            
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(f"# {project_name} Business Logic Overview\n\n")
                f.write("## Executive Summary\n\n")
                f.write(business_logic.get("overview", "No business logic overview available."))
                f.write("\n\n## Business Processes\n\n")
                
                business_processes = business_logic.get("business_processes", {})
                if business_processes:
                    for process_name, procedures in business_processes.items():
                        f.write(f"### {process_name}\n\n")
                        for proc in procedures:
                            f.write(f"- **{proc.get('name', 'Unnamed')}**: {proc.get('business_logic', 'No description')}\n")
                        f.write("\n")
                else:
                    f.write("No specific business processes identified.\n\n")
                    
                f.write("\n## Additional Information\n\n")
                f.write("This document provides a high-level overview of the business logic extracted from the analyzed codebase. ")
                f.write("For more detailed information, please refer to the individual SQL files in the codebase.\n")
            
            return {
                "message": "Generated project-level business logic document.",
                "file_path": file_path,
                "file_paths": [file_path]
            }    
    def post(self, shared, prep_res, exec_res):
        # Store the generated document path(s) in the shared store
        if exec_res.get("file_paths"):
            shared["business_logic_document"] = exec_res["file_paths"]
        else:
            shared["business_logic_document"] = exec_res.get("file_path")
        
        print(exec_res["message"])
        return "default"

