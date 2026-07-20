from flask import *
import spacy
from pickle import load
from reader import read_latest

# --------------------------
# Load SpaCy
# --------------------------
# nlp = spacy.load("en_core_web_lg")
nlp = spacy.load("en_core_web_sm")

# --------------------------
# Load ML Model
# --------------------------
with open("model.pkl", "rb") as f:
    model = load(f)

with open("vector.pkl", "rb") as f:
    tv = load(f)

# --------------------------
# Flask App
# --------------------------
app = Flask(__name__)
app.secret_key = "spam_detection_project_2026"

# --------------------------
# Cleaning Function
# --------------------------
def clean_function(text):
    text = text.lower()
    doc = nlp(text)
    words = []
    for token in doc:
        if token.is_stop:
            continue
        if token.is_punct:
            continue
        words.append(token.lemma_)
    return " ".join(words)

# ====================================================
# HOME
# ====================================================
@app.route("/", methods=["GET", "POST"])
def home():
    if request.method == "POST":
        text = request.form.get("text")
        clean_text = clean_function(text)
        vector = tv.transform([clean_text])
        prediction = model.predict(vector)[0]
        if prediction.lower() == "ham":
            prediction = "Not Spam"
        else:
            prediction = "Spam"
        return render_template("home.html", body=text, result=prediction)
    return render_template("home.html")

# ====================================================
# LOGIN PAGE
# ====================================================
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        gmail = request.form.get("gmail")
        password = request.form.get("password")
        remember = request.form.get("remember")
        session["gmail"] = gmail
        session["password"] = password
        if remember:
            session.permanent = True
        return redirect("/recent")
    return render_template("login.html")

# ====================================================
# RECENT MAIL (with optional live flag)
# ====================================================
@app.route("/recent")
def recent():
    if "gmail" not in session:
        return redirect("/login")

    live = request.args.get("live") == "1"          # check for live flag

    sender, subject, body = read_latest(
        session["gmail"],
        session["password"]
    )

    if body is None:
        return render_template(
            "recent.html",
            error="Unable to login to Gmail.",
            live=live
        )

    clean_body = clean_function(body)
    vector = tv.transform([clean_body])
    prediction = model.predict(vector)[0]
    if prediction.lower() == "ham":
        result = "Not Spam"
    else:
        result = "Spam"

    return render_template(
        "recent.html",
        sender=sender,
        subject=subject,
        body=body,
        result=result,
        live=live
    )

# ====================================================
# LIVE ANALYSIS – redirects to /recent with live flag
# ====================================================
@app.route("/live")
def live():
    if "gmail" not in session:
        return redirect("/login")
    return redirect("/recent?live=1")

# ====================================================
# LOGOUT
# ====================================================
@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")

# ====================================================
# if __name__ == "__main__":
#     app.run(debug=True)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
