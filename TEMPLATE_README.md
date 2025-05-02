# QA Documentation Templates

## Overview

The template system enables you to control the exact structure and format of the QA documentation that the AI agent generates. By providing a template file, you can ensure that all generated documentation follows your organization's standards and includes the specific sections, tables, and formatting that you require.

## How It Works

1. The AI agent loads the template file (`utils/qa_template.md` by default)
2. When generating a new QA document, the AI strictly follows the structure of the template
3. The agent preserves all headings, table formats, bullet points, and overall organization
4. Only the specific content is customized based on the analyzed codebase

## Creating Custom Templates

Your template should be a markdown file with the following:

1. **Clear structure** - Include all section headings you want in the final document
2. **Table formats** - Define the exact column headers and layout for tables
3. **Placeholders** - Use placeholders like `[Component Name]` which the AI will replace
4. **Formatting** - Include any special formatting, bullet points, or numbering schemes

## Template Examples

The default template at `utils/qa_template.md` provides a good starting point.

You can create specialized templates for different types of applications, such as:

- Web application QA documentation
- Mobile application QA documentation
- API testing documentation
- Performance testing documentation
- Accessibility testing documentation

## Testing Your Template

You can test how a template will be applied using the included test script:

```bash
python test_template.py --template path/to/your/custom_template.md
```

This will generate a test document using your template and save it to the `template_test` directory.

## Tips for Effective Templates

1. **Be specific** - The more detailed your template, the more consistent your results
2. **Include examples** - Add example content in brackets like `[Example: Button click test]`
3. **Keep it organized** - Use clear headings and a logical structure
4. **Include instructions** - Add comments or instructions in areas where you want specific content

## Using Templates in Production

To use your template for actual QA document generation:

1. Place your template at `utils/qa_template.md` (replacing the default)
2. Run the main tool as normal:
   ```bash
   python main.py --dir /path/to/your/project
   ```

The generated documentation will follow your template's structure precisely. 