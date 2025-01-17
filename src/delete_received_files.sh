# delete_received_files.sh

# Specify the directory where files should be deleted
TARGET_DIR="received_files"

# Delete all files in the specified folder (but not subdirectories)
rm -f "$TARGET_DIR"/*

echo "All files in $TARGET_DIR have been deleted."