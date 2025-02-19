from pathlib import Path
import logging
import os

logging.basicConfig(level=logging.INFO , format='[%(asctime)s]: %(message)s')

project_name = 'RAG_Chatbot'

list_of_files =[
    ".github/workflows/.gitkeep",
    f"src/{project_name}/__init__.py",
    f"src/{project_name}/documents/",
    f"src/{project_name}/components/__init__.py",
    f"src/{project_name}/utils/__init__.py",
    f"src/{project_name}/utils/common.py",
    f"src/{project_name}/logging/__init__.py",
    f"src/{project_name}/config/__init__.py",
    f"src/{project_name}/config/configuration.py",
    f"src/{project_name}/pipeline/__init__.py",
    f"src/{project_name}/entity/__init__.py",
    f"src/{project_name}/constants/__init__.py",
    "yaml/config.yaml",
    "yaml/params.yaml",
    "app.py",
    "main.py",
    "Dockerfile",
    "requirements.txt",
    "setup.py",
    "research/research.ipynb"

]

for file in list_of_files:
    filepath = Path(file)
    filedir , filename = os.path.split(filepath)
    
    if filedir != "":
        os.makedirs(filedir , exist_ok=True)
        logging.info(f'file directory created {filedir} for file name {filename}')
        
    if (not os.path.exists(filepath)) or (os.path.getsize(filepath) == 0):
         with open(filepath , 'w') as f :
            pass
            logging.info(f'created empty file: {filename}')
        
    else:
        logging.info(f'file already exists : {filepath}')
       
        