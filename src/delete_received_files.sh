# delete_received_files.sh

# To run this script: ./delete_received_files.sh 
# Note: Have to cd to the src folder for this to work

# Specify the directory where files should be deleted
TARGET_DIR="./received_files"

echo "Target directory is: $TARGET_DIR"

# Check if the folder exists
if [ -d "$TARGET_DIR" ]; then
    # Delete all files in the specified folder (but not subdirectories)
    # Use option '-rf' to delete all files and subdirectories    
    rm -f "$TARGET_DIR"/*
    echo "All files in $TARGET_DIR have been deleted."
else
    echo "Error: $TARGET_DIR does not exist."
fi