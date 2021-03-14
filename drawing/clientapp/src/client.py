import pygame
import math
import zmq
import struct
from time import sleep
from sys import argv
import os
import atexit




print("I am alive")
def unpack_helper(fmt, data):
    size = struct.calcsize(fmt)
    return struct.unpack(fmt, data[:size])

def unpack_helper_part(fmt, data):
    size = struct.calcsize(fmt)
    return struct.unpack(fmt, data[:size]), data[size:]

def exit_handler():
    global pub
    global name
    global client_disc_topic
    message = struct.pack("8s16s", client_disc_topic, name.encode('utf-8'))
    pub.send(message)

connect_message_format = "8s16s"
connect_message_topic = b'cnt_mesg'
client_draw_topic = b'drw_updt'
image_update_topic = b'img_updt'
client_disc_topic = b'clt_disc'


server_to_client_port = 8000
client_to_server_port = 8001
context = zmq.Context()

users = {}
own_color = ""
image_as_string = ""

name = os.environ.get('NAME')
server = "tcp://serverd"#os.environ.get('SERVER_CONNECT_URI')
atexit.register(exit_handler)
while True:
    print("Give your name:")
    
    print(name)
    name = "{}                ".format(name)[:16]
    while True:
        try:
            connect_socket = context.socket(zmq.REQ)
            connect_socket.connect("{}:8002".format(server))
            break
        except Exception as e:
            print(e)
            sleep(1)
    print("Connected")
    connect_message = struct.pack("16s", name.encode('utf-8'))
    connect_socket.send(connect_message)
    answer = connect_socket.recv()
    connect_socket.close()
    success = unpack_helper("i", answer)[0]
    if int(success) == 1:
        user_count = int(unpack_helper("ii", answer)[1])
        unpacked, left = unpack_helper_part("ii7s7500s",answer)
        for i in range(user_count-1):
            user, left = unpack_helper_part("16s7s", left)
            user_name = user[0].decode('utf-8')
            user_color = user[1].decode('utf-8')
            users[user_name] = user_color
        own_color = unpacked[2].decode('utf-8')
        users[name] = own_color
        image_as_string = unpacked[3]
        break
    else:
        print("This name is already in use")
        quit()
        pass



sub = context.socket(zmq.SUB)
sub.connect("{}:{}".format(server, server_to_client_port))
sub.setsockopt(zmq.SUBSCRIBE, image_update_topic)

pub = context.socket(zmq.PUB)
pub.connect("{}:{}".format(server, client_to_server_port))
pygame.init()

scale = 10
display_width = 50*scale
display_height = 50*scale

gameDisplay = pygame.display.set_mode((display_width, display_height))
pygame.display.set_caption("Client")

image = pygame.image.fromstring(image_as_string, (50, 50), "RGB")


def scale_image(image, size):
    image = pygame.transform.scale(image, size)
    return image

clock = pygame.time.Clock()
done = False
mouseIsPressed = False
mouseWasPressed = False
mouse_prev_x = -1
mouse_prev_y = -1
color = (255,0,0)



while not done:
    try:
        data = sub.recv(zmq.NOBLOCK)
        
        topic = unpack_helper("8s", data)[0]
        if topic == image_update_topic:
            msg, left = unpack_helper_part("8si7500s", data)
            user_count = msg[1]
            users = {}
            for i in range(user_count):
                user, left = unpack_helper_part("16s7s", left)
                user_name = user[0].decode('utf-8')
                user_color = user[1].decode('utf-8')
                users[user_name] = user_color
            img = pygame.image.fromstring(msg[2],(50,50), "RGB")
            image.blit(img, (0, 0))
    except Exception as e:
        pass#print(e)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            done = True
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:
                mouseIsPressed = True
        if event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1:
                mouseIsPressed = False
            
    if mouseIsPressed:
        x, y = pygame.mouse.get_pos()
        x = math.floor(x/scale)
        y = math.floor(y/scale)
        if mouseWasPressed == False or mouse_prev_x != x or mouse_prev_y != y:
            message = struct.pack("8s16sii", client_draw_topic, name.encode('utf-8'), x, y)
            pub.send(message)
        mouse_prev_x = x
        mouse_prev_y = y
        mouseWasPressed = True
    else:
        mouseWasPressed = False

    
    scaled = scale_image(image, (display_width, display_height))
    gameDisplay.blit(scaled,(0, 0))
    pygame.display.flip()
    clock.tick(60)
