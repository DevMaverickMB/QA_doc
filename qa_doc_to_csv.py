#!/usr/bin/env python3
import os
import re
import csv
import argparse
import sys

def convert_qa_doc_to_csv(doc_path, output_dir=None, debug=False):
    """
    Convert test case tables from a QA documentation markdown file to a single CSV file.
    
    Args:
        doc_path (str): Path to the QA documentation markdown file
        output_dir (str, optional): Directory to save the CSV file. Defaults to a 'csv_tables'
                                   subdirectory in the same location as the markdown file.
        debug (bool): Enable debug output
    
    Returns:
        dict: Information about the extracted tables and generated CSV file
    """
    if not os.path.exists(doc_path):
        print(f"Error: Documentation file not found at {doc_path}")
        return {}
    
    # Set default output directory if not provided
    if not output_dir:
        doc_dir = os.path.dirname(doc_path)
        output_dir = os.path.join(doc_dir, "csv_tables")
    
    # Create output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)
    
    # Get the base name of the input file (without extension)
    doc_basename = os.path.basename(doc_path)
    base_name = os.path.splitext(doc_basename)[0]
    
    # Read the markdown file
    with open(doc_path, "r", encoding="utf-8") as f:
        content = f.read()
    
    if debug:
        print(f"DEBUG: Read {len(content)} bytes from {doc_path}")
    
    # Try multiple patterns to find test case sections
    test_case_patterns = [
        r'### \d+\.\d+\. Test Cases: ([^\n]+)',  # Original pattern
        r'### Test Cases: ([^\n]+)',             # Simpler section
        r'## Test Cases[:\s]*([^\n]+)',          # Level 2 heading
        r'# Test Cases[:\s]*([^\n]+)',           # Level 1 heading
    ]
    
    # Also look for any markdown tables directly
    all_tables = re.findall(r'(\|[^\n]+\|(?:\n\|[^\n]+\|)+)', content)
    
    if debug:
        print(f"DEBUG: Found {len(all_tables)} total markdown tables in document")
        for pattern in test_case_patterns:
            matches = re.findall(pattern, content)
            print(f"DEBUG: Pattern '{pattern}' found {len(matches)} matches")
    
    # Define standard columns that all test cases should have
    standard_columns = ["Component", "Test ID", "Preconditions", "Steps to Execute", 
                        "Expected Result @ Each Step", "Expected Final Result", "Severity/Priority"]
    
    # Collect all test cases from all tables
    all_test_cases = []
    test_case_sections = []
    
    # Try each pattern to find test case sections
    for pattern in test_case_patterns:
        section_matches = list(re.finditer(pattern, content, re.MULTILINE))
        
        if debug:
            print(f"DEBUG: Trying pattern '{pattern}' - found {len(section_matches)} matches")
        
        if not section_matches:
            continue
            
        # Process each matching section
        for i, section_match in enumerate(section_matches):
            section_title = section_match.group(1).strip()
            section_start_pos = section_match.end()
            
            # Get end position (next section or end of file)
            if i < len(section_matches) - 1:
                section_end_pos = section_matches[i+1].start()
            else:
                section_end_pos = len(content)
            
            # Find any table in this section
            section_content = content[section_start_pos:section_end_pos]
            table_match = re.search(r'(\|[^\n]+\|(?:\n\|[^\n]+\|)+)', section_content)
            
            if not table_match:
                if debug:
                    print(f"DEBUG: No table found in section '{section_title}'")
                continue
                
            table_content = table_match.group(1)
            
            # Process the markdown table
            table_rows = []
            for line in table_content.split('\n'):
                line = line.strip()
                if line and line.startswith('|') and line.endswith('|'):
                    table_rows.append(line)
            
            if len(table_rows) < 3:  # Need at least header, separator, and one data row
                if debug:
                    print(f"DEBUG: Table for '{section_title}' has too few rows")
                continue
                
            # Extract headers (first row)
            header_row = table_rows[0]
            header_cells = [cell.strip() for cell in header_row.split('|')[1:-1]]
            
            if debug:
                print(f"DEBUG: Found table with {len(table_rows)} rows and {len(header_cells)} columns for '{section_title}'")
                print(f"DEBUG: Headers: {header_cells}")
            
            # Process data rows (row 2 onwards)
            section_rows = 0
            for row in table_rows[2:]:  # Skip header and separator
                cells = [cell.strip() for cell in row.split('|')[1:-1]]
                
                # Only add row if it has the same number of cells as headers
                if len(cells) == len(header_cells):
                    section_rows += 1
                    # Create a dictionary with header cells as keys
                    row_data = {header_cells[i]: cells[i] for i in range(len(header_cells))}
                    
                    # Add the component name
                    row_data["Component"] = section_title
                    
                    all_test_cases.append(row_data)
            
            test_case_sections.append({
                "component": section_title,
                "rows": section_rows
            })
        
        # If we found any valid sections with this pattern, stop trying others
        if test_case_sections:
            break
    
    # If still no sections found, try extracting tables directly
    if not test_case_sections and all_tables:
        if debug:
            print("DEBUG: No sections matched patterns, trying direct table extraction")
            
        for i, table_content in enumerate(all_tables):
            table_rows = []
            for line in table_content.split('\n'):
                line = line.strip()
                if line and line.startswith('|') and line.endswith('|'):
                    table_rows.append(line)
            
            if len(table_rows) < 3:  # Need at least header, separator, and one data row
                continue
                
            # Extract headers (first row)
            header_row = table_rows[0]
            header_cells = [cell.strip() for cell in header_row.split('|')[1:-1]]
            
            # Check if this looks like a test case table (has common test case headers)
            test_headers = ['test', 'case', 'step', 'expect', 'precond', 'sever', 'prior']
            is_test_table = any(any(test_h in cell.lower() for test_h in test_headers) for cell in header_cells)
            
            if not is_test_table:
                continue
                
            section_title = f"Table {i+1}"
            
            if debug:
                print(f"DEBUG: Found possible test table {i+1} with {len(table_rows)} rows")
                print(f"DEBUG: Headers: {header_cells}")
            
            # Process data rows
            section_rows = 0
            for row in table_rows[2:]:  # Skip header and separator
                cells = [cell.strip() for cell in row.split('|')[1:-1]]
                
                # Only add row if it has the same number of cells as headers
                if len(cells) == len(header_cells):
                    section_rows += 1
                    # Create a dictionary with header cells as keys
                    row_data = {header_cells[i]: cells[i] for i in range(len(header_cells))}
                    
                    # Add the component name
                    row_data["Component"] = section_title
                    
                    all_test_cases.append(row_data)
            
            test_case_sections.append({
                "component": section_title,
                "rows": section_rows
            })
    
    # Create a single CSV file with all test cases
    if all_test_cases:
        # Get all columns from the data
        all_columns = set(["Component"])
        for test_case in all_test_cases:
            all_columns.update(test_case.keys())
            
        # Create final column list
        columns = []
        # First add standard columns if they exist in our data
        for col in standard_columns:
            if any(col in test_case for test_case in all_test_cases):
                columns.append(col)
        
        # Then add any remaining columns
        for col in sorted(all_columns):
            if col not in columns:
                columns.append(col)
                
        if debug:
            print(f"DEBUG: CSV will have {len(columns)} columns: {columns}")
        
        # Use input filename for the generated CSV file
        csv_filename = f"{base_name}_test_cases.csv"
        csv_path = os.path.join(output_dir, csv_filename)
        
        with open(csv_path, 'w', newline='', encoding='utf-8') as csv_file:
            writer = csv.DictWriter(csv_file, fieldnames=columns)
            writer.writeheader()
            
            for row_data in all_test_cases:
                # Create a new row with standard columns, using empty strings for missing values
                standardized_row = {col: row_data.get(col, "") for col in columns}
                writer.writerow(standardized_row)
        
        # Create README.md in the output directory
        create_readme(output_dir, test_case_sections, doc_basename, csv_filename)
        
        return {
            "csv_path": csv_path,
            "test_case_sections": test_case_sections,
            "total_test_cases": len(all_test_cases),
            "base_name": base_name
        }
    
    return {}

