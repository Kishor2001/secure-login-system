from flask import Flask, render_template_string, request, redirect, session
import sqlite3
import bcrypt

app = Flask(__name__)
app.secret_key = "secure_secret_key"

conn = sqlite3.connect("users.db")
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS users(
id INTEGER PRIMARY KEY AUTOINCREMENT,
username TEXT UNIQUE,
password BLOB
)
""")

conn.commit()
conn.close()

register_page = """
<h2>Register</h2>
<form method="POST">
Username: <input name="username"><br><br>
Password: <input type="password" name="password"><br><br>
<button type="submit">Register</button>
</form>
<a href="/login">Login</a>
"""

login_page = """
<h2>Login</h2>
<form method="POST">
Username: <input name="username"><br><br>
Password: <input type="password" name="password"><br><br>
<button type="submit">Login</button>
</form>
<a href="/">Register</a>
"""

@app.route("/", methods=["GET","POST"])
def register():

    if request.method == "POST":

        username = request.form["username"].strip()
        password = request.form["password"]

        if len(username) < 3:
            return "Username too short"

        hashed = bcrypt.hashpw(
            password.encode(),
            bcrypt.gensalt()
        )

        try:
            conn = sqlite3.connect("users.db")
            cursor = conn.cursor()

            cursor.execute(
                "INSERT INTO users(username,password) VALUES(?,?)",
                (username, hashed)
            )

            conn.commit()
            conn.close()

            return redirect("/login")

        except:
            return "User already exists"

    return render_template_string(register_page)

@app.route("/login", methods=["GET","POST"])
def login():

    if request.method == "POST":

        username = request.form["username"]
        password = request.form["password"]

        conn = sqlite3.connect("users.db")
        cursor = conn.cursor()

        cursor.execute(
            "SELECT password FROM users WHERE username=?",
            (username,)
        )

        user = cursor.fetchone()

        if user and bcrypt.checkpw(
            password.encode(),
            user[0]
        ):
            session["user"] = username
            return redirect("/dashboard")

        return "Invalid Credentials"

    return render_template_string(login_page)

@app.route("/dashboard")
def dashboard():

    if "user" not in session:
        return redirect("/login")

    return f"""
    <h2>Welcome {session['user']}</h2>
    <a href='/logout'>Logout</a>
    """

@app.route("/logout")
def logout():
    session.clear()
    return redirect("/login")

if __name__ == "__main__":
    app.run(debug=True)