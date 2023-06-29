from flask import Flask, render_template, request, send_file, redirect
import utils
from extension import database

app = Flask(__name__)


@app.route("/")
@app.route("/index")
def index():
    return render_template("index.html")


@app.route("/speech", methods=["POST"])
def speech():
    message = request.form["message"]
    return render_template("index.html", result=utils.speak_and_save(message.strip()))


@app.route("/history")
def history():
    return render_template("history.html", history=utils.get_history())


@app.route("/history", methods=["POST"])
def del_history():
    utils.del_history()
    return redirect("/history")


@app.route("/audio/<path:filename>")
def send_media(filename):
    return send_file(utils.full_path(filename))


@app.teardown_appcontext
def close_connection(exception):
    database.close_db()


if __name__ == "__main__":
    utils.init()
    app.run(debug=True)
