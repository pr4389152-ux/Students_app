from flask import Flask, render_template, request, redirect, session, url_for
import sqlite3
import os

app = Flask(__name__)
app.secret_key = "secret123"

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "database.db")
UPLOAD_FOLDER = os.path.join(BASE_DIR, "static/uploads")
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# ----------------- Database Init -----------------
def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    # Users table
    c.execute("""CREATE TABLE IF NOT EXISTS users(
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT UNIQUE,
                    password TEXT)""")
    # Videos table
    c.execute("""CREATE TABLE IF NOT EXISTS videos(
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    title TEXT,
                    filename TEXT)""")
    # PDFs table
    c.execute("""CREATE TABLE IF NOT EXISTS pdfs(
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    filename TEXT)""")
    # Notes table
    c.execute("""CREATE TABLE IF NOT EXISTS notes(
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    content TEXT)""")
    # MCQs table
    c.execute("""CREATE TABLE IF NOT EXISTS quiz(
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    question TEXT,
                    o1 TEXT,
                    o2 TEXT,
                    o3 TEXT,
                    o4 TEXT,
                    ans TEXT)""")
    conn.commit()
    conn.close()

init_db()

# ----------------- User Login/Register -----------------
@app.route("/", methods=["GET","POST"])
def login():
    if request.method=="POST":
        username = request.form["username"]
        password = request.form["password"]
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute("SELECT * FROM users WHERE username=? AND password=?", (username, password))
        user = c.fetchone()
        conn.close()
        if user:
            session["user"] = username
            return redirect("/dashboard")
        else:
            return "Invalid Credentials"
    return render_template("login.html")

@app.route("/register", methods=["GET","POST"])
def register():
    if request.method=="POST":
        username = request.form["username"]
        password = request.form["password"]
        try:
            conn = sqlite3.connect(DB_PATH)
            c = conn.cursor()
            c.execute("INSERT INTO users (username,password) VALUES (?,?)", (username,password))
            conn.commit()
            conn.close()
            return redirect("/")
        except:
            return "User already exists"
    return render_template("register.html")

# ----------------- Dashboard -----------------
@app.route("/dashboard")
def dashboard():
    if "user" not in session:
        return redirect("/")
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    videos = c.execute("SELECT * FROM videos").fetchall()
    notes = c.execute("SELECT * FROM notes").fetchall()
    pdfs = c.execute("SELECT * FROM pdfs").fetchall()
    quiz = c.execute("SELECT * FROM quiz").fetchall()
    conn.close()
    return render_template("dashboard.html", videos=videos, notes=notes, pdfs=pdfs, quiz=quiz)

# ----------------- Admin Login -----------------
@app.route("/admin_login", methods=["GET","POST"])
def admin_login():
    if request.method=="POST":
        username = request.form["username"]
        password = request.form["password"]
        # Hardcoded admin credentials
        if username=="admin" and password=="admin123":
            session["admin"] = username
            return redirect("/admin")
        else:
            return "Invalid Admin Credentials"
    return render_template("admin_login.html")

# ----------------- Admin Panel -----------------
@app.route("/admin", methods=["GET","POST"])
def admin():
    if "admin" not in session:
        return redirect("/admin_login")
    if request.method=="POST":
        file = request.files.get("file")
        title = request.form.get("title","")
        if file and file.filename!="":
            filepath = os.path.join(UPLOAD_FOLDER, file.filename)
            file.save(filepath)
            conn = sqlite3.connect(DB_PATH)
            c = conn.cursor()
            if "video" in request.form:
                c.execute("INSERT INTO videos (title, filename) VALUES (?,?)", (title, file.filename))
            elif "pdf" in request.form:
                c.execute("INSERT INTO pdfs (filename) VALUES (?)", (file.filename,))
            conn.commit()
            conn.close()
    return render_template("admin.html")

# ----------------- Add Note -----------------
@app.route("/add_note", methods=["POST"])
def add_note():
    if "admin" not in session:
        return redirect("/admin_login")
    content = request.form["content"]
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("INSERT INTO notes (content) VALUES (?)", (content,))
    conn.commit()
    conn.close()
    return redirect("/admin")

# ----------------- Add MCQ -----------------
@app.route("/add_quiz", methods=["POST"])
def add_quiz():
    if "admin" not in session:
        return redirect("/admin_login")
    data = request.form
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("INSERT INTO quiz (question,o1,o2,o3,o4,ans) VALUES (?,?,?,?,?,?)",
              (data["q"], data["o1"], data["o2"], data["o3"], data["o4"], data["ans"]))
    conn.commit()
    conn.close()
    return redirect("/admin")

# ----------------- Logout -----------------
@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")

# ----------------- Run App -----------------
if __name__=="__main__":
    app.run(host="0.0.0.0", port=10000)
