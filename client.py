import socket, base64

ip = raw_input("Please input the ip to connect: ")
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
try:
    sock.connect((ip, 8964))
except:
    print "Can't connect to the server..."
    raw_input("Press enter to quit ...")
    exit()

path = sock.recv(10240).strip()
while True:
    cmd = raw_input("[wong2@%s %s]$ " % (socket.gethostbyname(socket.gethostname()), path))
    if cmd == "quit":
        break
    if cmd.split(" ")[0] == "wget":
        filename = "".join(cmd.split(" ")[1:])
        sock.send(cmd)
        fp = open(filename, "wb")
        fp.write(base64.b64decode(eval(sock.recv(10240).strip())['data']))
        fp.close()
        continue
    sock.send(cmd)
    result = eval(sock.recv(10240).strip())
    if result['type'] == 'path':
        path = result['data'].replace("/", "\\")
    else:
        print result['data']
        
sock.close()

