import asyncio
import utils
from utils import TRACKER_IP

class Tracker:
    def __init__(self):
        self.seeder_list = {}

    def response(self, message, addr) -> str:
        if message == 'Join':
            if addr in self.seeder_list.keys():
                return 'OK'

            self.seeder_list[addr] = set()
            return 'OK'

        elif message == 'Quit':
            self.seeder_list.pop(addr, None)
            return 'OK'

        elif message == 'Reset':
            self.seeder_list[addr] = set()
            return 'OK'

        else:
            message = message.split('\n')

            if message[0] == 'Update':
                self.seeder_list[addr].update(message[1:])
                return 'OK'

            if message[0] == 'Query':
                seed = message[1]
                ret = []
                for s in seeder_list:
                    if seed in seeder_list[s]:
                        ret.append(s)
                return ret

            return 'Error'

    async def dispatch(self, reader, writer):
        data = await reader.read(100)
        message = data.decode()
        addr = writer.get_extra_info('peername')

        response = self.response(message, addr)
        print("Received %r from %r" % (message, addr))

        print("Send: %r" % response)
        writer.write(response.encode())
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
