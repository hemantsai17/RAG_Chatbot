import os
import logging
import sys

log_dir='Logs'
log_format = '[%(asctime)s : %(levelname)s : %(module)s : %(message)s]'

log_filepath = os.path.join(log_dir , 'running logs')

os.makedirs(log_dir,exist_ok=True)

logging.basicConfig(level=logging.INFO , 
                    format=log_format , 
                    handlers=[logging.FileHandler(log_filepath) , logging.StreamHandler(sys.stdout)])


logger = logging.getLogger("Logger RAG")