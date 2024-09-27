from flaskr import createApp
from flask import Flask, render_template

app = Flask(__name__)

@app.route("/")
def home():
    return render_template("index.html")

#HTML file to test out functions. Delete later
@app.route("/example")
def example_file():
    return render_template("example.html")



if __name__ == "__main__":
    app.run(debug=True)