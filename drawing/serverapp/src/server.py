
import zmq
import struct
from time import sleep, time
import pygame
import os
import json



def get_colors():
    '''
    This function gets the color data from the json file
    '''
    with open("colors.json") as file:
        data = json.load(file)
    return data.values()

def unpack_helper(fmt, data):
    '''
    Unpack helper for structs
    '''
    size = struct.calcsize(fmt)
    return struct.unpack(fmt, data[:size])



def main():
    #Get all the colors as list
    all_colors = list(get_colors())

    #Zeromq pub and sub topics
    client_draw_topic = b'drw_updt'
    image_update_topic = b'img_updt'
    client_disc_topic = b'clt_disc'

    #Ports for the communication
    server_to_client_port = 8000
    client_to_server_port = 8001

    #Start the context and start publisher and subscribers
    context = zmq.Context()

    sub = context.socket(zmq.SUB)
    sub.bind("tcp://*:{}".format(client_to_server_port))
    sub.setsockopt(zmq.SUBSCRIBE, client_draw_topic)
    sub.setsockopt(zmq.SUBSCRIBE, image_update_topic)
    sub.setsockopt(zmq.SUBSCRIBE, client_disc_topic)

    pub = context.socket(zmq.PUB)
    pub.bind("tcp://*:{}".format(server_to_client_port))

    #Start the connection server
    connect_socket = context.socket(zmq.REP)
    connect_socket.bind("tcp://*:8002")

    #Initialize the users dictionary
    users = {}

    #Timer for backing up the image
    last_save_time = time()
    backup_time = 30

    #Try getting the image from existing file. If this fails then create new image
    try:
        image = pygame.image.load_basic("log/canvas.bmp")
    except:
        image = pygame.Surface((10,10))
        image.fill((255,255,255))

    #Start serving
    while True:
        try:
            #Check for subscriber messages
            data = sub.recv(zmq.NOBLOCK)

            #Get the topic of the message
            topic = unpack_helper("8s", data)[0]

            if topic == client_draw_topic:
                #If topic is client draw topic then receive the pixel coordinates and color and do the drawing into the image
                _, user, x, y = struct.unpack("8s16sii", data)
                color = users[user.decode('utf-8')]
                x = int(x)
                y = int(y)
                color = pygame.Color(color)

                #Use pygame to draw pixel
                pygame.draw.rect(image, color, (x, y, 1, 1))

                #Initialize the response message and send it to everyone
                userdata = ""
                original_user = user
                for user in users:
                    userdata += user + users[user]
                imagedata = pygame.image.tostring(image, "RGB")

                response = struct.pack("8si300s16s{}s".format(len(userdata)), image_update_topic, len(users), imagedata, original_user, userdata.encode('utf-8'))
                pub.send(response)

                
                
            if topic == client_disc_topic:
                #If the topic is client disconnecting topic then remove the client from the users list. This will be updated to the clients in the next draw message
                _, user = struct.unpack("8s16s", data)
                del(users[user.decode('utf-8')])
                print("User left: {}".format(user.decode('utf-8')))

                
        except Exception as e:
            pass
            
        try:
            #Check if we got new clients connecting
            data = connect_socket.recv(zmq.NOBLOCK)
            #Get the name of connecting user
            new_name = struct.unpack("16s", data)[0].decode('utf-8')
            
            #If the name is already taken then respond with error message. Otherwise add user to list and send them their own color and current image
            response = b'0'
            if new_name in users:
                response = struct.pack("i",0)
                print("Already user with this name")
            else:
                print("Adding user: {}".format(new_name))
                #Initialize response to the connection message
                form = "ii7s300s{}s".format(len(users)*23)
                color = ""
                for c in all_colors:
                    if not c in users.values():
                        color = c
                        break
                users[new_name] = color
                colordata = color.encode('utf-8')

                #get all the users and their colors into string
                userdata = ""
                
                for user in users:
                    userdata += user + users[user]
                
                #Get the byte data from the image
                imagedata = pygame.image.tostring(image, "RGB")

                response = struct.pack(form, 1, len(users), colordata, imagedata, userdata.encode('utf-8'))

            #Send back the response                
            connect_socket.send(response)
                
        except Exception as e:
            #print(e)
            pass
    

    if time()>last_save_time+backup_time:
        #Backup the image
        pygame.image.save(image, "log/canvas.bmp")
        last_save_time = time()

main()