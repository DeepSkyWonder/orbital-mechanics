"""
Example usage of the GitHub push automation script
Run this in a Google Colab cell after making changes to your files
"""

# Method 1: Direct execution
exec(open('/content/push_to_github.py').read())

"""
Method 2: Import and run (alternative)
import sys
sys.path.append('/content')
from push_to_github import main
main()
"""

"""
Method 3: Command line (in a cell with !)
!python /content/push_to_github.py
"""