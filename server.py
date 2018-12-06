import sys
import socket
import select
from des import *
from rsa import *
import random
import sympy
from ast import literal_eval

#-*- coding: utf8 -*-

HOST = ''
SOCKET_LIST = []
RECV_BUFFER = 4096
PORT = 9009

def chat_server():

    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_socket.bind((HOST, PORT))
    server_socket.listen(10)

    # add server socket object to the list of readable connections
    SOCKET_LIST.append(server_socket)

    primes = [i for i in range(17,100) if sympy.isprime(i)]
    p = random.choice(primes)
    primes.remove(p)
    q = random.choice(primes)
    print "Generating your public/private keypairs now . . ."
    public, private = generate_keypair(p, q)

    file = open('./public_key', 'w+')
    file.write(str(public))
    file.close()

    print "Your public key is ", public ," and your private key is ", private

    print "Chat server started on port " + str(PORT)
    while 1:

        # get the list sockets which are ready to be read through select
        # 4th arg, time_out  = 0 : poll and never block
        ready_to_read,ready_to_write,in_error = select.select(SOCKET_LIST,[],[],0)
        key = "secret_k"
        for sock in ready_to_read:
            # a new connection request recieved
            if sock == server_socket:
                sockfd, addr = server_socket.accept()
                SOCKET_LIST.append(sockfd)
                print "Client (%s, %s) connected" % addr
                message = str(addr) + " entered our chatting room\n"
                d = des()
                encrypted = d.encrypt(key, message)
                encrypted = encrypt(private, encrypted)
                broadcast2(server_socket, sockfd, str(encrypted))
            # a message from a client, not a new connection
            else:
                # process data recieved from client,
                try:
                    # receiving data from the socket.
                    data = sock.recv(RECV_BUFFER)
                    if data:
                        # there is something in the socket
                        d = des()
                        encrypted = d.encrypt(key, "\r" '[' + str(sock.getpeername()) + '] ')
                        encrypted = encrypt(private, encrypted + data)
                        broadcast2(server_socket, sock, str(encrypted))
                    else:
                        # remove the socket that's broken
                        if sock in SOCKET_LIST:
                            SOCKET_LIST.remove(sock)

                        # at this stage, no data means probably the connection has been broken
                        broadcast(server_socket, sock, "Client (%s, %s) is offline\n" % addr, private)

                # exception
                except:
                    broadcast(server_socket, sock, "Client (%s, %s) is offline\n" % addr, private)
                    continue

    server_socket.close()

# broadcast chat messages to all connected clients
def broadcast (server_socket, sock, message, private):
    key = "secret_k"
    for socket in SOCKET_LIST:
        # send the message only to peer
        if socket != server_socket and socket != sock :
            try :
                d = des()
                message = d.encrypt(key, message)
                message = encrypt(private, message)
                socket.send(str(message))
            except :
                # broken socket connection
                socket.close()
                # broken socket, remove it
                if socket in SOCKET_LIST:
                    SOCKET_LIST.remove(socket)

def broadcast2 (server_socket, sock, message):
    for socket in SOCKET_LIST:
        # send the message only to peer
        if socket != server_socket and socket != sock :
            try :
                socket.send(message)
            except :
                # broken socket connection
                socket.close()
                # broken socket, remove it
                if socket in SOCKET_LIST:
                    SOCKET_LIST.remove(socket)

if __name__ == "__main__":
    sys.exit(chat_server())
