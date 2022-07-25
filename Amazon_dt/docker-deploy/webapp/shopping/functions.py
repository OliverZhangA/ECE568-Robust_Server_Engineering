from http import client
import socket
#import sys
from shopping.models import warehouse
import math

def match_warehouse(x, y):
    warehouses = warehouse.objects.all()
    nearestwh_id = 1
    #nearest_dist = sys.maxsize
    nearest_dist = 2147483647
    for wh in warehouses:
        dist = math.sqrt(math.pow(wh.pos_x - x, 2) + math.pow(wh.pos_y - y, 2))
        if dist < nearest_dist:
            nearest_dist = dist
            nearestwh_id = wh.id
    return nearestwh_id

def buyandpack(package_id):
    toback_end = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    toback_end.connect(('daemon', 7777))
    # toback_end.connect(('127.0.0.1', 7777))
    data_tobackend = str(package_id) + '\n'
    toback_end.send(data_tobackend.encode('utf-8'))
    toback_end.close()
    return
