MEMORYMATE - Beginner-Friendly Flask Project
============================================

WHAT'S INCLUDED
- Home dashboard
- Memory gallery (add photo, title, description and date)
- My people (add names, relationships, notes and photos)
- Daily reminders (add, complete and delete reminders)
- JSON files for saving data; NO SQL DATABASE
- Responsive layout with a calm lavender, peach and sage colour palette

REQUIREMENTS
- Python 3.10 or newer recommended
- Internet is only needed once to install Flask. Google Fonts are loaded online; the site still works without them.

HOW TO RUN (Windows)
1. Extract the ZIP file.
2. Open the extracted MemoryMate folder.
3. Click the folder address bar in File Explorer, type cmd, and press Enter.
4. Run:
       py -m venv venv
       venv\Scripts\activate
       py -m pip install -r requirements.txt
       py app.py
5. Open this address in your browser:
       http://127.0.0.1:5000

HOW TO RUN (macOS)
1. Open Terminal and use cd to enter the extracted MemoryMate folder.
2. Run:
       python3 -m venv venv
       source venv/bin/activate
       python3 -m pip install -r requirements.txt
       python3 app.py
3. Open:
       http://127.0.0.1:5000

NOTES
- The website saves data to data/memories.json, data/people.json and data/reminders.json.
- Uploaded images are stored in static/uploads.
- The sample content is fictional. You can remove it by replacing each JSON file's contents with [].
- This is a student demo, not a medical device. Reminder entries are shown in the website; no automatic phone notifications are sent.
- Do not use real sensitive patient information on a publicly hosted demo without appropriate security and consent.
- The Flask development server is for local testing, not public production deployment.
