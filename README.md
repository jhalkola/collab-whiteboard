# collab-whiteboard
Distributed Systems course project

# Running
When starting the X11 server, in extra setting Disable access control needs to be ticked.

Before usage you need to set few environmental variables
To set the X11 display set:
```
set DISPLAY=x.x.x.x:0
```
where x.x.x.x is your X11 hosts ip address.

If you want to use automatic testing you need to add two more environmental variables:

To use the automatic drawing set:
```
set TESTING=true
```
To limit how many pixels will one client draw set:
```
set LIMIT=x
```
where x is integer value. -1 or no value means that client will draw until it is closed.



To start the server and two client go to the drawing folder and run:
```
docker-compose up
```

After if you want to start additional clients go to the drawing/clientapp folder and run:
```
docker-compose up
```

Remember that you have to set new name for the new clients

To set the client name set
```
set NAME=xxxxxxxxxxxxxxxx
```
where xxxx... is max 16 character long string.




To run automated test with 5 clients and server go to the drawing folder and run:
```
docker-compose -f docker-compose_5.yml
```

If you make changes to the python files remember to rebuild the composes using:
```
docker-compose build
```
in their respective folders
