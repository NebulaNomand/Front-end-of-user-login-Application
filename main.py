import sqlite3
from flask import Flask, render_template, request, redirect, url_for, session
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = "supersecretkey123"   # Change this in production


# -------------------- DATABASE INITIALIZATION --------------------
def init_db():
    conn = sqlite3.connect("users.db")
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT UNIQUE,
            password TEXT
        )
    """)
    conn.commit()
    conn.close()


init_db()


# -------------------- LOGIN PAGE --------------------
@app.route("/", methods=["GET", "POST"])
def login():
    message = ""

    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]

        conn = sqlite3.connect("users.db")
        cursor = conn.cursor()
        cursor.execute("SELECT password FROM users WHERE email = ?", (email,))
        user = cursor.fetchone()
        conn.close()

        if user and check_password_hash(user[0], password):
            session["email"] = email
            return redirect(url_for("dashboard"))
        else:
            message = "Invalid email or password"

    return render_template("login.html", message=message)


# -------------------- SIGNUP PAGE --------------------
@app.route("/signup", methods=["GET", "POST"])
def signup():
    message = ""

    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]

        hashed_password = generate_password_hash(password)

        try:
            conn = sqlite3.connect("users.db")
            cursor = conn.cursor()
            cursor.execute("INSERT INTO users (email, password) VALUES (?, ?)",
                           (email, hashed_password))
            conn.commit()
            conn.close()
            message = "Account created successfully! Please log in."
            return redirect(url_for("login"))
        except sqlite3.IntegrityError:
            message = "This email already exists!"

    return render_template("signup.html", message=message)


# -------------------- PROTECTED DASHBOARD --------------------
@app.route("/dashboard")
def dashboard():
    if "email" not in session:
        return redirect(url_for("login"))
    return render_template("dashboard.html", email=session["email"])


# -------------------- LOGOUT --------------------
@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))


if __name__ == "__main__":
    app.run(debug=True)
