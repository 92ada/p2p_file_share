import asyncio
import utils
from utils import TRACKER_IP, CHUNK_SIZE
from threading import Thread
import time

class Client:
    def __init__(self, addr):
        self.tracker_addr = addr
        self.addr_list = []
        self.seed = None
        self.data = None
        # self.root = input('Please input your share path: ')
        self.root = '/Users/apple/p2p_file_share'
        self.serve_port = 30123

    def get_message(self, code, chunk_id=None):
        if code == 'Join':
            ret = 'Join\n' + utils.get_ip() + ':' + str(self.serve_port)
            return ret.encode()

        if code == 'Update':
            seed_list = [utils.make_big_hash(path) for path in utils.get_file_list(self.root)]
            message = 'Update\n' + utils.get_ip() + ':' + str(self.serve_port) \
                        + '\n' + '\n'.join(seed_list)
            return message.encode()

        if code == 'Query':
            big_hash = self.seed.split(b'\n')[2]
            return b'Query\n' + big_hash

        if code == 'Test' or 'Download':
            # format: 'Test\n' + str(id) + '\n' + seed
            ret = code + '\n' + str(chunk_id) + '\n\n'
            return ret.encode() + self.seed


    def get_response(self, message):
        pass

    async def produce(self, queue):
        # open the connection to tracker
        reader, writer = await asyncio.open_connection(self.tracker_addr[0], self.tracker_addr[1])

        while True:
            writer.write(self.get_message('Join'))
            await writer.drain()
            data = await reader.read(100)
            if data == b'OK': break

        while True:
            writer.write(self.get_message('Update'))
            await writer.drain()
            data = await reader.read(100)
            if data == b'OK': break

        while True:
            writer.write(self.get_message('Query'))
            await writer.drain()
            data = await reader.read(100)
            message = data.decode().split('\n')
            if message[0] == 'List':
                addr_list = message[1:]
                break

        writer.close()
        await writer.wait_closed()

        for addr in addr_list:
            # produce an item
            print('add {} to the queue'.format(addr))
            await queue.put(addr)

        # indicate the producer is done
        await queue.put(None)


    async def consume(self, queue):
        while True:
            # wait for an item from the producer
            addr = await queue.get()
            print("in consume", addr)
            if addr is None: continue
            ip, port = addr.split(':')
            reader, writer = await asyncio.open_connection(ip, port)

            writer.write(self.get_message('Test', -1))
            await writer.drain()
            print("Send Test")
            data = await reader.read(100)
            print(data)
            if data == b'OK':
                print("Received OK")
                self.addr_list.append((ip, port))
            break

    async def _download(self, addr, id):
        reader, writer = await asyncio.open_connection(addr[0], addr[1])
        writer.write(self.get_message('Download', id))
        await writer.drain()
        message = await reader.read(1024)
        head, data = message.split(b'\n\n', 1)
        head_list = head.decode().split('\n')
        if head_list[0] == 'Result':
            self.data[int(head_list[1])] = data
        else:
            print('Chunk #{} download failed', id)



    def download(self, seed):
        self.seed = seed
        loop = asyncio.get_event_loop()
        queue = asyncio.Queue(loop=loop)
        producer_coro = self.produce(queue)
        consumer_coro = self.consume(queue)
        loop.run_until_complete(asyncio.gather(producer_coro, consumer_coro))

        print('Get accessible addr list: ')
        print(self.addr_list)

        addr_num = len(self.addr_list)
        if addr_num == 0:
            print('Download failed.')
            return

        tasks = []
        file_len = seed.decode().split('\n')[1]
        chunk_num = (int(file_len)-1)//CHUNK_SIZE + 1
        self.data = [None] * chunk_num
        for id in range(chunk_num):
            tasks.append(self._download(self.addr_list[id%addr_num], id))
        loop.run_until_complete(asyncio.wait(tasks))
        loop.close()
        print(self.data)


if __name__ == '__main__':
    seed = utils.make_seed('/Users/apple/p2p_file_share/README.md')
    client = Client((TRACKER_IP, 30030))
    client.download(seed)
    # client.quit()
