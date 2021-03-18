
import zmq
import struct
from time import sleep
import pygame
import os
import json

address = os.environ.get("SERVER_LISTEN_URI")

def get_colors():
    with open("colors.json") as file:
        data = json.load(file)
    return data.values()

def unpack_helper(fmt, data):
    size = struct.calcsize(fmt)
    return struct.unpack(fmt, data[:size])

def main():
    all_colors = list(get_colors())
    connect_message_format = "8s16s"
    client_draw_topic = b'drw_updt'
    image_update_topic = b'img_updt'
    client_disc_topic = b'clt_disc'

    server_to_client_port = 8000
    client_to_server_port = 8001

    context = zmq.Context()
    sub = context.socket(zmq.SUB)
    sub.bind("tcp://*:{}".format(client_to_server_port))
    sub.setsockopt(zmq.SUBSCRIBE, client_draw_topic)
    sub.setsockopt(zmq.SUBSCRIBE, image_update_topic)
    sub.setsockopt(zmq.SUBSCRIBE, client_disc_topic)
    pub = context.socket(zmq.PUB)
    pub.bind("tcp://*:{}".format(server_to_client_port))

    connect_socket = context.socket(zmq.REP)
    connect_socket.bind("tcp://*:8002")

    users = {}
    try:
        image = pygame.image.load_basic("log/canvas.bmp")
    except:
        image = pygame.Surface((50,50))
        image.fill((255,255,255))

    while True:
        try:
            data = sub.recv(zmq.NOBLOCK)
            topic = unpack_helper("8s", data)[0]
            if topic == client_draw_topic:
                _, user, x, y = struct.unpack("8s16sii", data)
                color = users[user.decode('utf-8')]
                #print("Draw from user: {} {}".format(user, users[user.decode('utf-8')]))
                x = int(x)
                y = int(y)
                color = pygame.Color(color)
                pygame.draw.rect(image, color, (x, y, 1, 1))
                pygame.image.save(image, "log/canvas.bmp")
                userdata = ""
                original_user = user
                for user in users:
                    userdata += user + users[user]
                imagedata = pygame.image.tostring(image, "RGB")

                response = struct.pack("8si7500s16s{}s".format(len(userdata)), image_update_topic, len(users), imagedata, original_user, userdata.encode('utf-8'))
                pub.send(response)
            if topic == client_disc_topic:
                _, user = struct.unpack("8s16s", data)
                del(users[user.decode('utf-8')])
                print("User left: {}".format(user.decode('utf-8')))

                
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
                color = ""
                for c in all_colors:
                    if not c in users.values():
                        color = c
                        break
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