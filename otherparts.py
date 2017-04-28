def conn_string(conn, data, addr):
    try:
        first_line = data.split('\n')[0]
        url = first_line.split(' ')[1]
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

        proxy_server(webserver, port, conn, addr, data)
except Exception, e:
        pass
