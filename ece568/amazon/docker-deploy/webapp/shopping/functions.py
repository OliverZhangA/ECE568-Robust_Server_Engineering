import socket

def buyandpack(package_id):
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # use port 8888 to communicate with daemon
    client.connect(('127.0.0.1', 7777))
    # NOTE: append a \n at the end to become a line
    msg = str(package_id) + '\n'
    client.send(msg.encode('utf-8'))
    # expected response: ack:<package_id>
    data = client.recv(1024)
    data = data.decode()
    res = data.split(":")
    if res[0] == "ack" and res[1] == str(package_id):
        client.close()
        return True
    print('recv:', data)
    client.close()
    return False