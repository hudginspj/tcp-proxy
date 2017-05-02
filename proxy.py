import socket
import sys
import time
from thread import start_new_thread
import urllib

port = 80
maxConn = 1500
bufferSize = 8192
pwebserver = ""
proxyip = ""
addrmap = {}
blocked = {}
perm_block = []
ban = True

def check_blacklist(url, typ):
    blacklist = ["--", "0=0", ">", "<", "'", '"']
    decoded = urllib.unquote(url).decode('utf8')
    print "[--] Checking " + typ +" data against blacklist..."
    for badword in blacklist:
        if badword in url or badword in decoded:
           print "[--] ATTACK DETECTED. Blocking traffic."
           return True
    print "[--] " + typ + " data is clean"
    return False



def proxy(webserver, port, conn, data, addr):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect((webserver, port))
    print "Sending data:\n-----\n"+data+"\n-----\n"
    sock.send(data)
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
        post_data = data.split("\n")[len(data.split("\n"))-1]
        url = first_line.split(' ')[1]
        if check_blacklist(url, "GET") or check_blacklist(post_data, "POST"):
           conn.send("<h1>403 - Request Denied. You've been Perma-banned.</h1>")
           print "ATTACK BLOCKED - IP Perma-banned"
           if (ban): perm_block.append(addr[0])
           conn.close()
           return
        else:
           print "[--] Data is clean - forwarding through."
        proxy(pwebserver, 80, conn, data, addr)
    except Exception, e:
                print "Exception:"
                print e
                pass

def start():
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind((proxyip, port))
    s.listen(maxConn)
    print "[--] Running proxy"
    while True:
        try:
            conn, addr = s.accept()
            #Temporary IP Blocking - Block IP for 15 seconds due to DDOS Detected
            if addr[0] in blocked.keys():
                if abs(blocked[addr[0]]-time.time()) < 15:
                    print blocked
                    print "[--] Request from "+addr[0]+" blocked."
                    conn.recv(bufferSize)
                    conn.send("<h1>403 - Request Denied.</h1>")
                    conn.close()
                    blocked[addr[0]] = time.time()
                    continue
                else:
                    del blocked[addr[0]]
            #END of Temporary IP Blocking
            #Perminate IP Blocking - Block IP forever due to XSS or SQL ATTACK
            if addr[0] in perm_block:
                print "[--] Request from "+addr[0]+" blocked."
                conn.close()
                continue
            #END of Perminate IP Block
            #DDOS Detection - More than 5 connections within 10 seconds
            if addr[0] in addrmap.keys():
                num = 0
                now = time.time()
                for ad in addrmap[addr[0]]:
                    if ad[2]-now < 10:
                        num+=1
                if num > 5:
                    print "[--] Too many connections from " + addr[0] + ". DDOS ATTACK detected. Instigating block,"
                    conn.recv(bufferSize);
                    conn.send("<h1>403 - Request Denied.</h1>")
                    conn.close()
                    blocked[addr[0]]= time.time()
                    del addrmap[addr[0]]
                    continue
                else:
                    addrmap[addr[0]].append((conn, addr, time.time()))
            else:
                addrmap[addr[0]] = [(conn, addr, time.time())]
            #End of DDOS Detection
            print "[--] Connection accepted from "+addr[0]
            data = conn.recv(bufferSize)
            start_new_thread(conn_string, (conn, data, addr))
        except KeyboardInterrupt:
			s.close()
			print "[--] Shutting Down Proxy"
			sys.exit(1)

pwebserver = raw_input("Enter address of websever: ")
proxyip = raw_input("Enter address of this proxy: ")
ban = (raw_input("Enable banning Y/n? ") == "Y")
if (ban):
   print "Banning enabled"
else:
   print "Banning disabled"

start()
