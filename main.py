from flask import Flask, Response, request, jsonify, abort
from flask_cors import CORS
import os
import json
import fnmatch
import subprocess
from flask.json import JSONEncoder

class CustomJSONEncoder(JSONEncoder):
    def default(self, obj):
        try:
            return super().default(obj)
        except TypeError:
            return str(obj)

app = Flask(__name__)
CORS(app)
app.json_encoder = CustomJSONEncoder

IGNORE_FILE = 'D:/Code/GPT/.GPTignore'
BASE_DIR = 'D:/Code/GPT/'
YOUR_DIRECTORY_PATH = BASE_DIR

@app.route('/', methods=['GET'])
def list_files():
    with open(IGNORE_FILE, 'r') as f:
        ignore_patterns = f.read().splitlines()
    return jsonify(list_files_dirs(YOUR_DIRECTORY_PATH, ignore_patterns))

def list_files_dirs(path, ignore_patterns):
    response = {'files': [], 'directories': []}
    for root, dirs, files in os.walk(path):
        dirs[:] = [d for d in dirs if not any(fnmatch.fnmatch(d, pattern) for pattern in ignore_patterns)]
        for file in files:
            if not any(fnmatch.fnmatch(file, pattern) for pattern in ignore_patterns):
                response['files'].append(os.path.join(root, file))
        for dir in dirs:
            response['directories'].append(os.path.join(root, dir))
    return response

@app.route('/<path:filename>', methods=['GET', 'POST', 'DELETE'])
def get_or_write_file(filename):
    file_path = os.path.join(YOUR_DIRECTORY_PATH, filename)
    if request.method == 'GET':
        if os.path.exists(file_path):
            with open(file_path, 'r') as file:
                content = file.read()
            return content
        else:
            abort(404, description='File not found')
    elif request.method == 'POST':
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        data = request.data.decode('utf-8')  # assumes data is sent as text
        with open(file_path, 'w') as file:
            file.write(str(json.loads(data)['content']))
        return f'Successfully wrote to {filename}'
    elif request.method == 'DELETE':
        if os.path.exists(file_path):
            os.remove(file_path)
            return f'Successfully deleted {filename}'
        else:
            abort(404, description='File not found')

@app.route('/.well-known/ai-plugin.json', methods=['GET'])
def plugin_manifest():
    host = request.headers.get('Host')
    with open('./.well-known/ai-plugin.json') as f:
        text = f.read()
        return Response(text, mimetype='text/json')

@app.route('/api.yaml', methods=['GET'])
def openapi_spec():
    host = request.headers.get('Host')
    with open('api.yaml') as f:
        text = f.read()
        return Response(text, mimetype='text/yaml')

@app.route('/cli', methods=['POST'])
def cli():
    command = request.json.get('command')
    process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
    stdout, stderr = process.communicate()
    return jsonify({'stdout': stdout.decode('utf-8'), 'stderr': stderr.decode('utf-8')})

@app.route('/execute', methods=['POST'])
def execute():
    code = request.json.get('code')
    exec_globals = {}
    exec_locals = {}
    exec(code, exec_globals, exec_locals)
    return jsonify(exec_locals)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5001)