from flask import Flask, render_template, request, redirect, flash
from templates.secrtes import *
import pyrebase

app = Flask(__name__)
firebase_db = pyrebase.initialize_app(firebaseConfig)
db = firebase_db.database()
app.secret_key = "key"


def name(regno):
    find = False
    with app.open_resource('students-data.csv', "r") as file:
        csv_file = csv.reader(file, delimiter=",")
        for row in csv_file:
            if regno == row[1]:
                find = True
                return row[2]
        if not find:
            return redirect("/")


@app.route("/", methods=["POST", "GET"])
def home():
    if request.method == "POST" and request.form["email"] != "" and request.form["section"] != "":
        email = request.form["email"]
        number = request.form["phone"]
        section = request.form["section"]
        x = name(str(email.split("@")[0]))
        if x is not None:
            packet = {
                "name": x,
                "number": number,
            }
            db.child("users").child(section).child(email.split("@")[0]).set(packet)
            return redirect("/classmates")
        else:
            return render_template("add.html", flash=flash("Incorrect details or empty fields"))
    else:
        if request.method == "POST":
            return render_template("add.html", flash=flash("*fields are required."))
        else:
            return render_template("add.html")


@app.route("/classmates")
def classmates():
    users = db.get()
    for _ in users:
        students = _.val()
    return render_template("classmate.html", data=students)


@app.route("/feedback", methods=["POST", "GET"])
def feedback():
    if request.method == "POST" and request.form["email"] != "" and request.form["phone"] != "" and request.form["message"] != "":
        email = request.form["email"]
        number = request.form["phone"]
        message = request.form["message"]
        name_get = name(str(email.split("@")[0]))
        if name_get is not None:
            packet = {
                "name": name_get,
                "email": email,
                "number": number,
                "message": message
            }
            db.child("feedback").child(number).push(packet)
            return render_template("feedback.html", flash=flash("Thanks For Your Feedback"))
        else:
            return render_template("feedback.html", flash=flash("Incorrect details or empty fields"))
    else:
        if request.method == "POST":
            return render_template("feedback.html", flash=flash("*fields are required."))
        else:
            return render_template("feedback.html")


if __name__ == "__main__":
    app.run(debug=True)
