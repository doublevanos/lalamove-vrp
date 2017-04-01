from flask import Flask, jsonify
from flask import make_response
from shipment import Shipment
from shipment import ShipmentJSONEncoder
import random

PICKUP = 1
DELIVERY = 2
MAX_DRIVERS = 2
MAX_DELIVERY = 5

orders = []
max_orders = 0

app = Flask(__name__)

@app.errorhandler(404)
def not_found():
    return make_response(jsonify({'error': 'Not found'}), 404)


@app.route('/')
def hello_world():
    return 'Hello LalaMove!'


@app.route('/api/v1.0/reset', methods=['GET'])
def reset():
    global orders
    global max_orders

    del orders[:]
    max_orders = 0
    return make_response(jsonify({'success': 'App reset'}), 200)


@app.route('/api/v1.0/orders/list', methods=['GET'])
def list_all_orders():
    global orders
    return jsonify(orders=orders)


@app.route('/api/v1.0/orders/create', methods=['GET'])
def generate_orders():
    global orders
    global max_orders
    # First we purge the existing orders
    #    del orders[:]

    # Create random number of orders up to MAX_DELIVERY constant
    # Using i as the service type/name
    for i in range(0, random.randrange(1, MAX_DELIVERY-len(orders))):
        orders.append(Shipment(str(max_orders)))
        max_orders += 1

    return jsonify(orders=orders)


@app.route('/api/v1.0/orders/remove/', methods=['GET'])
def remove_random():
    global orders
    order_id = random.randrange(0, len(orders))
    order = orders[order_id]
    orders.remove(order)
    return jsonify({'removed': order})


@app.route('/api/v1.0/orders/remove/<string:service_type>', methods=['GET'])
def remove_order(service_type):
    for i in range(0, len(orders)):
        if orders[i].service_type == service_type:
            order = orders[i]
            orders.remove(order)
            return jsonify({'removed': order})

    return make_response(jsonify({'error': 'Not found'}), 404)


@app.route('/api/v1.0/orders/search/<string:service_type>', methods=['GET'])
def get_order(service_type):
    for i in range(0, len(orders)):
        if orders[i].service_type == service_type:
            return jsonify({'order': orders[i]})

    return make_response(jsonify({'error': 'Not found'}), 404)


app.json_encoder = ShipmentJSONEncoder
if __name__ == '__main__':
    app.run()
