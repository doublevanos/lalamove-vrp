import address
import timewindow

TIME_WINDOW = 45*60

class Shipment:
    total_distance = 0
    total_duration = 0

    def __init__(self, _service_type):
        """
        Initilizes a shipment
        
        :param _service_type: Name of the service
        """
        self.service_type = _service_type
        self.pickup_loc = address.Address()
        self.dropoff_loc = address.Address()
        self.pickup_time = timewindow.Timewindow()
        self.dropoff_time = timewindow.Timewindow()

        # Makes sure dropoff time occurs after pickup time
        if self.pickup_time.time > self.dropoff_time.time:
            t = self.dropoff_time
            self.dropoff_time = self.pickup_time
            self.pickup_time = t

        # Makes sure there's at least a TIME_WINDOW between pickup and delivery
        if self.dropoff_time.time - self.pickup_time.time < TIME_WINDOW:
            self.dropoff_time.add_time(TIME_WINDOW - (self.dropoff_time.time - self.pickup_time.time))

        self.directions = self.dropoff_loc.directions(self.pickup_loc)
        self.total_distance = self.directions[0]['distance']['value']
        self.totol_duration = self.directions[0]['duration']['value']


if __name__ == "__main__":
    import doctest
    doctest.testmod()