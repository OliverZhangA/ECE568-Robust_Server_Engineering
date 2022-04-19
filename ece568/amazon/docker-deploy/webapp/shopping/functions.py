import socket
#import sys
from shopping.models import warehouse
import math

def match_warehouse(x, y):
    warehouses = warehouse.objects.all()
    nearestwh_id = 1
    #nearest_dist = sys.maxsize
    nearest_dist = 65536
    for wh in warehouses:
        dist = math.sqrt(math.pow(wh.pos_x - x, 2) + math.pow(wh.pos_y - y, 2))
        if dist < nearest_dist:
            nearest_dist = dist
            nearestwh_id = wh.id
    return nearestwh_id

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