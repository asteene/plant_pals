from flask import Blueprint,render_template

main = Blueprint('main', __name__)

@main.route("/")
def home():
    return render_template("index.html")

@main.route("/new")
def new_post():
    return render_template("new.html")

@main.route("/journals")
def journals():
    return render_template("journals.html")

@main.route("/profile") #Once the account feature is created the router will include idenitfying profile information. I'm also assuming the profile page can act as the users & friends profiles
def profile():
    return render_template("profile.html")

@main.route("/settings")
def settings():
    return render_template("settings.html")

#Post pages 

@main.route("/journal") #Once journals DB is made routing will include journal information 
def journal():
    return render_template("journal.html")

@main.route("/journal/entry") #Once journals DB is made routing will include journal & entry information 
def entry():
    return render_template("entry.html")

#HTML file to test out functions. Delete later
@main.route("/example")
def example_file():
    return render_template("example.html")