def create_readme(output_dir, test_case_sections, source_filename, csv_filename):
    """
    Create a README.md file in the output directory with instructions on using the CSV file.
    
    Args:
        output_dir (str): Directory where the CSV file is saved
        test_case_sections (list): List of dictionaries with details about the extracted tables
        source_filename (str): Name of the source markdown file
        csv_filename (str): Name of the generated CSV file
    """
    total_test_cases = sum(section["rows"] for section in test_case_sections)
    
    readme_content = f"""# QA Test Cases in CSV Format

## Overview

This directory contains test cases extracted from the QA documentation file `{source_filename}` and converted to a single CSV file for easy import into test management tools.

## File

All test cases have been consolidated into a single CSV file: [{csv_filename}]({csv_filename})

## Test Case Breakdown

The CSV file contains {total_test_cases} test cases from {len(test_case_sections)} different components:

| Component | Test Cases |
|-----------|------------|
"""
    
    # Add a table row for each component
    for section in sorted(test_case_sections, key=lambda x: x["component"]):
        readme_content += f"| {section['component']} | {section['rows']} |\n"
    
    readme_content += """
## CSV File Structure

The CSV file has the following columns:
- **Component**: Identifies which component the test case belongs to
- **Test ID**: Unique identifier for the test case
- **Preconditions**: Required state before executing the test
- **Steps to Execute**: Actions to perform during the test
- **Expected Result @ Each Step**: What should happen after each action
- **Expected Final Result**: Overall outcome when test completes
- **Severity/Priority**: Importance level of the test case

## Import Instructions

This CSV file can be imported into various test management tools:

### TestRail

1. Go to your TestRail project
2. Navigate to "Test Cases" section
3. Click "Import" or "Import Cases" (location varies by TestRail version)
4. Select "CSV Import"
5. Choose the CSV file
6. Map the CSV columns to TestRail fields:
   - "Component" → Custom field for component/section
   - "Test ID" → "Title" or "ID"
   - "Preconditions" → "Preconditions"
   - "Steps to Execute" → "Steps"
   - "Expected Result @ Each Step" → "Expected Result"
   - "Expected Final Result" → "Expected Result" or custom field
   - "Severity/Priority" → "Priority"
7. Complete the import

### JIRA/Xray

1. Go to your JIRA project
2. Navigate to "Tests" section (if using Xray)
3. Click "Import" or "Import Test Cases"
4. Select "CSV Import"
5. Choose the CSV file
6. Map the CSV columns to JIRA fields as applicable
7. Complete the import

### Other Test Management Tools

Most test management tools support CSV import. Consult your tool's documentation for specific import instructions.

## Customizing Import

If your test management tool requires a different CSV format, you can use a spreadsheet application to reformat the data.

## Source Documentation

For full context and additional details, refer to the original QA documentation file.
"""
    
    # Write the README file
    readme_path = os.path.join(output_dir, "README.md")
    with open(readme_path, 'w', encoding='utf-8') as f:
        f.write(readme_content)
    
    print(f"Created README.md with usage instructions in {output_dir}")

