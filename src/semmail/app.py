from dotenv import load_dotenv
from flask import Flask, jsonify, render_template_string, request

from .parser import interpret_email

load_dotenv()
app = Flask(__name__)


@app.route("/")
def home():
    """Just a dumb form where you can upload a file to the API"""

    return render_template_string(
        """
        <!DOCTYPE html>
        <html>
        <head>
            <title>Upload File</title>
        </head>
        <body>
        <h2>Upload File</h2>
        <form action="/upload" method="post" enctype="multipart/form-data">
            <input type="file" name="email_file">
            <input type="submit" value="Upload">
        </form>
        </body>
        </html>
    """
    )


@app.route("/upload", methods=["POST"])
def upload_file():
    """After a very basic validation of the file, we put it through the LLM
    so that we can know what it's about."""

    if "email_file" not in request.files:
        return jsonify({"error": "No file part"}), 400

    file = request.files["email_file"]

    if file.filename == "":
        return jsonify({"error": "No selected file"}), 400
    try:
        file_content = file.read()
        result = interpret_email(file_content)
        return jsonify(result), 200
    except ValueError as e:
        return jsonify({"error": str(e)}), 400


if __name__ == "__main__":
    app.run(debug=True)
