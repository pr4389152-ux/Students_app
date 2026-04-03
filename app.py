from flask import Flask, render_template, request, redirect, session, url_for
import sqlite3, os

app = Flask(__name__)
app.secret_key = "secret123"

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "database.db")

os.makedirs("static/uploads", exist_ok=True)

# ---------- DATABASE ----------
def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    c.execute("CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY, username TEXT, password TEXT)")
    c.execute("CREATE TABLE IF NOT EXISTS videos (id INTEGER PRIMARY KEY, title TEXT, filename TEXT)")
    c.execute("CREATE TABLE IF NOT EXISTS notes (id INTEGER PRIMARY KEY, content TEXT)")
    c.execute("CREATE TABLE IF NOT EXISTS pdfs (id INTEGER PRIMARY KEY, filename TEXT)")
    c.execute("CREATE TABLE IF NOT EXISTS quiz (id INTEGER PRIMARY KEY, question TEXT, o1 TEXT, o2 TEXT, o3 TEXT, o4 TEXT, ans TEXT)")

    conn.commit()
    conn.close()

init_db()

# ---------- LOGIN ----------
@app.route("/", methods=["GET","POST"])
def login():
    if request.method == "POST":
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute("SELECT * FROM users WHERE username=? AND password=?", 
                  (request.form["username"], request.form["password"]))
        user = c.fetchone()
        conn.close()

        if user:
            session["user"] = user[1]
            return redirect("/dashboard")
    
    return render_template("login.html")

# ---------- REGISTER ----------
@app.route("/register", methods=["GET","POST"])
def register():
    if request.method == "POST":
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute("INSERT INTO users (username,password) VALUES (?,?)",
                  (request.form["username"], request.form["password"]))
        conn.commit()
        conn.close()
        return redirect("/")
    
    return render_template("register.html")

# ---------- DASHBOARD ----------
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

# ---------- QUIZ ----------
@app.route("/submit_quiz", methods=["POST"])
def submit_quiz():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    questions = c.execute("SELECT * FROM quiz").fetchall()
    conn.close()

    score = 0
    total = len(questions)
    wrong = []

    for q in questions:
        qid = str(q[0])
        user_ans = request.form.get(qid)
        correct = q[6]

        if user_ans == correct:
            score += 1
        else:
            wrong.append({"q": q[1], "your": user_ans, "correct": correct})

    return render_template("result.html", score=score, total=total, wrong=wrong)

# ---------- ADMIN LOGIN ----------
@app.route("/admin_login", methods=["GET","POST"])
def admin_login():
    if request.method == "POST":
        if request.form["username"] == "admin" and request.form["password"] == "1234":
            session["admin"] = True
            return redirect("/admin")
    return render_template("admin_login.html")

# ---------- ADMIN PANEL ----------
@app.route("/admin", methods=["GET","POST"])
def admin():
    if "admin" not in session:
        return redirect("/admin_login")

    if request.method == "POST":
        file = request.files.get("file")
        title = request.form.get("title")

        if file and file.filename != "":
            filepath = os.path.join("static/uploads", file.filename)
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

# ---------- ADD NOTE ----------
@app.route("/add_note", methods=["POST"])
def add_note():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("INSERT INTO notes (content) VALUES (?)", (request.form["content"],))
    conn.commit()
    conn.close()
    return redirect("/admin")

# ---------- ADD QUIZ ----------
@app.route("/add_quiz", methods=["POST"])
def add_quiz():
    d = request.form
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    c.execute("INSERT INTO quiz (question,o1,o2,o3,o4,ans) VALUES (?,?,?,?,?,?)",
              (d["q"], d["o1"], d["o2"], d["o3"], d["o4"], d["ans"]))

    conn.commit()
    conn.close()
    return redirect("/admin")

# ---------- LOGOUT ----------
@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")

# ---------- RUN ----------
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
