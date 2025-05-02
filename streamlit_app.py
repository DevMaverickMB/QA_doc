import streamlit as st
import tempfile
import os
import base64
import uuid
import shutil
from pathlib import Path
from flow import create_component_action_flow, create_business_logic_flow, create_combined_flow
import time
import dotenv

# Load environment variables
dotenv.load_dotenv()

# Default file patterns (match with main.py)
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

# Function to get appropriate file icon
def get_file_icon(filename):
    """Return appropriate icon based on file extension"""
    ext = os.path.splitext(filename)[1].lower()
    icons = {
        '.py': '🐍',
        '.js': '📜',
        '.jsx': '⚛️',
        '.ts': '📘',
        '.tsx': '🔷',
        '.html': '🌐',
        '.css': '🎨',
        '.cs': '🔧',
        '.java': '☕',
        '.aspx': '🖥️',
        '.yml': '⚙️',
        '.yaml': '⚙️',
        '.md': '📝',
        '.txt': '📄',
    }
    return icons.get(ext, '📄')  # Default to generic file icon

# Function to read a file and return download link
def get_download_link(file_path, link_text):
    with open(file_path, "rb") as file:
        contents = file.read()
    b64 = base64.b64encode(contents).decode()
    href = f'<a href="data:application/octet-stream;base64,{b64}" download="{os.path.basename(file_path)}">{link_text}</a>'
    return href

# Replace the spinner with a more detailed loading animation
def loading_animation():
    cols = st.columns(5)
    dots = ["⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧", "⠇", "⠏"]
    status = st.empty()
    
    for i in range(40):  # Simulate iterations
        status.markdown(f"<h3 style='text-align: center; color: #4b6cb7;'>{dots[i % len(dots)]} Processing...</h3>", unsafe_allow_html=True)
        time.sleep(0.1)
    
    status.empty()

# Add a function to cache file contents in session state
def cache_file_contents(file_path, key_prefix):
    """Read a file and cache its contents in session state to prevent file access issues"""
    try:
        if not os.path.exists(file_path):
            return None
            
        with open(file_path, "rb") as f:
            contents = f.read()
            
        # Store in session state with a key based on file path
        cache_key = f"{key_prefix}_{os.path.basename(file_path)}"
        st.session_state[cache_key] = contents
        return contents
    except Exception as e:
        print(f"Error caching file {file_path}: {str(e)}")
        return None

