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
    # Videos table with trade
    c.execute("""CREATE TABLE IF NOT EXISTS videos(
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    title TEXT,
                    filename TEXT,
                    trade TEXT)""")
    # PDFs table with trade
    c.execute("""CREATE TABLE IF NOT EXISTS pdfs(
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    filename TEXT,
                    trade TEXT)""")
    # Notes table with trade
    c.execute("""CREATE TABLE IF NOT EXISTS notes(
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    content TEXT,
                    trade TEXT)""")
    conn.commit()
    conn.close()

init_db()

# ----------------- Site Name Context -----------------
@app.context_processor
def inject_site_name():
    return dict(site_name="Pooja Learning App")

# ----------------- Admin Login -----------------
@app.route("/admin_login", methods=["GET","POST"])
def admin_login():
    if request.method=="POST":
        username = request.form["username"]
        password = request.form["password"]
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
    trades = ["IIOT","IR&DMT","Plumber"]
    if request.method=="POST":
        file = request.files.get("file")
        title = request.form.get("title","")
        trade = request.form.get("trade","General")
        if file and file.filename!="":
            filepath = os.path.join(UPLOAD_FOLDER, file.filename)
            file.save(filepath)
            conn = sqlite3.connect(DB_PATH)
            c = conn.cursor()
            if "video" in request.form:
                c.execute("INSERT INTO videos (title, filename, trade) VALUES (?,?,?)",
                          (title, file.filename, trade))
            elif "pdf" in request.form:
                c.execute("INSERT INTO pdfs (filename, trade) VALUES (?,?)",
                          (file.filename, trade))
            conn.commit()
            conn.close()
    return render_template("admin.html", trades=trades)

# ----------------- Logout -----------------
@app.route("/logout")
def logout():
    session.clear()
    return redirect("/admin_login")

if __name__=="__main__":
    app.run(host="0.0.0.0", port=10000)
