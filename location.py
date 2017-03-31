class Location:
    def __init__(self, address, time_window):
        self.address = address
        self.time = time_window


if __name__ == "__main__":
    import doctest
    doctest.testmod()