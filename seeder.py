class Seeder:
    addr: str

    def __init__(self, addr=None):
        self.addr = addr

    def set_addr(self, addr):
        self.addr = addr
