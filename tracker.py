import asyncio
import utils
from utils import TRACKER_IP

class Tracker:
    def __init__(self):
        self.seeder_list = {}

    def response(self, message, addr) -> str:
        if message == 'Quit':
            self.seeder_list.pop(addr, None)
            return b'OK'

        elif message == 'Reset':
            self.seeder_list[addr] = set()
            return b'OK'

        else:
            message = message.split('\n')

            if message[0] == 'Join':
                addr = message[1]
                if addr in self.seeder_list.keys():
                    return b'OK'

                self.seeder_list[addr] = set()
                return b'OK'

            if message[0] == 'Update':
                addr = message[1]
                print(self.seeder_list)
                self.seeder_list[addr].update(message[2:])
                return b'OK'

            if message[0] == 'Query':
                big_hash = message[1]
                ret = ''
                for addr in self.seeder_list:
                    if big_hash in self.seeder_list[addr]:
                        ret += '\n' + addr
                return b'List' + ret.encode()

            return b'Error'

    async def dispatch(self, reader, writer):
        while True:
            data = await reader.read(4096)
            if data == b'': continue
            message = data.decode()
            addr = writer.get_extra_info('peername')
            response = self.response(message, addr)
            print("Received %r from %r" % (message, addr))
            print("Send: %r" % response)
            writer.write(response)
            await writer.drain()


def main():
    track = Tracker()
    loop = asyncio.get_event_loop()
    coro = asyncio.start_server(track.dispatch, TRACKER_IP, 30030, loop=loop)
    server = loop.run_until_complete(coro)

    # Serve requests until Ctrl+C is pressed
    print('Serving on {}'.format(server.sockets[0].getsockname()))
    try:
        loop.run_forever()
    except KeyboardInterrupt:
        pass

    # Close the server
    server.close()
    loop.run_until_complete(server.wait_closed())
    loop.close()


if __name__ == '__main__':
    main()
