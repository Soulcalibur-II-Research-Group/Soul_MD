class Credit(object):
    def __init__(self):
        self.day = 0
        self.month = 0
        self.year = 0
        self.sec = 0
        self.min = 0
        self.hour = 0
        self.name = ''
    def read(self,f):
        self.day = f.u8()
        self.month = f.u8()
        self.year = f.u16()

        self.sec = f.u8()
        self.min = f.u8()
        self.hour = f.u8()
        f.u8()
        precrd = f.read(0x20)
        self.name = precrd.decode('shift_jis')
