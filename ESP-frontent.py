"""Web frontend on WIFI-Acces Point of home WIFI."""

try: 
    import usocket as socket
except:
    import socket

import network

import esp
esp.osdebug(None)

import gc
gc.collect()

from time import sleep

HomeNet_ssid="SCHEIBENWELT"
HomeNet_password="Rincewind"

acces_point_ssid="ESP-frontend"
acces_point_password="wificontrol"

ap=network.WLAN(network.AP_IF)
ap.active(True)
ap.config(essid=acces_point_ssid, password=acces_point_password)

while ap.active() == False:
    pass

print("Connection successful")
print(ap.ifconfig())

class WebPage():
    """A framework for webpages"""
    def __init__(self,heading:str,rows:int,columns:int) -> None:
        """Create first html"""
        self.heading=heading
        self.rows=rows
        self.columns=columns
        self.html:str=''

    def create_html(self):
        html="""
        <html>
            <head>
            <meta name="viewport", content="width=device-width, initial-scale=1">
            </head>
            <body>
                <h1>"""+self.heading+"""</h1>
            </body>
        </html>"""
        self.html=html
        return html

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind(('',80))
s.listen(5)

while True:
    conn, addr = s.accept()
    print("Got a connection from %s" % str(addr))
    request=conn.recv(1024)
    print("Content = %s" % str(request))
    Page=WebPage("Test Page",2,2)
    response=Page.create_html()
    conn.send(response)
    print("Response sent.")
    conn.close()
    print("Connection closed")
