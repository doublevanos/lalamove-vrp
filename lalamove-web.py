from flask import Flask, jsonify
from flask import make_response
from shipment import Shipment
from location import Location
from address import Address
import random

PICKUP = 1
DELIVERY = 2
MAX_DRIVERS = 2
MAX_DELIVERY = 5


app = Flask(__name__)

@app.errorhandler(404)
def not_found(error):
    return make_response(jsonify({'error': 'Not found'}), 404)

@app.route('/')
def hello_world():
    return 'Hello Lala!'

@app.route('/api/v1.0/orders', methods=['GET'])
def generate_orders():
    orders = []

    # Create random number of orders up to MAX_DELIVERY constant
    # Using i as the service type/name
    for i in range(0, random.randrange(1, MAX_DELIVERY)):
        orders.append(Shipment(str(i)))

    return jsonify({'Orders': orders})


if __name__ == '__main__':
    app.run()
