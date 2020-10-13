from flask import Flask, request, jsonify
from flask_cors import CORS
import json

app = Flask(__name__)
CORS(app)


@app.route('Backend/parser', methods=['POST'])
def parse_resume():
    if request.method == 'POST':
        # TODO: Send request.json to handler
        pass
    return jsonify(Error="Method not allowed")


if __name__ == '__main__':
    app.run()
