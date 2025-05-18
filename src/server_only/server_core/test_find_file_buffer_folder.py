import os

def find_folder(targetFolder):
    startDir = os.path.abspath('.')
    for root, dirs, files in os.walk(startDir):
        if targetFolder in dirs:
            return os.path.join(root, targetFolder)
    return None

if __name__=='__main__':
    print(find_folder('file_buffer_folder'))
