import socket, pickle, time, uuid

def client_command(clientid, command, args=()):
    command_dict = {
        "clientid" : clientid,
        "command" : command,
        "args" : args
    }

    return command_dict

host = '100.64.7.195'
#host = socket.gethostbyname(socket.gethostname())
port = 6969
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect((host, port))

clientid = uuid.uuid4().hex

while True:
    command = client_command(clientid, 0)
    msg = pickle.dumps(command)
    s.sendall(msg)
    data = s.recv(4096*4)
    packet = pickle.loads(data)
    print(packet)
    #print(packet["dataframe"])
    time.sleep(0.05)



