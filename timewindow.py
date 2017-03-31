import random
import time

class Timewindow:
    def __init__(self):
        self.hour = random.randrange(8,12)
        self.min = random.randrange(0,59,15)
        self.time_string = str(self.hour).zfill(2) + ":" + str(self.min).zfill(2) + ":00"
        self.time = int(time.mktime(time.strptime("1970 " + self.time_string, '%Y %H:%M:%S')))


    def unsigned_delta(self, t_time):
        """Computes the time delta between 2 time, ensuring the result is always > 0
        :param t_time: The time to find the delta with
        
        >>> t1 = Timewindow()
        >>> t2 = Timewindow()
        >>> t1.set_time(100000)
        >>> t2.set_time(90000)
        >>> print t2.unsigned_delta(t1) > 0
        True

        >>> t1.set_time(80000)
        >>> t2.set_time(110000)
        >>> print t2.unsigned_delta(t1) > 0
        True
        """
        if t_time.time > self.time:
            return t_time.time - self.time
        else:
            return self.time - t_time.time


    def delta(self, t_time):
        """Finds the time delta between 2 times.  The delta CAN be negative
        :param t_time: The time to find the delta with
        
        >>> t1 = Timewindow()
        >>> t2 = Timewindow()
        >>> t1t = t1.time
        >>> t2t = t2.time
        >>> t3 = t2.delta(t1)
        >>> t4 = t1t - t2t
        >>> print t3 == t4
        True
        """
        return t_time.time - self.time


    def add_time(self, seconds):
        """Adding N seconds to time
        :param seconds: Number of seconds to add
        
        >>> t1 = Timewindow()
        >>> t2 = t1.time
        >>> t1.add_time(300)
        >>> print t1.time - t2
        300
        """
        self.set_time(self.time+seconds)


    def set_time(self, itime):
        """Deploy new time to instance
        :param itme: Time in seconds since epoch
        
         >>> t1 = Timewindow()
         >>> t2 = t1.time
         >>> t1.set_time(t2+300)
         >>> print t1.time == (t2+300)
         True
         """
        self.time_string = time.strftime('%H:%M:%S', time.localtime(itime))
        self.hour = int(time.strftime('%H', time.localtime(itime)))
        self.min = int(time.strftime('%M', time.localtime(itime)))
        self.time = itime

if __name__ == "__main__":
    import doctest
    doctest.testmod()