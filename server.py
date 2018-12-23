import asyncio
import utils
from utils import TRACKER_IP, CHUNK_SIZE

class Server:
    def __init__(self):
        self.root = '/Users/apple/p2p_file_share' # root directory of file list 

    def response(self, message) -> str:
        ''' Decode response message '''
        head, seed = message.split(b'\n\n')
        head_list = head.decode().split('\n')
        id = int(head_list[1])
        seed_path = utils.get_seed_path(self.root, seed, id)
        if seed_path == None:
            return b'Error'

        if head_list[0] == 'Test':
            return b'OK'

        if head_list[0] == 'Download':
            with open(seed_path, 'rb') as f:
                f.seek(id*CHUNK_SIZE)
                data = f.read(CHUNK_SIZE)
            head = 'Result\n' + str(id) + '\n\n'
            return head.encode() + data


    async def dispatch(self, reader, writer):
        while True:
            data = await reader.read(1024)
            if data == b'': continue
            addr = writer.get_extra_info('peername')
            response = self.response(data)
            print("Received %r from %r" % (data, addr))
            print("Send: %r" % response)
            writer.write(response)
            await writer.drain()
            break


def main():
    server = Server()
    loop = asyncio.get_event_loop()
    coro = asyncio.start_server(server.dispatch, utils.get_ip(), 30123, loop=loop)
    sv = loop.run_until_complete(coro)

    # Serve requests until Ctrl+C is pressed
    print('Serving on {}'.format(sv.sockets[0].getsockname()))
    try:
        loop.run_forever()
    except KeyboardInterrupt:
        pass

    # Close the server
    sv.close()
    loop.run_until_complete(sv.wait_closed())
    loop.close()


if __name__ == '__main__':
    main()