# Function to process files and generate documentation
def process_files(files, project_name):
    """
    Process uploaded files and generate all documentation types (combined mode).
    
    Args:
        files: List of uploaded file objects
        project_name: Name of the project
    
    Returns:
        Dictionary with processing results
    """
    # Create a temporary directory for uploaded files
    temp_dir = Path(tempfile.mkdtemp())
    
    try:
        # Save uploaded files to temporary directory
        file_paths = []
        for uploaded_file in files:
            file_path = temp_dir / uploaded_file.name
            with open(file_path, "wb") as f:
                f.write(uploaded_file.getbuffer())
            file_paths.append(file_path)
        
        # Create output directory with a unique ID to avoid conflicts
        output_dir = temp_dir / f"qa_docs_{uuid.uuid4().hex[:8]}"
        os.makedirs(output_dir, exist_ok=True)
        
        # Initialize shared store
        shared = {
            "repo_url": None,
            "local_dir": str(temp_dir),
            "project_name": project_name or "Uploaded Project",  # Default name if none provided
            "github_token": None,
            "output_dir": str(output_dir),
            
            # File patterns based on uploaded files
            "include_patterns": DEFAULT_INCLUDE_PATTERNS,
            "exclude_patterns": DEFAULT_EXCLUDE_PATTERNS,
            "max_file_size": 10 * 1024 * 1024,  # 10MB max file size
            
            # These will be populated by nodes
            "files": [],
            "abstractions": [],
            "relationships": {}
        }
        
        # Create and run the combined flow (generates all documentation types)
        flow = create_combined_flow()
        flow.run(shared)
        
        # Prepare results
        result = {"success": False, "error": "Documentation was not generated properly.", "mode": "combined"}
        
        # Component action documentation outputs
        if "component_action_doc_dir" in shared and "component_action_doc_filename" in shared:
            doc_dir = shared["component_action_doc_dir"]
            doc_filename = shared["component_action_doc_filename"]
            doc_path = os.path.join(doc_dir, doc_filename)
            
            if os.path.exists(doc_path):
                result["success"] = True
                result["doc_path"] = doc_path
                result["doc_dir"] = doc_dir
                result["doc_filename"] = doc_filename
                result["temp_dir"] = str(temp_dir)
                
                # Cache the MD file contents immediately
                doc_contents = cache_file_contents(doc_path, "doc_content")
                if doc_contents:
                    result["doc_content"] = doc_contents
        
        # CSV outputs
        if "csv_path" in shared and shared["csv_path"] and os.path.exists(shared["csv_path"]):
            csv_path = shared["csv_path"]
            result["csv_path"] = csv_path
            result["success"] = True  # Mark as success if at least CSV was generated
            
            # Cache the CSV file contents
            csv_contents = cache_file_contents(csv_path, "csv_content")
            if csv_contents:
                result["csv_content"] = csv_contents
                
            # Also check for the csv_tables directory which may contain the CSV file
            csv_tables_dir = os.path.join(shared.get("component_action_doc_dir", output_dir), "csv_tables")
            if os.path.exists(csv_tables_dir):
                csv_tables_file = os.path.join(csv_tables_dir, "all_test_cases.csv")
                if os.path.exists(csv_tables_file):
                    # This is the proper CSV file, update the path
                    print(f"Found CSV file in csv_tables directory: {csv_tables_file}")
                    result["csv_path"] = csv_tables_file
                    
                    # Cache this file too
                    csv_contents = cache_file_contents(csv_tables_file, "csv_content")
                    if csv_contents:
                        result["csv_content"] = csv_contents
        
        # Business logic documentation outputs
        if "business_logic_document" in shared:
            result["success"] = True  # Mark as success if business logic doc was generated
            
            if isinstance(shared["business_logic_document"], list):
                result["business_logic_docs"] = []
                
                for doc_path in shared["business_logic_document"]:
                    if os.path.exists(doc_path):
                        doc_contents = cache_file_contents(doc_path, f"bl_doc_{os.path.basename(doc_path)}")
                        result["business_logic_docs"].append({
                            "path": doc_path,
                            "filename": os.path.basename(doc_path),
                            "content": doc_contents
                        })
            else:
                bl_doc_path = shared["business_logic_document"]
                if os.path.exists(bl_doc_path):
                    result["business_logic_doc"] = bl_doc_path
                    result["business_logic_filename"] = os.path.basename(bl_doc_path)
                    
                    # Cache the business logic doc contents
                    bl_doc_contents = cache_file_contents(bl_doc_path, "bl_doc_content")
                    if bl_doc_contents:
                        result["business_logic_content"] = bl_doc_contents
        
        # Create persistent copies of all generated files
        try:
            # Create a persistent directory in the system temp location
            persistent_dir = Path(tempfile.gettempdir()) / "qa_docs_persistent"
            os.makedirs(persistent_dir, exist_ok=True)
            
            # Copy files to persistent location
            if "doc_path" in result and os.path.exists(result["doc_path"]):
                doc_persistent_path = persistent_dir / result.get("doc_filename", os.path.basename(result["doc_path"]))
                shutil.copy2(result["doc_path"], doc_persistent_path)
                result["doc_persistent_path"] = str(doc_persistent_path)
                result["doc_path"] = str(doc_persistent_path)
            
            if "csv_path" in result and os.path.exists(result["csv_path"]):
                csv_filename = os.path.basename(result["csv_path"])
                csv_persistent_path = persistent_dir / csv_filename
                shutil.copy2(result["csv_path"], csv_persistent_path)
                result["csv_persistent_path"] = str(csv_persistent_path)
                result["csv_path"] = str(csv_persistent_path)
            
            if "business_logic_docs" in result:
                result["business_logic_persistent_paths"] = []
                for doc_info in result["business_logic_docs"]:
                    if os.path.exists(doc_info["path"]):
                        bl_persistent_path = persistent_dir / doc_info["filename"]
                        shutil.copy2(doc_info["path"], bl_persistent_path)
                        result["business_logic_persistent_paths"].append(str(bl_persistent_path))
                        doc_info["path"] = str(bl_persistent_path)
            
            elif "business_logic_doc" in result and os.path.exists(result["business_logic_doc"]):
                bl_persistent_path = persistent_dir / result["business_logic_filename"]
                shutil.copy2(result["business_logic_doc"], bl_persistent_path)
                result["business_logic_persistent_path"] = str(bl_persistent_path)
                result["business_logic_doc"] = str(bl_persistent_path)
                
        except Exception as e:
            # If persistence fails, still return the original paths
            result["persistence_error"] = str(e)
        
        return result
        
    except Exception as e:
        import traceback
        return {
            "success": False, 
            "error": str(e),
            "traceback": traceback.format_exc(),
            "mode": "combined"
        }

