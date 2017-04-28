import socket
import sys
from thread import start_new_thread 

port = 80
maxConn = 15
bufferSize = 8192
webserver = "192.168.1.2"


def check_blacklist(data):
    blacklist = ["--", "0=0", ">", "<", "\'", "\""]
    for badword in blacklist:
        if badword in data:
           return True
    return False



def proxy(webserver, port, conn, data, addr):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect((webserver, port))
    print "Got here"
    print len(data)
    print data
    sock.send(data)
    print "got sdf"
    print data
    while True:
        reply = sock.recv(bufferSize)
        if (len(reply) > 0):
            conn.send(reply)
        else:
            break
    sock.close()
    conn.close()
    
def conn_string(conn, data, addr):
    try:
        first_line = data.split('\n')[0]
        url = first_line.split(' ')[1]
        if check_blacklist(url):
           print "ATTACK BLOCKED"
           conn.close()
           return
        http_pos = url.find("://")
        if (http_pos==-1):
            temp = url
        else:
            temp = url[(http_pos+3):]
        port_pos = temp.find(":")

        webserver_pos = temp.find("/")
        if webserver_pos == -1:
            webserver_pos = len(temp)
        webserver = ""
        port = -1
        if (port_pos==-1 or webserver_pos < port_pos):
            port = 80
            webserver = temp[:webserver_pos]
        else:
            port = int((temp[(port_pos+1):])[:webserver_pos-port_pos-1])
            webserver = temp[:port_pos]
        print "starting proxy"
        #proxy(webserver, 8000, conn, data, addr)
	proxy(webserver, 80, conn, data, addr)
    except Exception, e:
		pass
       
def start():
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind(("192.168.1.3", port))
    s.listen(maxConn)
    while True:
        try:
            conn, addr = s.accept()
            print "Connection accepted"
            data = conn.recv(bufferSize)
            print data
            start_new_thread(conn_string, (conn, data, addr))
        except KeyboardInterrupt:
			s.close()
			print "Shutting Down Proxy"
			sys.exit(1)

webserver = raw_input("Enter address of websever: ")        
start()



