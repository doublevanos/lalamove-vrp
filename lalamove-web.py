from flask import Flask, jsonify
from flask import make_response

app = Flask(__name__)

@app.errorhandler(404)
def not_found(error):
    return make_response(jsonify({'error': 'Not found'}), 404)

@app.route('/')
def hello_world():
    return 'Hello Lala!'

#@app.route('/api/v1.0/')
#def


if __name__ == '__main__':
    app.run()
