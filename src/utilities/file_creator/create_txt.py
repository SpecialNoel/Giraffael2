# create_txt.py

# .txt: text files

def create_file_with_zeros(filename, filesize):
    """Creates a file with zeros and the specified size in megabytes."""
    filesizeInBytes = filesize * 1024 * 1024
    with open(filename, 'wb') as file:
        file.write(b'\0' * filesizeInBytes) # Fill with null bytes (zeros)

# Create a file of given size (in MB)
create_file_with_zeros('./test_files/large_example.txt', 10)

print('Created example.txt')