# Configure page with a wider layout and custom theme
st.set_page_config(
    page_title="QA Document Generator",
    page_icon="📝",
    layout="wide"
)

# Custom CSS for modern styling
st.markdown("""
<style>
    /* Main container styling */
    .main {
        background-color: #f8f9fa;
        padding: 20px;
    }
    
    /* Headers */
    h1, h2, h3 {
        font-family: 'Helvetica Neue', sans-serif;
        font-weight: 500;
        color: #2c3e50;
    }
    
    /* Main header with gradient */
    .main-header {
        text-align: center;
        background: linear-gradient(90deg, #4b6cb7 0%, #182848 100%);
        color: white !important;
        padding: 1.5rem;
        border-radius: 10px;
        margin-bottom: 2rem;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }
    
    /* Cards for content sections */
    .card {
        background-color: white;
        border-radius: 10px;
        padding: 20px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.05);
        margin-bottom: 20px;
    }
    
    /* Custom button styling */
    .stButton > button {
        background-color: #4b6cb7;
        color: white;
        border-radius: 5px;
        border: none;
        padding: 0.5rem 2rem;
        font-weight: 500;
        box-shadow: 0 2px 5px rgba(0, 0, 0, 0.1);
        transition: all 0.3s ease;
    }
    .stButton > button:hover {
        background-color: #3a539b;
        box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2);
    }
    
    /* Messages */
    .success-message {
        background-color: #d4edda;
        color: #155724;
        padding: 10px;
        border-radius: 5px;
        margin: 10px 0;
        border-left: 5px solid #28a745;
    }
    .warning-message {
        background-color: #fff3cd;
        color: #856404;
        padding: 10px;
        border-radius: 5px;
        margin: 10px 0;
        border-left: 5px solid #ffc107;
    }
    .error-message {
        background-color: #f8d7da;
        color: #721c24;
        padding: 10px;
        border-radius: 5px;
        margin: 10px 0;
        border-left: 5px solid #dc3545;
    }
    
    /* Footer styling */
    .footer {
        text-align: center;
        padding: 20px;
        color: #6c757d;
        font-size: 0.9rem;
        margin-top: 40px;
    }
    
    /* File uploader styling */
    .uploadedFile {
        border: 1px solid #e9ecef;
        border-radius: 5px;
    }
    
    /* Download button styling */
    .stDownloadButton > button {
        background-color: #28a745;
        color: white;
        border: none;
        width: 100%;
    }
    .stDownloadButton > button:hover {
        background-color: #218838;
    }
    
    /* CSS for simple fade-in animation */
    @keyframes fadein {
        from { opacity: 0; }
        to   { opacity: 1; }
    }
    
    .card {
        animation: fadein 0.5s;
    }
    
    .success-message {
        animation: fadein 1s;
    }
</style>
""", unsafe_allow_html=True)

# App header with gradient background
st.markdown("<h1 class='main-header'>QA Documentation Generator</h1>", unsafe_allow_html=True)

# Main content in tabs for better organization
tab1, tab2 = st.tabs(["Generate Documentation", "About"])

