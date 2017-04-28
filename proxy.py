import socket
import sys
from thread import start_new_thread 

port = 8888
maxConn = 5
bufferSize = 8192
host = "127.0.0.1"
rport = 8889

def proxy(conn, data, addr):
	sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	sock.connect((host, rport))
	print data
	sock.send(data)
	while True:
		reply = sock.recv(bufferSize)
		print reply
		if (len(reply) > 0):
			conn.send(reply)
		else:
			break
	sock.close()
	conn.close()

def start():
	s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	s.bind(("localhost", port))
	s.listen(maxConn)
	while True:
		conn, addr = s.accept()
		data = conn.recv(bufferSize)
		start_new_thread(proxy, (conn, data, addr))
		
start()



