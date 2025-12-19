# file_transfer.py

import os
import requests
import tkinter as tk
from tkinter import filedialog

# Helper functions
def get_file_extension(filename):
    # Returns the extension of a file, including dot.
    # Example: .txt, .pdf, .png, etc..
    return os.path.splitext(filename)[1]
def get_file_dir_path(filepath):
    return os.path.dirname(filepath)

# FastAPI logic for uploading a file with given file content and room code
def upload(uri, roomCode, filename):
    def ask_file_location(filename, fileExtension):
        root = tk.Tk()
        root.withdraw()
        filepath = filedialog.askopenfilename(defaultextension=fileExtension, initialfile=filename)
        return filepath
    
    fileExtension = get_file_extension(filename)
    filepath = ask_file_location(filename, fileExtension)
    
    if os.path.isfile(filepath):
        print(f'✅ File [{filename}] exists on user local machine.')
    else:
        print(f'❌ File [{filename}] does not exist on user local machine.')
    
    with open(filepath, 'rb') as f:
        files = {'file': (filename, f)}
        response = requests.post(uri+'upload/'+roomCode, files=files)
        print(f'Response status code: {response.status_code}')
    return 

# FastAPI logic for downloading a file with given filename and room code
def download(uri, roomCode, filename, chunkSize):
    def ask_file_save_location(filename, fileExtension):
        # Additional arguments for filedialog.asksaveasfilename();
        #   provides default file extensions to users for selection.
        fileTypes = [('Text files', '*.txt'),
                     ('PDF files', '*.pdf'),
                     ('JPG files', '*.jpg'),
                     ('JPEG files', '*.jpeg'),
                     ('PNG files', '*.png'),
                     ('All files', '*.*')]
        
        root = tk.Tk()
        root.withdraw() # This hides the main window of Tk
        savePath = filedialog.asksaveasfilename(defaultextension=fileExtension, 
                                                initialfile=filename)
        return savePath
    
    # Setting 'stream' to True allows the client to download the file without loading it into memory
    response = requests.get(uri+'download/'+roomCode+'/'+filename, stream=True)
    print(f'Response status code: {response.status_code}')
    
    fileExtension = get_file_extension(filename)
    print('file ext:', fileExtension)
    savePath = ask_file_save_location(filename, fileExtension)
    try: 
        with open(savePath, 'wb') as f:
            for chunk in response.iter_content(chunk_size=chunkSize):
                f.write(chunk)
        fileDirPath = get_file_dir_path(savePath)
        print(f'✅ File [{filename}] downloaded successfully. It is stored in [{fileDirPath}].')
    except Exception as e:
        print(f'❌ Failed to download file [{filename}].')
        print(f'Failed reason: {e}.')
    return