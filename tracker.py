import asyncio
import utils
from utils import TRACKER_IP

class Tracker:
    def __init__(self):
        self.seeder_list = {}

    def response(self, message, addr) -> str:
        if message == 'Join':
            if addr in self.seeder_list.keys():
                return b'OK'

            self.seeder_list[addr] = set()
            return b'OK'

        elif message == 'Quit':
            self.seeder_list.pop(addr, None)
            return b'OK'

        elif message == 'Reset':
            self.seeder_list[addr] = set()
            return b'OK'

        else:
            message = message.split('\n')

            if message[0] == 'Update':
                print(self.seeder_list)
                self.seeder_list[addr].update(message[1:])
                return b'OK'

            if message[0] == 'Query':
                big_seed = message[1]
                ret = ''
                for s in seeder_list:
                    if big_seed in seeder_list[s]:
                        ret += '\n' + s[0] + ':' + s[1]
                return b'List' + ret[1:].encode()

            return b'Error'

    async def dispatch(self, reader, writer):
        data = await reader.read(100)
        message = data.decode()
        addr = writer.get_extra_info('peername')

        response = self.response(message, addr)
        print("Received %r from %r" % (message, addr))

        print("Send: %r" % response)
        writer.write(response)
        await writer.drain()

        print("Close the client socket")
        writer.close()


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
