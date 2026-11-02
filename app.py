from flask import Flask, render_template, request, redirect, url_for, flash
from datetime import date, datetime
from pathlib import Path
from werkzeug.utils import secure_filename
import json
import uuid

app = Flask(__name__)
app.secret_key = "memorymate-demo-secret-key"

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
UPLOAD_DIR = BASE_DIR / "static" / "uploads"
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

DATA_FILES = {
    "memories": DATA_DIR / "memories.json",
    "people": DATA_DIR / "people.json",
    "reminders": DATA_DIR / "reminders.json",
}
ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "gif", "webp"}


def read_data(kind):
    path = DATA_FILES[kind]
    if not path.exists():
        path.write_text("[]", encoding="utf-8")
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return []


def write_data(kind, items):
    DATA_DIR.mkdir(exist_ok=True)
    DATA_FILES[kind].write_text(
        json.dumps(items, indent=2, ensure_ascii=False), encoding="utf-8"
    )


def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


def save_uploaded_image(file):
    if not file or not file.filename:
        return ""
    if not allowed_file(file.filename):
        flash("Please upload an image file (JPG, PNG, GIF or WEBP).", "error")
        return ""
    safe_name = secure_filename(file.filename)
    unique_name = f"{uuid.uuid4().hex[:10]}_{safe_name}"
    file.save(UPLOAD_DIR / unique_name)
    return unique_name


def image_url(filename, fallback=""):
    return url_for("static", filename=f"uploads/{filename}") if filename else fallback


@app.template_filter("pretty_date")
def pretty_date(value):
    if not value:
        return "No date set"
    try:
        return datetime.strptime(value, "%Y-%m-%d").strftime("%d %b %Y")
    except ValueError:
        return value


@app.route("/")
def dashboard():
    memories = read_data("memories")
    people = read_data("people")
    reminders = sorted(
        read_data("reminders"),
        key=lambda item: (item.get("date", "9999-12-31"), item.get("time", "23:59"))
    )
    today = date.today().isoformat()
    today_reminders = [r for r in reminders if r.get("date") == today]
    upcoming = [r for r in reminders if r.get("date", "") >= today][:4]
    return render_template(
        "dashboard.html",
        memories=memories,
        people=people,
        reminders=reminders,
        today_reminders=today_reminders,
        upcoming=upcoming,
        today=date.today().strftime("%A, %d %B %Y"),
        image_url=image_url,
    )


@app.route("/memories", methods=["GET", "POST"])
def memories_page():
    memories = read_data("memories")
    if request.method == "POST":
        title = request.form.get("title", "").strip()
        description = request.form.get("description", "").strip()
        memory_date = request.form.get("memory_date", "").strip()
        if not title:
            flash("Please add a title for this memory.", "error")
            return redirect(url_for("memories_page"))
        photo = save_uploaded_image(request.files.get("photo"))
        memories.insert(0, {
            "id": uuid.uuid4().hex[:8],
            "title": title,
            "description": description,
            "date": memory_date,
            "photo": photo,
        })
        write_data("memories", memories)
        flash("Memory added to your gallery.", "success")
        return redirect(url_for("memories_page"))
    return render_template("memories.html", memories=memories, image_url=image_url)


@app.post("/memories/delete/<memory_id>")
def delete_memory(memory_id):
    memories = read_data("memories")
    target = next((m for m in memories if m.get("id") == memory_id), None)
    if target and target.get("photo"):
        try:
            (UPLOAD_DIR / target["photo"]).unlink(missing_ok=True)
        except OSError:
            pass
    write_data("memories", [m for m in memories if m.get("id") != memory_id])
    flash("Memory deleted.", "success")
    return redirect(url_for("memories_page"))


@app.route("/people", methods=["GET", "POST"])
def people_page():
    people = read_data("people")
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        relationship = request.form.get("relationship", "").strip()
        note = request.form.get("note", "").strip()
        if not name:
            flash("Please add a name.", "error")
            return redirect(url_for("people_page"))
        photo = save_uploaded_image(request.files.get("photo"))
        people.insert(0, {
            "id": uuid.uuid4().hex[:8],
            "name": name,
            "relationship": relationship or "Family & friend",
            "note": note,
            "photo": photo,
        })
        write_data("people", people)
        flash("Person added to your circle.", "success")
        return redirect(url_for("people_page"))
    return render_template("people.html", people=people, image_url=image_url)


@app.post("/people/delete/<person_id>")
def delete_person(person_id):
    people = read_data("people")
    target = next((p for p in people if p.get("id") == person_id), None)
    if target and target.get("photo"):
        try:
            (UPLOAD_DIR / target["photo"]).unlink(missing_ok=True)
        except OSError:
            pass
    write_data("people", [p for p in people if p.get("id") != person_id])
    flash("Person removed.", "success")
    return redirect(url_for("people_page"))


@app.route("/reminders", methods=["GET", "POST"])
def reminders_page():
    reminders = sorted(
        read_data("reminders"),
        key=lambda item: (item.get("date", "9999-12-31"), item.get("time", "23:59"))
    )
    if request.method == "POST":
        title = request.form.get("title", "").strip()
        reminder_date = request.form.get("date", "").strip()
        reminder_time = request.form.get("time", "").strip()
        category = request.form.get("category", "Daily routine").strip()
        notes = request.form.get("notes", "").strip()
        if not title or not reminder_date:
            flash("Please enter a reminder and a date.", "error")
            return redirect(url_for("reminders_page"))
        reminders.append({
            "id": uuid.uuid4().hex[:8],
            "title": title,
            "date": reminder_date,
            "time": reminder_time,
            "category": category,
            "notes": notes,
            "done": False,
        })
        write_data("reminders", reminders)
        flash("Reminder saved.", "success")
        return redirect(url_for("reminders_page"))
    return render_template("reminders.html", reminders=reminders, today=date.today().isoformat())


@app.post("/reminders/toggle/<reminder_id>")
def toggle_reminder(reminder_id):
    reminders = read_data("reminders")
    for reminder in reminders:
        if reminder.get("id") == reminder_id:
            reminder["done"] = not reminder.get("done", False)
            break
    write_data("reminders", reminders)
    return redirect(url_for("reminders_page"))


@app.post("/reminders/delete/<reminder_id>")
def delete_reminder(reminder_id):
    reminders = read_data("reminders")
    write_data("reminders", [r for r in reminders if r.get("id") != reminder_id])
    flash("Reminder deleted.", "success")
    return redirect(url_for("reminders_page"))


@app.errorhandler(413)
def too_large(_error):
    flash("That image is too large. Please choose an image under 8 MB.", "error")
    return redirect(request.referrer or url_for("dashboard"))


app.config["MAX_CONTENT_LENGTH"] = 8 * 1024 * 1024

if __name__ == "__main__":
    for kind, path in DATA_FILES.items():
        if not path.exists():
            path.write_text("[]", encoding="utf-8")
    app.run(debug=True)
