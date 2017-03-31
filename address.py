import random
import json
import googlemaps


def loadfile():
    filename = "yelp_business_hk.txt"

    # Reading the file and combinging it
    f = open(filename, "r")
    json_data = []

    for data in f.readlines():
        json_data.append(json.loads(data)['businesses'])

    f.close()

    return json_data


class Address:
    # Static list of addresses.  There should behave like a singleton (static class variable)
    addresses = loadfile()

    # Googlemap API access key
    googlemaps_key = 'AIzaSyCaieaCXXG_j4mVKYpdMk9OUVS7VXWJ654'

    def __init__(self, iaddr=None):
        """Initilizing class instance
        :param iaddr: String representing a custom set address by the user.  If left blank, will default to None
            and the system will randomly pick one from the addresses list
        
        >>> a = Address()
        >>> print a.long, a.lat
        
        >>> a = Address('680 Folsom St, San Francisco, CA')
        >>> print a.long, a.lat
        -122.3985641 37.7845584
        
        """
        self.generate_addr(iaddr)

    def generate_addr(self, iaddr=None):
        """Generate a new address
        :param iaddr: String representing a custom set address by the user.  If left blank, will default to None
            and the system will randomly pick one from the addresses list
        
        Test with input address
        >>> lng01, lat01 = Address().generate_addr('680 Folsom St, San Francisco, CA')
        >>> print lng01, lat01
        -122.3985641 37.7845584
        
        Testing with random addrss
        >>> lng01, lat01 = Address().generate_addr()
        >>> print lng01, lat01
        """

        # If no address were specified

        if iaddr is None:
            line = random.randrange(0, len(self.addresses))
            addr = self.addresses[line][random.randrange(0, len(self.addresses[line]))]
            self.long = addr['coordinates']['longitude']
            self.lat = addr['coordinates']['latitude']
            self.addr = ",".join(addr['location']['display_address'])
        else:
            gmaps = googlemaps.Client(key=self.googlemaps_key)
            geocode = gmaps.geocode(iaddr)
            self.lat = geocode[0]['geometry']['location']['lat']
            self.long = geocode[0]['geometry']['location']['lng']
            self.addr = iaddr

        return self.long, self.lat

    def dist(self, t_addr, s_addr=None):
        """Calculate distance between *this* address and another provided
        :param t_addr: Target address object
        :param s_addr: Source address object, if blank will use current class instance address
        
        >>> dist01, dur01 = Address().dist(Address('680 folsom, san francisco, ca'), Address('115 sansome st, san francisco, ca'))
        >>> print dist01, dur01
        1861 479
        
        >>> dist02, dur02 = Address().dist(Address('G/F, Fu Fai Commercial Centre, 27 Hillier Street, hong kong'))  
        >>> print dist02, dur02  #doctest: +ELLIPSIS
        ... ...
        """
        gmaps = googlemaps.Client(key=self.googlemaps_key)

        if s_addr is None:
            lat01 = self.lat
            long01 = self.long
        else:
            lat01 = s_addr.lat
            long01 = s_addr.long

        directions = gmaps.directions(origin=(lat01, long01),
                                      destination=(t_addr.lat, t_addr.long))

        return directions[0]['legs'][0]['distance']['value'], \
               directions[0]['legs'][0]['duration']['value']

    def printAddresses(self):
        """ This method will print the address set in the current class instance
        """
        for i in range(0, len(self.addresses)):
            for store in self.addresses[i]:
                print store['name']
                print store['coordinates']
                print store['location']['display_address']

    def directions(self, t_addr, s_addr=None):
        """ Returns the directions, distance, leg, and travel-time between 2 addresses
        :param t_addr:  The target address
        :param s_addr:  The Source address, if left blank will use current instance address
        """
        gmaps = googlemaps.Client(key=self.googlemaps_key)

        if s_addr is None:
            lat01 = self.lat
            lng01 = self.long
        else:
            lat01 = t_saddr.lat
            lng01 = self.lng

        t_dirs = gmaps.directions(origin=(lat01,lng01),
                                  destination=(t_addr.lat, t_addr.long))

        if isinstance(t_dirs, list):
            dirs = t_dirs[0]['legs']
        else:
            dirs = t_dirs['legs']

        #for leg in self.directions:
        #    self.total_distance = self.total_distance + leg['distance']['value']
        #    self.total_duration = self.total_duration + leg['duration']['value']

        return dirs


if __name__ == "__main__":
    import doctest
    doctest.testmod()