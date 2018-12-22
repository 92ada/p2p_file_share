import asyncio
import utils
from utils import TRACKER_IP, CHUNK_SIZE

class Client:
    def __init__(self):
        self.loop = asyncio.get_event_loop()
        self.root = ''

    async def _send(self, message, loop):
        reader, writer = await asyncio.open_connection(TRACKER_IP, 30030,
                                                       loop=loop)

        while True:
            print('Send: %r' % message)
            writer.write(message.encode())

            data = await reader.read(100)
            print('Received: %r' % data.decode())

            if data.decode() == 'OK':
                break

        writer.close()
        return data


    def _join(self):
        self.loop.run_until_complete(self._send('Join', self.loop))

    def _quit(self):
        self.loop.run_until_complete(self._send('Quit', self.loop))
        print('Close the socket')
        self.loop.close()

    def _query(self, seed):
        message = 'Query\n' + seed
        self.loop.run_until_complete(self._send(message, self.loop))

    def _update(self, path):
        message = 'Update\n' + '\n'.join(utils.get_file_list(path))
        self.loop.run_until_complete(self._send(message, self.loop))

    def _reset(self):
        self.loop.run_until_complete(self._send('Reset', self.loop))
        self.loop.close()

    def _get_response(self, message, addr):
        # receive format:
        # str(CHUNK_id) + '\n' + seed_info
        CHUNK_id, seed_info = message.decode().split('\n')
        seed_path = utils.get_seed_path(self.root, seed_info)
        if seed_path == None:
            return b'\xff\xff\xff\xff'

        data = open(path, 'rb').read()
        push_data = data[CHUNK_id*CHUNK_SIZE:(CHUNK_id+1)*CHUNK_SIZE]
        # checksum = utils.get_checksum(push_data)
        ret = utils.int_to_four_bytes(CHUNK_id)
        ret += utils.int_to_four_bytes(CHUNK_id)
        ret += push_data

        # push format:
        # [first 4bytes: an unsigned int for the CHUNK id]
        #       if all bits are 1, didn't find or refuse
        # [then: data]
        return ret

    async def dispatch(self, path, range: tuple):
        data = await reader.read(100)
        message = data.decode()
        addr = writer.get_extra_info('peername')

        response = self._get_response(message, addr)
        print("Received %r from %r" % (message, addr))

        print("Send: %r" % response)
        writer.write(response.encode())
        await writer.drain()

        print("Close the client socket")
        writer.close()

    def serving(self):
        loop = asyncio.get_event_loop()
        myip = utils.get_ip()
        coro = asyncio.start_server(self.dispatch, myip, 30031, loop=loop)
        server = loop.run_until_complete(coro)

        # Serve requests until Ctrl+C is pressed
        print('Seeder Serving on {}'.format(server.sockets[0].getsockname()))
        try:
            loop.run_forever()
        except KeyboardInterrupt:
            pass
        self._join()
        # TODO: edit the logic to tell tracker servering addr
        # addr format: str(ip)+':'+str(port)
        self._update(self.root)

    def _receive(self):
        pass

    def download(self, seed):
        self.root = input('Please input a sharing path: ')
        self.serving()



if __name__ == '__main__':
    seed = utils.make_seed('/Users/apple/p2p_file_share/.test.py')
    client = Client()
    client.download(seed)
    # client.quit()
