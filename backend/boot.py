import sys
import os
import site

# Force the local venv site-packages to be FIRST in the path
# This overrides any global packages causing conflicts
current_dir = os.path.dirname(os.path.abspath(__file__))
venv_site_packages = os.path.join(current_dir, "venv", "Lib", "site-packages")

print(f"Forcing site-packages path: {venv_site_packages}")
sys.path.insert(0, venv_site_packages)

from youtube_transcript_api import YouTubeTranscriptApi
print(f"Loaded Transcript API from: {YouTubeTranscriptApi}")

# Now import the main flask app
from app import app

if __name__ == '__main__':
    print("Starting Flask app via bootloader...")
    app.run(port=5000, debug=True)
