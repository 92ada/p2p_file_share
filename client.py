import asyncio
import utils

class Client:
    def __init__(self):
        self.loop = asyncio.get_event_loop()

    async def send(self, message, loop):
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


    def join(self):
        loop.run_until_complete(self.send('Join', self.loop))

    def quit(self):
        loop.run_until_complete(self.send('Quit', self.loop))
        print('Close the socket')
        loop.close()

    def query(self, seed):
        message = 'Query\n' + seed
        loop.run_until_complete(self.send(message, self.loop))

    def update(self, path):
        message = 'Update\n' + '\n'.join(utils.get_file_list(path))
        loop.run_until_complete(self.send(message, self.loop))

    def reset(self):
        loop.run_until_complete(self.send('Reset', self.loop))
        loop.close()


if __name__ == '__main__':
    client = Client()
    message = 'Join'
    loop = asyncio.get_event_loop()
    client.join()
    # client.quit()
