import asyncio
import utils
from utils import TRACKER_PORT
from utils import UPDATE_INTERVAL
from seeder import Seeder
from torrent import Torrent


class Tracker:
    seeder_list: dict
    torrent_list: {str: Torrent}

    def __init__(self):
        self.seeder_list = {}
        self.torrent_list = {}

    def response(self, message: str, addr) -> str:
        lines = message.splitlines()
        cmd = lines[0].split()
        lines = lines[1:]

        if cmd[0] == 'get_torrent_list':
            return self.get_torrent_list()
        elif cmd[0] == 'seed_torrent_list':
            self.seed_torrent_list(lines, addr)
            return 'OK'
        elif cmd[0] == 'get_seeder_list':
            if len(cmd) == 2:
                return self.return_seeder_list(cmd[1])
            else:
                return 'Command Error'
        else:
            return 'Command Error'

    async def dispatch(self, reader, writer):
        data = await reader.read()
        message = data.decode('utf-8')
        addr = writer.get_extra_info('peername')

        response = self.response(message, addr)
        print("Received %r from %r" % (message, addr))

        print("Send: %r" % response)
        writer.write(response.encode('utf-8'))
        await writer.drain()

        print("Close the client socket\n")
        writer.close()

    async def update_torrent_seeder(self):
        while True:
            await asyncio.sleep(UPDATE_INTERVAL)
            print('update_torrent_seeder')
            for t in self.torrent_list.values():
                t.update_seeder_list()

    def run(self):
        loop = asyncio.get_event_loop()

        server_start = asyncio.start_server(self.dispatch, '', TRACKER_PORT, loop=loop)
        server = loop.run_until_complete(server_start)
        addr = server.sockets[0].getsockname()
        print(f'Serving on {addr}')

        # task1 = asyncio.ensure_future(server.serve_forever())
        task2 = asyncio.ensure_future(self.update_torrent_seeder())

        # Serve requests until Ctrl+C is pressed
        try:
            loop.run_forever()
        except KeyboardInterrupt:
            pass

        print('Server is closing...')
        # task1.cancel()
        server.close()
        task2.cancel()
        loop.run_until_complete(server.wait_closed())
        # while not task2.cancelled():
        #     loop.run_forever()
        loop.close()

    def get_torrent_list(self) -> str:
        torrent_list = ''
        for t in self.torrent_list.values():
            torrent_list += f'{t.name} {t.size}\n'
        return torrent_list

    def seed_torrent_list(self, t_list: list, addr):
        for t in t_list:
            if addr in self.seeder_list:
                seeder = self.seeder_list[addr]
            else:
                seeder = Seeder(addr)
                self.seeder_list[addr] = seeder
            self.torrent_list[t].update_seeder(seeder)

    def return_seeder_list(self, t_name) -> str:
        seeder_list = ''
        if t_name in self.torrent_list:
            torrent = self.torrent_list[t_name]
            for seeder in torrent.get_seeder_list():
                seeder_list += f'{seeder.addr}\n'
        return seeder_list


def main():
    track = Tracker()
    track.run()


if __name__ == '__main__':
    main()
