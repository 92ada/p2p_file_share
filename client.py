import asyncio
import utils
from utils import TRACKER_IP, CHUNK_SIZE

class Client:
    def __init__(self, addr):
        self.loop = asyncio.get_event_loop()
        self.root = ''
        self.data_list = None
        self.reader, self.writer = await asyncio.open_connection(addr[0], addr[1], loop=loop)

    async def _send(self, message):
        while True:
            print('Send: %r' % message)
            self.writer.write(message.encode())

            data = await reader.read(100)
            print('Received: %r' % data.decode())

            if data.decode() == 'OK':
                break
        return data


    def _join(self):
        self.loop.run_until_complete(self._send('Join'))

    def _quit(self):
        self.loop.run_until_complete(self._send('Quit'))
        print('Close the socket')
        self.loop.close()

    def _query(self, seed):
        message = 'Query\n' + seed
        self.loop.run_until_complete(self._send(message))

    def _update(self, path):
        seed_list = [utils.make_big_seed(path) for path in utils.get_file_list(path)]
        message = 'Update\n' + '\n'.join(seed_list)
        self.loop.run_until_complete(self._send(message))

    def _reset(self):
        self.loop.run_until_complete(self._send('Reset'))
        self.loop.close()

    def get_response(self, message):
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

        if head_list[0] == 'List':
            pass

    def get_message(self, seed, id):
        message = 'Query\n' + str(id) + '\n'
        return message.encode() + seed


    async def serving(self):
        data = await reader.read(100)
        message = data.decode()
        print("Received %r from %r" % (message))
        addr = self.writer.get_extra_info('peername')

        response = self.get_response(message)
        print("Send: %r" % response)
        self.writer.write(response)
        await self.writer.drain()

        print("Close the client socket")
        self.writer.close()

    async def dispatch(self, addr_list, seed):
        file_len = seed.split('\n')[1]
        chunk_num = int((file_len-1)//CHUNK_SIZE + 1)
        for addr in addr_list:
            reader, writer = await asyncio.open_connection(addr[0], addr[1], loop=loop)
            writer.write(self.get_message())

        data = await reader.read(100)
        message = data.decode()
        print("Received %r from %r" % (message))
        addr = self.writer.get_extra_info('peername')

        response = self.get_response(message)
        print("Send: %r" % response)
        self.writer.write(response)
        await self.writer.drain()

        print("Close the client socket")
        self.writer.close()


    def download(self, seed):
        self.root = input('Please input a sharing path: ')
        loop = asyncio.get_event_loop()
        myip = utils.get_ip()
        coro = asyncio.start_server(self.serving, myip, 30031, loop=loop)

        # Serve requests until Ctrl+C is pressed
        print('Seeder Serving on {}'.format(server.sockets[0].getsockname()))
        self._join()
        self._update(self.root)
        # TODO: logic here need to be edit to correspond with the doc

        loop.run_until_complete(coro)
        try:
            loop.run_forever()
        except KeyboardInterrupt:
            pass


if __name__ == '__main__':
    seed = utils.make_seed('/Users/apple/p2p_file_share/.test.py')
    client = Client((TRACKER_IP, 30030))
    client.download(seed)
    # client.quit()
