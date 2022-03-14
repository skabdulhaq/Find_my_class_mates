from flask import Flask, render_template, request, redirect, flash
from templates.secrtes import *
import pyrebase
import gunicorn

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
            return None


def not_exist(id_num):
    global data_
    users = db.get()
    for _ in users:
        data_ = _.val()
    for section in data_:
        if id_num in data_[section].keys():
            # if reg == id_num:
            print(data_[section].keys())
            return False
    return True


@app.route("/", methods=["POST", "GET"])
def home():
    if request.method == "POST" and request.form["email"] != "" and request.form["section"] != "":
        email = request.form["email"]
        number = request.form["phone"]
        section = request.form["section"]
        x = name(str(email.split("@")[0]))
        print(x)
        print(email)
        not_exist_ = not_exist(email.split("@")[0])
        if x is not None:
            if not_exist_:
                packet = {
                    "name": x,
                    "number": number,
                }
                db.child("users").child(section).child(email.split("@")[0]).set(packet)
                return redirect("/classmates")
            else:
                return render_template("add.html", flash=flash("Your mail has been registered click on classmates button to check your classmates."))
        else:
            return render_template("add.html", flash=flash("Incorrect details or empty fields."))
    else:
        if request.method == "POST":
            return render_template("add.html", flash=flash("*fields are required."))
        else:
            return render_template("add.html")


@app.route("/classmates")
def classmates():
    global students
    users = db.get()
    for _ in users:
        students = _.val()
    total = 0
    for sec in students:
        total += len(students[sec])
        # print(f"{sec} - ")
    print(total)
    return render_template("classmate.html", data=students, len=len, total=total)


@app.route("/feedback", methods=["POST", "GET"])
def feedback():
    if request.method == "POST" and request.form["email"] != "" and request.form["phone"] != "" and request.form["message"] != "":
        email = request.form["email"]
        number = request.form["phone"]
        message = request.form["message"]
        name_get = name(str(email.split("@")[0]))
        if name_get is not None and len(number) == 10:
            packet = {
                "completed": False,
                "name": name_get,
                "email": email,
                "number": number,
                "message": message
            }
            db.child("feedback").child(number).push(packet)
            return render_template("feedback.html", flash=flash("Thanks For Your Feedback."))
        else:
            return render_template("feedback.html", flash=flash("Incorrect details or empty fields."))
    else:
        if request.method == "POST":
            return render_template("feedback.html", flash=flash("*fields are required."))
        else:
            return render_template("feedback.html")


if __name__ == "__main__":
    app.run(debug=True)
