'''
this is a local messenger.
it uses sockets to communicate with other users on the same network without the need for a server.
Do not change the port if you want to use this program with other users.
This program doesn't implement encryption, so don't use it for anything sensitive. Avoid strong profanity.
'''
import socket
import sys
import threading
import time
from scapy.layers.l2 import Ether, ARP, srp

users_online = []
clients = []


def arp(ip):
    arps = ARP(pdst=ip)
    eth = Ether(dst="ff:ff:ff:ff:ff:ff")
    packet = eth / arps
    result = srp(packet, timeout=3, verbose=0)[0]
    for sent, received in result:
        clients.append(received.psrc)
        # remove broadcast address from clients
        if '255' in received.psrc:
            clients.remove(received.psrc)
    return clients


# send a packet to all IPs in clients without broadcasting
def sendall():
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    while True:
        time.sleep(10)
        for client in clients:
            try:
                s.sendto(f'2510c39011c5be704182423e3a695e91: {uname}'.encode('utf-8'), (client, 55565))
                print(f'sent to {client}')
            except:
                pass


def generate_ip():
    ips = socket.gethostbyname(socket.gethostname()).split('.')
    ips[3] = '0/24'
    return '.'.join(ips)


def receivemsg():
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind((socket.gethostbyname(socket.gethostname()), 55565))
    #s.bind(('localhost', 55565))
    s.listen(5)
    while True:
        try:
            conn, addr = s.accept()
            data = conn.recv(1024).decode("utf-8")
            if '2510c39011c5be704182423e3a695e91: ' in data:
                data = data.replace('2510c39011c5be704182423e3a695e91: ', '')
                if data not in users_online:
                    # append the username and the ip address to the users_online list
                    users_online.append({data: addr[0]})
                print(data + ' has connected')
            # check if IP is in the online users list, if it is, print the username associated along with the message
            elif addr[0] in [list(user.values())[0] for user in users_online]:
                for user in users_online:
                    if addr[0] == list(user.values())[0]:
                        print(list(user.keys())[0] + ': ' + data)
        except:
            pass


print('Welcome to Local Messenger! Please type help for a list of commands.')
threading.Thread(target=receivemsg).start()
uname = input('Please enter a username: ')
threading.Thread(target=sendall).start()
threading.Thread(target=arp, args=(generate_ip(),)).start()

while True:
    inp = input('>> ')
    if inp == 'help':
        print('help - show this message')
        print('list - list all users on the network')
        print('msg <user> <message> - send a message to a user. By default you are sending to the global pool.')
        print('exit - exit the program')
        print('DEBUG COMMAND listarp - list collected ARP information')

    elif inp == 'list':
        print('Active Users: ')
        for user in users_online:
            print(user)

    elif inp == 'exit':
        sys.exit()

    elif inp.startswith('msg'):
        us = inp.split(' ')[1]
        msg = inp.split(' ')[2:]
        msg = ' '.join(msg)
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        for user in users_online:
            if user[0] == us:
                s.sendto(f'{us}: {msg}'.encode('utf-8'), (user[1], 55565))
                s.close()

    elif inp == 'listarp':
        print(clients)

    else:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        for user in users_online:
            s.sendto(inp.encode('utf-8'), (user[1], 55565))
            s.close()
