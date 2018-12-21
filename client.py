import asyncio
import utils

class Client:
    def __init__(self):
        self.loop = asyncio.get_event_loop()

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
        loop.run_until_complete(self._send('Join', self.loop))

    def _quit(self):
        loop.run_until_complete(self._send('Quit', self.loop))
        print('Close the socket')
        loop.close()

    def _query(self, seed):
        message = 'Query\n' + seed
        loop.run_until_complete(self._send(message, self.loop))

    def _update(self, path):
        message = 'Update\n' + '\n'.join(utils.get_file_list(path))
        loop.run_until_complete(self._send(message, self.loop))

    def _reset(self):
        loop.run_until_complete(self._send('Reset', self.loop))
        loop.close()

    def _get_response(self, message, addr):
        # receive format:
        # str(block_id) + '\n' + seed_info


        # push format:
        # [first 4bytes: an unsigned int for the block id]
        #       if the first bit is 1, didn't find or refuse
        # [next 4bytes: checksum, an unsigned int]
        # [then: data]

        # TODO: add checksum
        pass

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
        self._update(path)

    def _receive(self):
        pass

    def download(self, seed):
        path = input('Please input a sharing path: ')
        self.serving(path)



if __name__ == '__main__':
    seed = utils.make_seed('#')
    client = Client()
    client.download(seed)
    # client.quit()
