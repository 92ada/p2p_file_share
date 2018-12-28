from seeder import Seeder
from utils import UPDATE_INTERVAL
import time


class Torrent:
    name: str
    size: int
    big_hash: str
    seeder_list: dict

    def __init__(self, big_hash: str, name: str = None, size: int = None, chuck_hash: list = None):
        self.name = name
        self.size = size
        self.big_hash = big_hash
        self.chuck_hash = chuck_hash
        self.seeder_list = {}  # seeders register seeding this torrent

    def get_seeder_list(self) -> list:
        return list(self.seeder_list.keys())

    def update_seeder(self, seeder):
        self.seeder_list[seeder] = time.time()

    def update_seeder_list(self):
        """ remove out-of-date seeder """
        time_now = time.time()
        for key in self.seeder_list.keys():
            if self.seeder_list[key] + UPDATE_INTERVAL < time_now:
                self.seeder_list.pop(key)


def parse_torrent_str(t_str: str):
    t_lines = t_str.split('\n')
    name = t_lines[0]
    size = int(t_lines[1])
    big_hash = t_lines[2]
    chuck_hash = t_lines[3:]
    return Torrent(big_hash, name, size, chuck_hash)