with tab1:
    # Two-column layout
    col1, col2 = st.columns([3, 2])
    
    with col1:
        # Card for file upload
        st.markdown("<div class='card'>", unsafe_allow_html=True)
        st.subheader("📤 Upload Files")
        
        uploaded_files = st.file_uploader(
            "Upload one or more files to analyze", 
            accept_multiple_files=True,
            type=["py", "js", "jsx", "ts", "tsx", "html", "css", "cs", "java", "aspx", "yml", "yaml", "sql"],
            key="file_uploader"
        )
        
        project_name = st.text_input("Project Name (optional)", value="")
        
        st.markdown("<div class='warning-message'>Processing may take several minutes for large files.</div>", unsafe_allow_html=True)
        
        generate_btn = st.button("✨ Generate All Documentation", disabled=not uploaded_files)
        st.markdown("</div>", unsafe_allow_html=True)
    
    with col2:
        # Card for results/documents
        st.markdown("<div class='card'>", unsafe_allow_html=True)
        st.subheader("📑 Generated Documents")
        
        if "result" in st.session_state and st.session_state["result"]["success"]:
            result = st.session_state["result"]
            
            # Create a download section for all documents
            st.markdown("<h3 style='text-align: center; margin-bottom: 20px;'>📥 All Generated Documents</h3>", unsafe_allow_html=True)
            
            # Count available documents
            available_docs = 0
            component_doc_available = "doc_path" in result and (os.path.exists(result["doc_path"]) or "doc_content" in result)
            csv_available = "csv_path" in result and (os.path.exists(result["csv_path"]) or "csv_content" in result)
            bl_available = ("business_logic_doc" in result and (os.path.exists(result["business_logic_doc"]) or "business_logic_content" in result)) or \
                          ("business_logic_docs" in result and result["business_logic_docs"])
            
            if component_doc_available:
                available_docs += 1
            if csv_available:
                available_docs += 1
            if bl_available:
                if "business_logic_docs" in result:
                    available_docs += len(result["business_logic_docs"])
                else:
                    available_docs += 1
            
            if available_docs > 0:
                st.markdown(f"<div class='success-message'>✅ Successfully generated {available_docs} document(s)</div>", unsafe_allow_html=True)
                
                # Create a grid of download buttons
                download_cols = st.columns(min(3, available_docs))
                col_index = 0
                
                # Component Action Documentation
                if component_doc_available:
                    doc_path = result["doc_path"]
                    doc_contents = None
                    
                    # Get doc contents
                    if "doc_content" in result:
                        doc_contents = result["doc_content"]
                    elif os.path.exists(doc_path):
                        try:
                            with open(doc_path, "rb") as file:
                                doc_contents = file.read()
                        except Exception as e:
                            st.warning(f"Could not read component documentation file: {str(e)}")
                    
                    if doc_contents:
                        with download_cols[col_index % len(download_cols)]:
                            st.download_button(
                                label="📄 Component Doc",
                                data=doc_contents,
                                file_name=result.get("doc_filename", os.path.basename(doc_path)),
                                mime="text/markdown",
                                key="doc_download",
                                help="Component Action Documentation (Markdown)"
                            )
                            col_index += 1
                
                # CSV Test Cases
                if csv_available:
                    csv_path = result["csv_path"]
                    csv_contents = None
                    
                    # Get CSV contents
                    if "csv_content" in result:
                        csv_contents = result["csv_content"]
                    elif os.path.exists(csv_path):
                        try:
                            with open(csv_path, "rb") as file:
                                csv_contents = file.read()
                        except Exception as e:
                            st.warning(f"Could not read CSV file: {str(e)}")
                    
                    if csv_contents:
                        with download_cols[col_index % len(download_cols)]:
                            st.download_button(
                                label="📊 Test Cases (CSV)",
                                data=csv_contents,
                                file_name="Test_Cases.csv",
                                mime="text/csv",
                                key="csv_download",
                                help="Test Cases in CSV format"
                            )
                            col_index += 1
                
                # Business Logic Documentation - Multiple docs
                if "business_logic_docs" in result and result["business_logic_docs"]:
                    for i, doc_info in enumerate(result["business_logic_docs"]):
                        if "content" in doc_info and doc_info["content"]:
                            with download_cols[col_index % len(download_cols)]:
                                st.download_button(
                                    label=f"📘 Business Logic Doc",
                                    data=doc_info["content"],
                                    file_name=doc_info["filename"],
                                    mime="text/markdown",
                                    key=f"bl_download_{i}",
                                    help=f"Business Logic Documentation {i+1}"
                                )
                                col_index += 1
                
                # Business Logic Documentation - Single doc
                elif "business_logic_doc" in result and result["business_logic_doc"]:
                    bl_path = result["business_logic_doc"]
                    bl_contents = None
                    
                    # Get business logic contents
                    if "business_logic_content" in result:
                        bl_contents = result["business_logic_content"]
                    elif os.path.exists(bl_path):
                        try:
                            with open(bl_path, "rb") as file:
                                bl_contents = file.read()
                        except Exception as e:
                            st.warning(f"Could not read business logic file: {str(e)}")
                    
                    if bl_contents:
                        with download_cols[col_index % len(download_cols)]:
                            st.download_button(
                                label="📘 Business Logic Doc",
                                data=bl_contents,
                                file_name=result.get("business_logic_filename", os.path.basename(bl_path)),
                                mime="text/markdown",
                                key="bl_download",
                                help="Business Logic Documentation"
                            )
                            col_index += 1
            else:
                st.markdown("<div class='warning-message'>⚠️ Document generation completed but no files were produced. This may be a temporary file storage issue.</div>", unsafe_allow_html=True)
                st.markdown("<div style='text-align: center; margin-top: 10px;'>Try generating the documentation again.</div>", unsafe_allow_html=True)
        
        else:
            # When no documents are available, show a placeholder
            st.markdown("""
            <div style='text-align: center; padding: 30px; background-color: #f8f9fa; border-radius: 8px; border: 1px dashed #4b6cb7; margin-top: 10px;'>
                <img src="https://img.icons8.com/clouds/100/000000/document.png" style='width: 80px; margin-bottom: 15px;'/>
                <h4 style='margin-bottom: 10px; color: #1388f7;'>Ready to Generate Documents</h4>
                <p style='margin-bottom: 15px;'>Upload your files and click the Generate button</p>
                <p style='font-size: 0.85rem; color: #000000; max-width: 100%; margin: 0 auto;'>
                    The system will automatically generate all document types for download:
                    <ul style="text-align: left; margin-top: 5px;">
                        <li>Component Action Documentation (Markdown)</li>
                        <li>Test Cases (CSV format)</li>
                        <li>Business Logic Documentation (Markdown)</li>
                    </ul>
                </p>
                <p style='font-style: italic; font-size: 0.8rem; margin-top: 15px;'>
                    All documents will be available for direct download after processing
                </p>
            </div>
            """, unsafe_allow_html=True)
        
        st.markdown("</div>", unsafe_allow_html=True)

