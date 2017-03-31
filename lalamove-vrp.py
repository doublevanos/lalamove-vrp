from shipment import Shipment
from location import Location
from address import Address
import random


PICKUP = 1
DELIVERY = 2
MAX_DRIVERS = 2
MAX_DELIVERY = 5


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


def removeOrderFromDriver(service_type, drivers):
    """ Removing an order from the list.
    :param service_type: Name of the order, this is the key
    :param drivers: List of drivers
    """

    # iterate through all the driver's packages
    for driver in drivers:

        # We need to loop twice in removing the package since there's pickup and dropoff
        for i in range(0,2):

            # For each driver, look for the package
            for order in driver:
                if order[0] == service_type:
                    driver.remove(order)
                    break


def removeOrder(service_type, orders):
    """ Removes an order from the orders
    :param service_type: Name of the order, this is the key
    :param orders: List of all orders
    """
    # We need to loop twice in removing the package since there's pickup and dropoff
    for i in range(0,2):

        # For each driver, look for the package
        for order in orders:
            if order.service_type == service_type:
                orders.remove(order)
                break


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
                and order.pickup_time.time == t_orders[i].pickup_time.time\
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


def printOrders(drivers):
    """
    Print the orders and delivery order
    :param drivers: Drivers and their packages
    :return: 
    """
    stops = 0
    i = 0
    for driver in drivers:
        stops += len(driver)
        print "Driver " + str(i+1) + ":",
        j = 0
        for order in driver:
            print "Service " + order[0],
            if order[2] == PICKUP:
                print ": Pickup (",
            else:
                print ": Deliver (",
            print order[1].time.time_string + " ) ",
            if j < len(driver)-1:
                print "--",
                dist, dur = Address().dist(drivers[i][j][1].address,
                                           drivers[i][j+1][1].address)
                print str(int(dur/60)) + " --> ",
            j = j + 1
        print ""
        i = i + 1

    print "Total Shipments: " + str(int(stops/2))
    print ""



def main():
    orders = []

    # Create random number of orders up to MAX_DELIVERY constant
    # Using i as the service type/name
    for i in range(0, random.randrange(1, MAX_DELIVERY)):
    #for i in range(0, MAX_DELIVERY):
        orders.append(Shipment(str(i)))

    splits, sorted_orders = createShipmentSplit(orders)
    drivers = sendToDrivers(splits, sorted_orders)
    printOrders(drivers)

    # Remove a package
    #removeOrder('0', drivers)
    removeOrder('0', orders)
    splits, sorted_orders = createShipmentSplit(orders)
    drivers = sendToDrivers(splits, sorted_orders)
    printOrders(drivers)


if __name__ == '__main__':
    main()


