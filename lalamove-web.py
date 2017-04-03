from flask import Flask, jsonify
from flask import make_response
from flask_cors import CORS
from shipment import Shipment
from shipment import ShipmentJSONEncoder
from location import Location
from address import Address
import random

PICKUP = 1
DELIVERY = 2
MAX_DRIVERS = 2
MAX_DELIVERY = 5

orders = []
max_orders = 0

app = Flask(__name__)
CORS(app)

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
    global orders

    for i in range(0, len(orders)):
        if orders[i].service_type == service_type:
            order = orders[i]
            orders.remove(order)
            return jsonify({'removed': order})

    return make_response(jsonify({'error': 'Not found'}), 404)


@app.route('/api/v1.0/orders/search/<string:service_type>', methods=['GET'])
def get_order(service_type):
    global orders

    for i in range(0, len(orders)):
        if orders[i].service_type == service_type:
            return jsonify({'order': orders[i]})

    return make_response(jsonify({'error': 'Not found'}), 404)


@app.route('/api/v1.0/orders/deliver/', methods=['GET'])
def deliver_packages():
    global orders

    splits, sorted_orders = createShipmentSplit(orders)
    drivers = sendToDrivers(splits, sorted_orders)

    results = []
    for driver in drivers:
        dr = []
        for routes in driver:
            dr.append(routes[1].address)
        if (len(dr)):
            results.append({'driver': Address().directions_with_waypoints(dr)})

    return jsonify(results)


@app.route('/api/v1.0/orders/path/', methods=['GET'])
def delivery_route():
    global orders

    splits, sorted_orders = createShipmentSplit(orders)
    drivers = sendToDrivers(splits, sorted_orders)

    results = []
    d = 1
    for driver in drivers:
        dr = []
        for order in driver:
            dr.append([{"ServiceType": order[0]},
                       {"Action": order[2]},
                       {"Time": order[1].time.time_string},
                       {"Location": [
                            {"lat": order[1].address.lat},
                            {"lng": order[1].address.lng}]
                        }])
        results.append({"driver": dr})
        d += 1

    return jsonify(results)


"""
 Functions to support API
"""

def createOrder(order):
    """ This method actually creates the order object that is handed off to the driver
    :param order: The order to be pickedup and delivered
    :return orders: A new list of orders where pickup/dropoff are just stops
    """
    orders = []
    orders.append([order.service_type,
                   Location(order.pickup_loc,
                            order.pickup_time),
                   PICKUP])
    orders.append([order.service_type,
                   Location(order.dropoff_loc,
                            order.dropoff_time),
                   DELIVERY])
    return orders


def getTime(order):
    """ Small operator function to assist in sorting
    """
    return order[1].time.time


def createShipmentSplit(orders):
    """ We order all the shipments by start, stop times.  Once ordered, this method will
    identify where in the list to split the shipments between the drivers
    """
    splitPoints = []
    t_orders = []

    # First, we order by pickup time and delivery time (but we can't use standard sort since we have 2 keys)
    for order in orders:
        i = 0
        while i < len(t_orders) \
                and order.pickup_time.time > t_orders[i].pickup_time.time:
            i += 1

        # If startime is equal
        while i < len(t_orders) \
                and order.pickup_time.time == t_orders[i].pickup_time.time \
                and order.dropoff_time.time > t_orders[i].dropoff_time.time:
            i += 1

            # I create a split point when start times are equal
            if (len(splitPoints) < MAX_DRIVERS-1):
                splitPoints.append(i)

        t_orders.insert(i, order)

    if MAX_DRIVERS > 1 and len(splitPoints) < MAX_DRIVERS-1:
        # Try to find a where to split the routes between 2 drivers.
        # Decided on a very simple approach, if there's 2 pick up points where the travel time exceeds the time window,
        # I split it here.
        for order_idx in range(0, len(t_orders)-1):
            dist, dur = t_orders[order_idx].pickup_loc.dist(t_orders[order_idx+1].pickup_loc)
            time_delta = t_orders[order_idx+1].pickup_time.time - t_orders[order_idx].pickup_time.time

            # Make sure time is always positive
            if time_delta < 0:
                time_delta *= -1

            if len(splitPoints) < MAX_DRIVERS-1 and dur >= time_delta:
                splitPoints.append(order_idx)

    if MAX_DRIVERS > 1 and len(splitPoints) < MAX_DRIVERS-1:
        splitPoints.append(int(len(t_orders)/2)-1)

    return splitPoints, t_orders


def sendToDrivers(splits, orders):
    """ Assigns orders to drivers
    
    :param splits: The list of split points
    :param orders: All orders
    :return: List of drivers with packages assigned to each driver
    """
    drivers = [[] for i in range(len(splits)+1)]
    driver = 0

    for i in range(0, len(orders)):
        drivers[driver] += createOrder(orders[i])
        if i in splits:
            driver += 1

    # Order the pickup and drop offs
    for driver in drivers:
        driver.sort(key=getTime)

    return drivers


app.json_encoder = ShipmentJSONEncoder
if __name__ == '__main__':
    app.run()
