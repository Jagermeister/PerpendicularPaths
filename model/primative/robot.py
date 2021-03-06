import os

class Robot(object):
    name = ""
    value = 0

    def __init__(self, name, value):
        assert isinstance(name, str)
        assert len(name) > 0
        self.name = name
        assert isinstance(value, int)
        self.value = value
        
    def __str__(self): 
        """debug output of name"""
        return self.name.rjust(6)

    def __deepcopy__(self, memo):
        return self

 	#TODO: This should not know about display
    def bgcolor(self):
        if self.value == 0b00010000:
            return 0x0040 if os.name == 'nt' else 41
        elif self.value == 0b00100000:
            return 0x0010 if os.name == 'nt' else 46
        elif self.value == 0b01000000:
            return 0x0060 if os.name == 'nt' else 43
        elif self.value == 0b10000000:
            return 0x0020 if os.name == 'nt' else 42

    def fgcolor(self):
        if self.value == 0b00010000:
            return 12 if os.name == 'nt' else 31
        elif self.value == 0b00100000:
            return 9 if os.name == 'nt' else 36
        elif self.value == 0b01000000:
            return 14 if os.name == 'nt' else 33
        elif self.value == 0b10000000:
            return 10 if os.name == 'nt' else 32

    def rgbcolor(self):
        if self.value == 0b00010000:
            return (255,0,0)
        elif self.value == 0b00100000:
            return (0,0,255)
        elif self.value == 0b01000000:
            return (255,255,0)
        elif self.value == 0b10000000:
            return (0,255,0)
