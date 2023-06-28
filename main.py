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


# Routes for setting up the plugin
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

# Routes used by the plugin
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
    app.run(debug=True, host='0.0.0.0', port=5010)