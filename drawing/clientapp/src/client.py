import pygame
import math
import zmq
import struct
from sys import argv
from datetime import datetime
import time
import os
import atexit
import random




def unpack_helper(fmt, data):
    '''
    This function unpacks only part of the data and returns the variables
    '''
    size = struct.calcsize(fmt)
    return struct.unpack(fmt, data[:size])

def unpack_helper_part(fmt, data):
    '''
    This function unpacks only part of the data and returns the variables AND the leftover bytes
    '''
    size = struct.calcsize(fmt)
    return struct.unpack(fmt, data[:size]), data[size:]

def exit_handler():
    '''
    This function handles quiting the program. Closes the files and sends disconnect message
    '''
    global pub
    global name
    global client_disc_topic
    global log_file
    log_file.close()
    message = struct.pack("8s16s", client_disc_topic, name.encode('utf-8'))
    pub.send(message)



def update_namelist(users):
    '''
    Updates game display to display the users received from the server
    '''
    divider = 5
    for user in users:
        text = font.render(user, False, users[user])
        gameDisplay.blit(text, (display_width+10, divider))
        divider += 25



#Format for the connect message
connect_message_format = "8s16s"
#Set topics for different messages for publishing and subscribing
connect_message_topic = b'cnt_mesg'
client_draw_topic = b'drw_updt'
image_update_topic = b'img_updt'
client_disc_topic = b'clt_disc'

#Start the ZeroMQ context and store ports for the connection
server_to_client_port = 8000
client_to_server_port = 8001
context = zmq.Context()

#Initialize variables
users = {}
own_color = ""
image_as_string = ""

#If TESTING-env variable has been set then use randomized names. Otherwise use env-var NAME as name
is_automatic = os.environ.get('TESTING')
automatic_limit = int(os.environ.get('LIMIT'))
sent_messages = 0

if is_automatic=="true":
    name = "client{}".format(random.randint(0,50000))
else:
    name = os.environ.get('NAME')
#Format the name to be 16 characters long
name = "{}                ".format(name)[:16]
#Get the server ip
server = os.environ.get('SERVER_CONNECT_URI')


#Try connecting to the connect server
while True:
    try:
        connect_socket = context.socket(zmq.REQ)
        connect_socket.connect("{}:8002".format(server))
        break
    except Exception as e:
        print(e)
        time.sleep(1)

#Format the connection message and send it to the server
connect_message = struct.pack("16s", name.encode('utf-8'))
connect_socket.send(connect_message)

#Wait for the answer from the server and close the connection
answer = connect_socket.recv()
connect_socket.close()

#Check if connection was succesfull
success = unpack_helper("i", answer)[0]


if int(success) == 1:
    #If connection is succesfull then get users, clients own color and the image from the server
    user_count = int(unpack_helper("ii", answer)[1])
    unpacked, left = unpack_helper_part("ii7s300s",answer)
    for i in range(user_count-1):
        user, left = unpack_helper_part("16s7s", left)
        user_name = user[0].decode('utf-8')
        user_color = user[1].decode('utf-8')
        users[user_name] = user_color
    own_color = unpacked[2].decode('utf-8')
    users[name] = own_color
    image_as_string = unpacked[3]
else:
    #If not succesfull then quit the program
    print("This name is already in use")
    quit()


#connect the subscriber and publisher
sub = context.socket(zmq.SUB)
sub.connect("{}:{}".format(server, server_to_client_port))
sub.setsockopt(zmq.SUBSCRIBE, image_update_topic)

pub = context.socket(zmq.PUB)
pub.connect("{}:{}".format(server, client_to_server_port))


#Assign the exit handler
atexit.register(exit_handler)

#Initialize the pygame and screen
pygame.init()

scale = 50
display_width = 10*scale
display_height = 10*scale

gameDisplay = pygame.display.set_mode((display_width+200, display_height))
pygame.display.set_caption("Client")

#Get the image from the data received from the server
image = pygame.image.fromstring(image_as_string, (10, 10), "RGB")



#Checker for if the client should stop
done = False

#Variables for checking if we should draw new pixel
mouseIsPressed = False
mouseWasPressed = False
mouse_prev_x = -1
mouse_prev_y = -1

#Font for the name texts
font = pygame.font.Font('freesansbold.ttf', 20)


#Open the log file
now = datetime.now()
date_string = now.strftime("%d-%m-%Y_%H:%M:%S")
log_file = open("log/log_{}_{}.txt".format(date_string, name),'w')

#Variables for checking the time for automated drawing
last_time = time.time()+15
send_time = 0

#Scale the image and draw screen for the first time
scaled = pygame.transform.scale(image, (display_width, display_height))
gameDisplay.fill((255,255,255))
pygame.draw.rect(gameDisplay, (0, 0, 0), (display_width,0,2,display_height))
update_namelist(users)
gameDisplay.blit(scaled,(0, 0))
pygame.display.flip()

#Start working
while not done:
    try:
        #Try receiving data on subscribers
        data = sub.recv(zmq.NOBLOCK)

        #Get the topic of the message
        topic = unpack_helper("8s", data)[0]

        if topic == image_update_topic:
            #Topic is image update
            #unpack user count, image and the name of editer 
            msg, left = unpack_helper_part("8si300s16s", data)
            user_count = msg[1]
            users = {}
            for i in range(user_count):
                #Unpack the user names and colors from the rest of the data
                user, left = unpack_helper_part("16s7s", left)
                user_name = user[0].decode('utf-8')
                user_color = user[1].decode('utf-8')
                users[user_name] = user_color
            
            #If the editor is us then log the time of drawing
            editor = msg[3].decode('utf-8')
            if editor == name and is_automatic=="true":
                time_taken = time.time()-send_time
                log_file.write("{}\n".format(time_taken))
                send_time=0
                #Assing random time for the next automatic pixel
                last_time = time.time()+random.random()*3
            
            #Get the image data from the bytes
            img = pygame.image.fromstring(msg[2],(10,10), "RGB")
            image.blit(img, (0, 0))
            #Scale and display the image
            scaled = pygame.transform.scale(image, (display_width, display_height))
            gameDisplay.fill((255,255,255))
            pygame.draw.rect(gameDisplay, (0, 0, 0), (display_width,0,2,display_height))
            update_namelist(users)
            gameDisplay.blit(scaled,(0, 0))
            pygame.display.flip()
    except Exception as e:
        pass
    #Check pygame events
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            done = True
        if event.type == pygame.MOUSEBUTTONDOWN:
            #Mouse down event
            if event.button == 1:
                mouseIsPressed = True
        if event.type == pygame.MOUSEBUTTONUP:
            #Mouse up event
            if event.button == 1:
                mouseIsPressed = False
            
    if mouseIsPressed:
        #If mouse was pressed down at this moment or if we moved from one pixel to another then send new pixel to server
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
    
    if is_automatic=="true":
        #If testing mode is on send random pixels to the server
        if time.time()>last_time and send_time==0 and sent_messages<automatic_limit:
            x = random.randint(0,9)
            y = random.randint(0,9)
            send_time = time.time()
            message = struct.pack("8s16sii", client_draw_topic, name.encode('utf-8'), x, y)
            pub.send(message)
            sent_messages+=1
            