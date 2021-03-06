import asyncio
import utils
from utils import TRACKER_PORT
from utils import UPDATE_INTERVAL
from seeder import Seeder
from torrent import Torrent, parse_torrent_str


class Tracker:
    seeder_list: dict
    torrent_list: {str: Torrent}

    def __init__(self):
        self.seeder_list = {}
        self.torrent_list = {}

    def response(self, message: str, addr) -> str:
        """ according to the request, response the requested resource or handle result """
        parts = message.split('\n\n')
        code = parts[0].split(' ')
        content = []
        for p in parts[1:]:
            if len(p):
                content.append(p)

        if code[0] == 'get_torrent_list':
            return self.get_torrent_list()
        elif code[0] == 'Update':
            if len(content) == 0:
                return 'No seed'
            if len(code) == 2:
                # get seeder port
                port = int(code[1])
            else:
                return 'Command Error'
            t_hash_list = []
            for t_str in content:
                # make a torrent object
                torrent = parse_torrent_str(t_str)
                t_hash_list.append(torrent.big_hash)
                # add torrent
                if torrent.big_hash not in self.torrent_list:
                    self.torrent_list[torrent.big_hash] = torrent
            self.seed_torrent_list(t_hash_list, (addr[0], port))  # register seeder
            print(self.torrent_list)
            return 'OK'
        elif code[0] == 'Query':
            if len(content) == 1:
                return self.return_seeder_list(content[0])
            else:
                return 'Command Error'
        else:
            return 'Command Error'

    async def dispatch(self, reader, writer):
        """ coroutine for receive and response request """
        data = await reader.read(10240)
        message = data.decode('utf-8')
        addr = writer.get_extra_info('peername')

        print(f'From {addr} received:\n{message}')
        response = self.response(message, addr)

        print(f'Response:\n{response}')
        writer.write(response.encode('utf-8'))
        await writer.drain()

        print("Close the client socket\n")
        writer.close()

    async def update_torrent_seeder(self):
        ''' After certain interval, check timestamp of all seeds to see if it's out of date (get del if out of date) '''
        while True:
            await asyncio.sleep(UPDATE_INTERVAL)
            print('update_torrent_seeder')
            for t in self.torrent_list.values():
                t.update_seeder_list()

    def run(self):
        """ start tracker using asyncio """
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
        ''' Return a list of torrent, each torrent is a string of torrent infrom '''
        torrent_list = ''
        for t in self.torrent_list.values():
            torrent_list += f'{t.big_hash} {t.size}\n'
        return torrent_list

    def seed_torrent_list(self, t_list: list, addr):
        ''' Periodically update status and file'''
        # parse torrent string

        for t_hash in t_list:
            if addr in self.seeder_list:
                seeder = self.seeder_list[addr]
            else:
                seeder = Seeder(addr)
                self.seeder_list[addr] = seeder
            if t_hash in self.torrent_list:
                torrent = self.torrent_list[t_hash]
            else:
                torrent = Torrent(t_hash)
                self.torrent_list[t_hash] = torrent

            torrent.update_seeder(seeder)

    def return_seeder_list(self, t_hash) -> str:
        """ get the seeder list of the torrent of t_hash """
        seeder_list = 'List\n'
        if t_hash in self.torrent_list:
            torrent = self.torrent_list[t_hash]
            for seeder in torrent.get_seeder_list():
                seeder_list += f'{seeder.addr[0]}:{seeder.addr[1]}\n'
        return seeder_list


def main():
    track = Tracker()
    track.run()


if __name__ == '__main__':
    main()
