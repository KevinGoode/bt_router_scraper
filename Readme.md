# BT Router Scraper

This directory contains a microservice that scrapes a BT router for connection information and stores results in a history file. A GUI is provided that allows the browsing and display of this history file. 
 
 NOTE. 
 - Records are only written when connection info has changed
 - Main config file is /etc/bt_router_scraper/conf.json
 - Docker file is used to build and run service although built rpm can be installed on Centos 7
 - Docker container mounts current directory **(bt_router_container)** directory as /usr/src so rpm that is built is available outside of container.
  
## How to build  rpm
 
 1. Install docker
 2. Build host container
```console
bt_router_scraper> docker build --build-arg http_proxy=$http_proxy --build-arg https_proxy=$https_proxy -t bt_router_scraper:latest .
```
3. Run container
```console
bt_router_scraper> docker container run -dit -v $(pwd):/usr/src  -p 1234:80 -d bt_router_scraper:latest
```
4. Run shell in container
```console
bt_router_scraper>docker container exec -it <container-id> bash
```
5. Build rpm
```console
container-prompt> cd /usr/src/bt_router_scraper; make rpm
```

## How to install  rpm (on either Centos 7 or inside container)
 
 1. Install rpm (in container)
```console
container-prompt> cd /usr/src/dist; rpm -Uvh <rpm-name>.noarch.rpm
```
## How to run service
 
 1. Execute as follows
```console
cd /usr/lib/python3.6/site-packages/bt_router_scraper
python3 bt_router_scraper.py
```
## How to view GUI
 
 1. http://localhost:1234 (NOTE Run service for a few days to see meaningful graphs)
 

