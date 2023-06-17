from flask import Flask, request, jsonify, abort
from flask_cors import CORS
import os

app = Flask(__name__)
CORS(app)
BASE_DIR = 'D:/Code/GPT/'
YOUR_DIRECTORY_PATH = BASE_DIR + 'test/'
# YOUR_DIRECTORY_PATH = "ABC"
@app.route('/', methods=['GET'])
def list_files():
    print(YOUR_DIRECTORY_PATH)
    files = os.listdir(YOUR_DIRECTORY_PATH)
    # return jsonify({"ABC": "ABC"})
    return jsonify(files)

@app.route('/<path:filename>', methods=['GET', 'POST'])
def get_or_write_file(filename):
    file_path = os.path.join(YOUR_DIRECTORY_PATH, filename)

    if request.method == 'GET':
        if os.path.exists(file_path):
            with open(file_path, 'r') as file:
                content = file.read()
            return content
        else:
            abort(404, description="File not found")
    elif request.method == 'POST':
        data = request.data.decode('utf-8')  # assumes data is sent as text
        with open(file_path, 'w') as file:
            file.write(data)
        return f"Successfully wrote to {filename}"

if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0", port=5001)
