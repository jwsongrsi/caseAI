import os

# Use the current directory for txt files
folder_path = os.getcwd()  # Current working directory
# Specify the output file name
output_file = 'combined_text.txt'

# Create or overwrite the output file
with open(output_file, 'w', encoding='utf-8') as outfile:
    # Loop through all files in the current directory
    for filename in os.listdir(folder_path):
        # Check if the file is a .txt file
        if filename.endswith('.txt') and filename != output_file:  # Avoid including the output file
            file_path = os.path.join(folder_path, filename)
            # Open and read the content of the current file
            with open(file_path, 'r', encoding='utf-8') as infile:
                content = infile.read()
                # Write the content to the output file
                outfile.write(content + '\n')  # Add newline between files

print(f"All text files have been combined into '{output_file}'")
