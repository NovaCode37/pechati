import sys
import os
import glob

project_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_dir)

# Auto-detect virtualenv site-packages
venv_patterns = [
    os.path.join(project_dir, 'flaskenv', 'lib', 'python*', 'site-packages'),
    os.path.join(project_dir, 'venv', 'lib', 'python*', 'site-packages'),
]
for pattern in venv_patterns:
    for sp in glob.glob(pattern):
        if sp not in sys.path:
            sys.path.insert(0, sp)

from app import app as application
