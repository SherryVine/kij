# chat_client.py

import sys, socket, select
from des import *

def chat_client():
    if(len(sys.argv) < 3) :
        print 'Usage : python chat_client.py hostname port'
        sys.exit()

    host = sys.argv[1]
    port = int(sys.argv[2])
    key = ''

    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.settimeout(2)

    # connect to remote host
    try :
        s.connect((host, port))
        d = des()
        key = d.decrypt(str(s.getsockname()), s.recv(4096))
    except :
        print 'Unable to connect'
        sys.exit()

    print 'Connected to remote host. You can start sending messages'
    sys.stdout.write('[Me] '); sys.stdout.flush()

    while 1:
        socket_list = [sys.stdin, s]

        # Get the list sockets which are readable
        read_sockets, write_sockets, error_sockets = select.select(socket_list , [], [])

        for sock in read_sockets:
            if sock == s:
                # incoming message from remote server, s
                data = sock.recv(4096)
                if not data :
                    print '\nDisconnected from chat server'
                    sys.exit()
                else :
                    #print data
                    d = des()
                    decrypted = d.decrypt(key, data)
                    data = decrypted
                    sys.stdout.write(data + '\n')
                    sys.stdout.write('[Me] '); sys.stdout.flush()

            else :
                # user entered a message
                msg = sys.stdin.readline()
                check = (len(msg) - 1) % 8
                if(check != 0):
                    sys.stdout.write('PLAINTEXT MUST BE A MULTIPLE OF EIGHT' + '\n')
                text = msg
                d = des()
                msg = d.encrypt(key,text)
                s.send(msg)
                sys.stdout.write('[Me] '); sys.stdout.flush()

if __name__ == "__main__":
    sys.exit(chat_client())
    # print "Ciphered: ", r.encode('hex')
    # #print "Ciphered: %r" % r
    # print "Deciphered: ", r2
