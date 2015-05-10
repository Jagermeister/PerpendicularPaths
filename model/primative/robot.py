class Robot (object):
    name = ""
    value = 0

    def __init__ (self, name, value):
        assert isinstance(name, str)
        self.name = name
        assert isinstance(value, int)
        self.value = value

    def __str__ (self):
        return self.name

 	#TODO: This should not know about display
    def bgcolor (self):
        if self.value == 0b00010000:
            return 0x0040
        elif self.value == 0b00100000:
            return 0x0010
        elif self.value == 0b01000000:
            return 0x0060
        elif self.value == 0b10000000:
            return 0x0020

    def fgcolor (self):
        if self.value == 0b00010000:
            return 12
        elif self.value == 0b00100000:
            return 9
        elif self.value == 0b01000000:
            return 14
        elif self.value == 0b10000000:
            return 10