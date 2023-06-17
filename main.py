from quart import Quart, request, jsonify, abort
from quart_cors import cors
import os

app = Quart(__name__)
app = cors(app, allow_origin="https://chat.openai.com")

BASE_DIR = 'D:/Code/GPT/'
YOUR_DIRECTORY_PATH = BASE_DIR + 'test/'

@app.route('/', methods=['GET'])
async def list_files():
    print(YOUR_DIRECTORY_PATH)
    files = os.listdir(YOUR_DIRECTORY_PATH)
    return jsonify(files)

@app.route('/<path:filename>', methods=['GET', 'POST'])
async def get_or_write_file(filename):
    file_path = os.path.join(YOUR_DIRECTORY_PATH, filename)

    if request.method == 'GET':
        if os.path.exists(file_path):
            with open(file_path, 'r') as file:
                content = file.read()
            return content
        else:
            abort(404, description="File not found")
    elif request.method == 'POST':
        data = await request.get_data()  # get_data() is an async function in Quart
        data = data.decode('utf-8')
        with open(file_path, 'w') as file:
            file.write(data)
        return f"Successfully wrote to {filename}"

if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0", port=5001)
