from flask import Flask, jsonify
from flask import make_response
from flask_cors import CORS
from shipment import Shipment
from shipment import ShipmentJSONEncoder
from location import Location
from address import Address
import random
import threading

PICKUP = 1
DELIVERY = 2
MAX_DRIVERS = 2
MAX_DELIVERY = 5

app = Flask(__name__)
CORS(app)

orders = []
max_orders = 0
lock = threading.Lock();

@app.errorhandler(404)
def not_found():
    return make_response(jsonify({'error': 'Not found'}), 404)


@app.route('/')
def hello_world():
    return 'Hello LalaMove!'


@app.route('/favicon.ico')
def handle_favicon():
    return make_response(jsonify({'success': 'Found'}), 200)


@app.route('/api/v1.0/reset', methods=['GET'])
def reset():
    global orders
    global max_orders

    with lock:
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

    with lock:
        # Create random number of orders up to MAX_DELIVERY constant
        # Using i as the service type/name
        # We also only generate more orders if we have not hit the limit
        range_ceiling = MAX_DELIVERY+1 - len(orders)
        if range_ceiling > 1:
            for i in range(0, random.randrange(1, range_ceiling)):
                orders.append(Shipment(str(max_orders)))
                max_orders += 1
        else:
            print "Package limit reached"

    return jsonify(orders=orders)


@app.route('/api/v1.0/orders/remove', methods=['GET'])
def remove_random():
    global orders
    global max_orders

    with lock:
        if len(orders):
            order_id = random.randrange(0, len(orders))
            order = orders[order_id]
            orders.remove(order)
            return jsonify({'removed': order})
        else:
            return make_response(jsonify({'error': "Nothing to remove"}))


@app.route('/api/v1.0/orders/deliver', methods=['GET'])
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


@app.route('/api/v1.0/orders/route', methods=['GET'])
def delivery_route():
    global orders

    action = ['NULL','PICKUP','DELIVER']

    with lock:
        splits, sorted_orders = createShipmentSplit(orders)
        drivers = sendToDrivers(splits, sorted_orders)

    results = []
    d = 1
    for driver in drivers:
        dr = []
        time_overflow = 0
        for i in range(0, len(driver)):
            order = driver[i]

            # Calculating travel time, only if it's the second stop and beyond
            dist = 0
            dur = 0
            if i >= 1:
                dist, dur = order[1].address.dist(driver[i-1][1].address)
                time_window = order[1].time.time - driver[i-1][1].time.time
                if ((dur + time_overflow) > time_window):
                    time_overflow = dur - time_window
                else:
                    time_overflow = 0

            dr.append([{"ServiceType": order[0]},
                       {"Action": action[order[2]]},
                       {"Time": order[1].time.time_string},
                       {"Location": [
                            {"lat": order[1].address.lat},
                            {"lng": order[1].address.lng}]
                        },
                       {"Distance": dist},
                       {"TravelTime": dur},
                       {"Delayedby": time_overflow}])
        results.append({"driver": dr})
        d += 1

    return jsonify(results)


"""
 Functions to support API
"""


def createShipmentSplit(_orders):
    """ We order all the shipments by start, stop times.  Once ordered, this method will
    identify where in the list to split the shipments between the drivers
    """
    splitPoints = []
    t_orders = []

    # First, we order by pickup time and delivery time (but we can't use standard sort since we have 2 keys)
    for order in _orders:
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


def sendToDrivers(splits, _orders):
    """ Assigns orders to drivers
    
    :param splits: The list of split points
    :param _orders: All orders
    :return: List of drivers with packages assigned to each driver
    """
    drivers = [[] for i in range(len(splits)+1)]
    driver = 0

    # Assigning package to driver but also sorting it by time
    i = 0
    for order in _orders:
        j = 0
        while (j < len(drivers[driver]))\
            and order.pickup_time.time >= drivers[driver][j][1].time.time:
            j += 1
        drivers[driver].insert(j, [order.service_type,
                                   Location(order.pickup_loc,
                                            order.pickup_time),
                                   PICKUP])

        k = 0
        while (k < len(drivers[driver]))\
            and order.dropoff_time.time >= drivers[driver][k][1].time.time:
            k += 1
        drivers[driver].insert(k, [order.service_type,
                                   Location(order.dropoff_loc,
                                            order.dropoff_time),
                                   DELIVERY])

        if i in splits:
            driver += 1
        i += 1

    return drivers


app.json_encoder = ShipmentJSONEncoder
if __name__ == '__main__':
    app.run()
