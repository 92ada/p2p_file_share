import asyncio
import utils
from utils import TRACKER_IP, CHUNK_SIZE

class Client:
    def __init__(self):
        self.loop = asyncio.get_event_loop()
        self.root = ''
        self.data_list = None

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
        # query format (notice: convert to bytes):
        # str('Query\n') + str(chunk_id) + '\n' + seed_info

        head, data = message.split(b'\n\n')
        head_list = head.decode().split('\n')
        if head_list[0] == 'Query':
            chunk_id = int(head_list[1])
            seed = head_list[2]
            seed_path = utils.get_seed_path(self.root, seed, chunk_id)
            if seed_path == None:
                head = 'Result\n' + str(-1)
                return head.encode()

            data = open(path, 'rb').read()
            push_data = data[chunk_id*CHUNK_SIZE:(chunk_id+1)*CHUNK_SIZE]
            head = 'Result\n' + str(chunk_id) + '\n\n'
            return head.encode() + push_data

        # response format:
        # str('Result\n') + str(chunk_id) + '\n\n' + [bytes data]
        # if chunk_id == -1, data not found or refused

        if head_list[0] == 'Result':
            chunk_id = int(head_list[1])










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
        self._join()
        self._update(self.root)
        # TODO: logic here need to be edit to correspond with the doc
        try:
            loop.run_forever()
        except KeyboardInterrupt:
            pass

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
