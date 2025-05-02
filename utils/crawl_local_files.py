import os
import fnmatch

def crawl_local_files(directory, include_patterns=None, exclude_patterns=None, max_file_size=None, use_relative_paths=True):
    """
    Crawl files in a local directory with similar interface as crawl_github_files.
    
    Args:
        directory (str): Path to local directory
        include_patterns (set): File patterns to include (e.g. {"*.py", "*.js"})
        exclude_patterns (set): File patterns to exclude (e.g. {"tests/*"})
        max_file_size (int): Maximum file size in bytes
        use_relative_paths (bool): Whether to use paths relative to directory
        
    Returns:
        dict: {"files": {filepath: content}}
    """
    if not os.path.isdir(directory):
        raise ValueError(f"Directory does not exist: {directory}")
        
    files_dict = {}
    
    print(f"Crawling directory: {directory}...")
    
    for root, _, files in os.walk(directory):
        for filename in files:
            filepath = os.path.join(root, filename)
            
            # Get path relative to directory if requested
            if use_relative_paths:
                relpath = os.path.relpath(filepath, directory)
            else:
                relpath = filepath
                
            # Check if file matches any include pattern
            included = False
            if include_patterns:
                for pattern in include_patterns:
                    if fnmatch.fnmatch(relpath, pattern):
                        included = True
                        break
            else:
                included = True
                
            # Check if file matches any exclude pattern
            excluded = False
            if exclude_patterns:
                for pattern in exclude_patterns:
                    if fnmatch.fnmatch(relpath, pattern):
                        excluded = True
                        break
                        
            if not included or excluded:
                continue
                
            # Check file size
            if max_file_size and os.path.getsize(filepath) > max_file_size:
                continue
                
            # Better binary file detection - check file extension first
            file_ext = os.path.splitext(filename)[1].lower()
            binary_extensions = {'.png', '.jpg', '.jpeg', '.gif', '.bmp', '.ico', '.pdf', 
                               '.zip', '.gz', '.tar', '.rar', '.exe', '.dll', '.so', '.bin',
                               '.pyc', '.pyd', '.o', '.obj', '.dat', '.db', '.sqlite', '.db3',
                               '.xlsx', '.xls', '.doc', '.docx', '.ppt', '.pptx', '.class',
                               '.jar', '.war', '.ttf', '.otf', '.woff', '.woff2', '.eot', '.svg',
                               '.tiff', '.tif', '.psd', '.mp3', '.mp4', '.avi', '.mkv', '.mov',
                               '.wmv', '.wav', '.flac', '.dmg', '.iso', '.img', '.ds_store'}
                
            if file_ext in binary_extensions or filename.lower() == '.ds_store':
                continue
                
            try:
                # Check for binary content
                is_binary = False
                with open(filepath, 'rb') as f:
                    chunk = f.read(1024)
                    # Check for null bytes or high percentage of non-printable chars
                    if b'\x00' in chunk or sum(c < 9 or 13 < c < 32 or c > 126 for c in chunk) > len(chunk) * 0.1:
                        is_binary = True
                
                if is_binary:
                    continue
                
                # Try reading as UTF-8
                with open(filepath, 'r', encoding='utf-8') as f:
                    content = f.read()
                    files_dict[relpath] = content
                    
            except UnicodeDecodeError:
                # Skip files that can't be decoded as text
                continue
            except Exception as e:
                print(f"Warning: Could not read file {filepath}: {e}")
                
    print(f"Fetched {len(files_dict)} files.")
    return {"files": files_dict}

if __name__ == "__main__":
    print("--- Crawling parent directory ('..') ---")
    files_data = crawl_local_files("..", exclude_patterns={"*.pyc", "__pycache__/*", ".git/*", "output/*"})
    print(f"Found {len(files_data['files'])} files:")
    for path in files_data["files"]:
        print(f"  {path}")