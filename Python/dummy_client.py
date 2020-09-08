import socket, pickle, time

HOST = 'localhost'
PORT = 6969
# Create a socket connection.
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect((HOST, PORT))

while True:
    msg = bytes("gimme", 'utf-8')
    s.sendall(msg)
    data = s.recv(4096)
    dic = pickle.loads(data)
    print(dic)
    time.sleep(0.1)
