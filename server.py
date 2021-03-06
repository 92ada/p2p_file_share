import asyncio
import utils
from utils import TRACKER_IP, TRACKER_PORT, CHUNK_SIZE, UPDATE_INTERVAL
# from client /import download
import time 

class Server:
    def __init__(self, port):
        self.root = './file_set' # root directory of file list 
        self.tracker_addr = [TRACKER_IP, TRACKER_PORT]
        self.port = port 

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
    
    async def update_status(self, quit_flag=None):
        '''Update seeds to tracker '''
        while True:
            print("Update Start")
            reader, writer = await asyncio.open_connection(self.tracker_addr[0], self.tracker_addr[1])
            seed_list = [utils.make_seed(path) for path in utils.get_file_list(self.root)]
            message = 'Update '+ str(self.port)+"\n\n"
            print(len(seed_list))
            for i,seed in enumerate(seed_list):
                message += seed.decode() + '\n\n'
            print(message)
            writer.write(message.encode())
            await writer.drain()
            print("Update sent 3:{}".format(time.time()))
            data = await reader.read(100)
            print(data)
            writer.close()
            # break 
            if not quit_flag:
                await asyncio.sleep(UPDATE_INTERVAL)
            else:
                break 


def main():
    server = Server(30033)
    loop = asyncio.get_event_loop()
    coro = asyncio.start_server(server.dispatch, utils.get_ip(), server.port, loop=loop)
    sv = loop.run_until_complete(coro)

    task_update = asyncio.ensure_future(server.update_status())

    # seed = utils.make_seed('./README.md')
    # download(seed, "./")
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
