import os

# Define the folder and file structure
project_structure = {
    "app": [  # Application folder
        "__init__.py",
        "routes.py",
        "services.py",
        "config.py"
    ],
    "": [  # Root folder
        "run.py",
        "requirements.txt",
        ".gitignore",
        "README.md"
    ]
}

# Function to create folders and files
def setup_project():
    for folder, files in project_structure.items():
        folder_path = os.path.join(os.getcwd(), folder)
        
        # Create folders if they don't exist
        if folder and not os.path.exists(folder_path):
            os.makedirs(folder_path)
            print(f"📁 Created folder: {folder_path}")

        # Create empty files
        for file in files:
            file_path = os.path.join(folder_path, file)
            if not os.path.exists(file_path):
                with open(file_path, "w") as f:
                    pass  # Create an empty file
                print(f"📄 Created file: {file_path}")

# Run the setup script
if __name__ == "__main__":
    setup_project()
    print("✅ Project structure setup completed! 🎉")
