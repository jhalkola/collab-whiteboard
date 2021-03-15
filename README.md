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

To set the client name set
```
set NAME=xxxxxxxxxxxxxxxx
```
where xxxx... is max 16 character long string.

To start the server and single client go to the drawing folder and run:
```
docker-compose up
```

After if you want to start additional clients go to the drawing/clientapp folder and run:
```
docker-compose up
```

Remember that you have to set new name for the new clients

If you make changes to the python files remember to rebuild the composes using:
```
docker-compose build
```
in their respective folders

#To-do
- data logging
- saving the image on server side
- showing names in client (Already received and stored in users-dictionary)
- documentating
- commenting the code

Data loggausta ja kuvan tallennusta varten:
https://docs.docker.com/storage/volumes/
