import os
import sys

# Add project root to sys.path so imports from the repository work when running this script
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from modelscope_agent.utils.nltk_utils import install_nltk_data


if __name__ == '__main__':
    install_nltk_data()
    print('INSTALL_NLTK_COMPLETE')
