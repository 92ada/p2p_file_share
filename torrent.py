from seeder import Seeder
from utils import UPDATE_INTERVAL
import time


class Torrent:
    name: str
    size: int
    seeder_list: dict

    def __init__(self, name: str, size: int):
        self.name = name
        self.size = size
        self.seeder_list = {}

    def get_seeder_list(self) -> list:
        return list(self.seeder_list.keys())

    def update_seeder(self, seeder):
        self.seeder_list[seeder] = time.time()

    def update_seeder_list(self):
        time_now = time.time()
        for key in self.seeder_list.keys():
            if self.seeder_list[key] + UPDATE_INTERVAL < time_now:
                self.seeder_list.pop(key)
