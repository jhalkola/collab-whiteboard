
import zmq
import struct
from time import sleep
import pygame

def unpack_helper(fmt, data):
    size = struct.calcsize(fmt)
    return struct.unpack(fmt, data[:size])

def main():
    connect_message_format = "8s16s"
    client_draw_topic = b'drw_updt'
    image_update_topic = b'img_updt'

    server_to_client_port = 8000
    client_to_server_port = 8001

    context = zmq.Context()
    sub = context.socket(zmq.SUB)
    sub.bind("tcp://*:{}".format(client_to_server_port))
    sub.setsockopt(zmq.SUBSCRIBE, client_draw_topic)
    sub.setsockopt(zmq.SUBSCRIBE, image_update_topic)
    pub = context.socket(zmq.PUB)
    pub.bind("tcp://*:{}".format(server_to_client_port))

    connect_socket = context.socket(zmq.REP)
    connect_socket.bind("tcp://*:8002")

    users = {"matti           ":"#ffffff"}
    image = pygame.Surface((50,50))

    while True:
        try:
            data = sub.recv(zmq.NOBLOCK)
            topic = unpack_helper("8s", data)[0]
            if topic == client_draw_topic:
                _, color, x, y = struct.unpack("8s7sii", data)
                x = int(x)
                y = int(y)
                color = pygame.Color(color.decode('utf-8'))
                pygame.draw.rect(image, color, (x, y, 1, 1))
                userdata = ""
                
                for user in users:
                    userdata += user + users[user]
                imagedata = pygame.image.tostring(image, "RGB")

                response = struct.pack("8si7500s{}s".format(len(user)*23), image_update_topic, len(users), imagedata, userdata.encode('utf-8'))
                pub.send(response)

                
        except Exception as e:
            pass
            
        try:
            data = connect_socket.recv(zmq.NOBLOCK)
            new_name = struct.unpack("16s", data)[0].decode('utf-8')
            
            response = b'0'
            if new_name in users:
                response = struct.pack("i",0)
                print("Already user with this name")
            else:
                print("Adding user: {}".format(new_name))
                form = "ii7s7500s{}s".format(len(users)*23)
                color = "#AAAAAA"
                users[new_name] = color
                
                colordata = color.encode('utf-8')
                userdata = ""
                
                for user in users:
                    userdata += user + users[user]
                imagedata = pygame.image.tostring(image, "RGB")
                
                response = struct.pack(form, 1, len(users), colordata, imagedata, userdata.encode('utf-8'))
                
            connect_socket.send(response)
                
        except Exception as e:
            #print(e)
            pass

main()