# Processing logic
if generate_btn:
    if not uploaded_files:
        st.error("Please upload at least one file.")
    else:
        # Show a card for the processing state
        st.markdown("<div class='card'>", unsafe_allow_html=True)
        with st.spinner("Generating documentation..."):
            # Progress indicators
            progress_container = st.container()
            with progress_container:
                progress_msg = st.empty()
                progress_bar = st.progress(0)
                
                # Show stages of processing for combined mode
                stages = ["Analyzing files", "Identifying components", "Extracting abstractions", 
                        "Building relationships", "Generating QA documentation", 
                        "Extracting test cases to CSV", "Analyzing business logic"]
                
                for i, stage in enumerate(stages):
                    progress_msg.text(f"Step {i+1}/{len(stages)}: {stage}...")
                    progress_bar.progress((i + 0.5) / len(stages))
                
                # Process files with combined mode
                result = process_files(
                    files=uploaded_files, 
                    project_name=project_name
                )
                
                # Complete progress
                progress_bar.progress(1.0)
                progress_msg.empty()
            
            # Show results
            if result["success"]:
                # Store in session state - this is crucial for persistence!
                st.session_state["result"] = result
                
                # Force Streamlit to refresh its state by creating a rerun trigger
                st.session_state["trigger_rerun"] = True
                
                # Display success message
                st.markdown("<div class='success-message'>✅ Documentation generated successfully!</div>", unsafe_allow_html=True)
                
                # Add a forced rerun to update the UI with the documents
                st.rerun()
            else:
                st.markdown(f"<div class='error-message'>❌ Error: {result['error']}</div>", unsafe_allow_html=True)
                if "traceback" in result:
                    with st.expander("Error Details"):
                        st.code(result["traceback"])
        st.markdown("</div>", unsafe_allow_html=True)

with tab2:
    # About tab content
    st.markdown("<div class='card'>", unsafe_allow_html=True)
    st.markdown("""
    ### About PocketFlow Agent UI
    
    This is a streamlined user interface for the PocketFlow AI agent, which automatically generates comprehensive documentation from source code files.
    
    #### How It Works:
    
    1. **Upload your source code files** - Simply drag-and-drop or select your code files
    2. **Click the Generate button** - The system processes all files automatically
    3. **Download your documents** - Download buttons appear for each generated document
    
    #### Documents You'll Get:
    
    - **Component Action Documentation** - Markdown file mapping UI components to their actions and effects
    - **Test Cases (CSV)** - Structured test cases ready for import into test management tools
    - **Business Logic Documentation** - Extracted business logic from code and stored procedures
    
    #### Benefits:
    
    - **Comprehensive Analysis** - All document types generated in a single operation
    - **Automatic Processing** - No configuration needed
    - **Simple Interface** - Just upload, generate, and download
    - **Secure Documents** - Files are available only as downloads, not displayed in the browser
    
    This tool analyzes your code using advanced AI techniques to extract components, relationships, behaviors, 
    test scenarios, and business logic automatically.
    """)
    st.markdown("</div>", unsafe_allow_html=True)

# Footer
st.markdown("<div class='footer'>Made with ❤️ by DevMaverickMB</div>", unsafe_allow_html=True)
