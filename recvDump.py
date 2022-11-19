import socket 
import time


sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.bind(("0.0.0.0", 4444))
sock.listen()

client, addr = sock.accept()

print(f"Client {addr}")

data = client.recv(1024).decode()

name = name = f"{time.localtime().tm_mday}-{time.localtime().tm_mon}-{time.localtime().tm_year}-{addr}.txt"
file = open(name, "a")

for item in data.split(";"):
    file.write(item+"\n")

file.close()
client.close()