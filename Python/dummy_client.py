import socket, pickle, time, uuid

def client_command(clientid, command, args=()):
    command_dict = {
        "clientid" : clientid,
        "command" : command,
        "args" : args
    }

    return command_dict

host = 'masadataserver'
#host = socket.gethostbyname(socket.gethostname())
port = 6969
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect((host, port))

clientid = uuid.uuid4().hex
count = 0

# while count < 100:
#     command = client_command(clientid, 0)
#     msg = pickle.dumps(command)
#     s.sendall(msg)
#     data = s.recv(4096*4)
#     packet = pickle.loads(data)
#     #print(packet)
#     #print(packet["dataframe"])
#     time.sleep(0.05)
#     count += 1

# command = client_command(clientid, 6, "test")
# msg = pickle.dumps(command)
# s.sendall(msg)
# data = s.recv(4096*4)
# packet = pickle.loads(data)
# time.sleep(0.05)

# count = 0
# while count < 100:
#     command = client_command(clientid, 0)
#     msg = pickle.dumps(command)
#     s.sendall(msg)
#     data = s.recv(4096*4)
#     packet = pickle.loads(data)
#     #print(packet)
#     #print(packet["dataframe"])
#     time.sleep(0.05)
#     count += 1

# command = client_command(clientid, 6, "test2")
# msg = pickle.dumps(command)
# s.sendall(msg)
# data = s.recv(4096*4)
# packet = pickle.loads(data)
# time.sleep(0.05)

# count = 0
# while count < 100:
#     command = client_command(clientid, 0)
#     msg = pickle.dumps(command)
#     s.sendall(msg)
#     data = s.recv(4096*4)
#     packet = pickle.loads(data)
#     #print(packet)
#     #print(packet["dataframe"])
#     time.sleep(0.05)
#     count += 1

# command = client_command(clientid, 6, None)
# msg = pickle.dumps(command)
# s.sendall(msg)
# data = s.recv(4096*4)
# packet = pickle.loads(data)
# time.sleep(0.05)

while True:
    command = client_command(clientid, 0)
    msg = pickle.dumps(command)
    s.sendall(msg)
    data = s.recv(4096*4)
    packet = pickle.loads(data)
    print(packet)
    #print(packet["dataframe"])
    time.sleep(0.2)