def main():
    parser = argparse.ArgumentParser(description="Convert QA documentation markdown tables to a single CSV file.")
    parser.add_argument("input_file", help="Path to the QA documentation markdown file")
    parser.add_argument("-o", "--output", help="Directory to save the CSV file (default: ./csv_tables)")
    parser.add_argument("-d", "--debug", action="store_true", help="Enable debug output")
    
    args = parser.parse_args()
    
    input_file = args.input_file
    output_dir = args.output
    debug = args.debug
    
    if not os.path.isfile(input_file):
        print(f"Error: Input file '{input_file}' not found or is not a file.")
        sys.exit(1)
    
    print(f"Converting test case tables from {input_file}...")
    
    result = convert_qa_doc_to_csv(input_file, output_dir, debug)
    
    if result:
        csv_path = result["csv_path"]
        output_dir = os.path.dirname(csv_path)
        base_name = result.get("base_name", os.path.splitext(os.path.basename(input_file))[0])
        
        print(f"\nTest cases extracted to: {csv_path}")
        print(f"Total test cases: {result['total_test_cases']} from {len(result['test_case_sections'])} components")
        print("\nComponent breakdown:")
        
        for section in result['test_case_sections']:
            print(f"  - {section['component']}: {section['rows']} test cases")
        
        print("\nThis CSV file can be imported into your test management tool.")
        print(f"See {output_dir}/README.md for import instructions.")
    else:
        print("No test case tables found in the documentation.")
        print("\nPossible reasons:")
        print("1. The documentation doesn't have any tables")
        print("2. The tables don't follow the expected markdown format")
        print("3. The test case sections aren't labeled in a way the script recognizes")
        print("\nTry running with --debug flag for more information")
        print("Example: python3 qa_doc_to_csv.py input.md --debug")

if __name__ == "__main__":
    main() 