from flask import Flask, render_template, request
import requests
from bs4 import BeautifulSoup
import os
import time
import glob
import difflib

app = Flask(__name__)

# Fetch website text
def get_website_text(url):
    try:
        response = requests.get(url)
        soup = BeautifulSoup(response.text, "html.parser")
        return soup.get_text()
    except:
        return None

# Save with version (timestamp)
def save_content(url, content):
    filename = url.replace("https://", "").replace("/", "_")
    timestamp = int(time.time())
    path = f"data/stored_pages/{filename}_{timestamp}.txt"

    with open(path, "w", encoding="utf-8") as f:
        f.write(content)

# Load latest version
def load_latest_content(url):
    filename = url.replace("https://", "").replace("/", "_")
    files = glob.glob(f"data/stored_pages/{filename}_*.txt")

    if not files:
        return None

    latest_file = max(files, key=os.path.getctime)

    with open(latest_file, "r", encoding="utf-8") as f:
        return f.read()

# Calculate % change
def get_change_percentage(old, new):
    matcher = difflib.SequenceMatcher(None, old, new)
    return round((1 - matcher.ratio()) * 100, 2)

# Highlight changes
def highlight_changes(old, new):
    diff = difflib.ndiff(old.split(), new.split())
    changes = [word for word in diff if word.startswith('+ ') or word.startswith('- ')]
    return " ".join(changes[:50])

@app.route("/", methods=["GET", "POST"])
def index():
    result = ""
    alert = ""
    changes = ""

    if request.method == "POST":
        url = request.form["url"]

        new_content = get_website_text(url)

        if not new_content:
            result = "Invalid URL"
        else:
            old_content = load_latest_content(url)

            if old_content:
                change_percent = get_change_percentage(old_content, new_content)

                if change_percent > 10:
                    result = f"🚨 Major Change Detected! ({change_percent}%)"
                    alert = "ALERT: Major update detected!"
                elif change_percent > 2:
                    result = f"⚠️ Minor Change Detected ({change_percent}%)"
                else:
                    result = f"✅ No Significant Change ({change_percent}%)"

                changes = highlight_changes(old_content, new_content)

            else:
                result = "First Time - Data Stored"

            save_content(url, new_content)

    return render_template("index.html", result=result, alert=alert, changes=changes)

if __name__ == "__main__":
    app.run(debug=True)