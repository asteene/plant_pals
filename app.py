from flaskr import createApp
from flask import Flask, render_template

app = Flask(__name__)

#Nav bar
@app.route("/")
def home():
    return render_template("index.html")

@app.route("/new")
def new_post():
    return render_template("new.html")

@app.route("/journals")
def journals():
    return render_template("journals.html")

@app.route("/profile") #Once the account feature is created the router will include idenitfying profile information. I'm also assuming the profile page can act as the users & friends profiles
def profile():
    return render_template("profile.html")

@app.route("/settings")
def settings():
    return render_template("settings.html")

#Post pages 

@app.route("/journal") #Once journals DB is made routing will include journal information 
def journal():
    return render_template("journal.html")

@app.route("/journal/entry") #Once journals DB is made routing will include journal & entry information 
def entry():
    return render_template("entry.html")

#HTML file to test out functions. Delete later
@app.route("/example")
def example_file():
    return render_template("example.html")



if __name__ == "__main__":
    app.run(debug=True)