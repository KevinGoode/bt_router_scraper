# Base image for bt_router_scraper build and test container
# docker build --build-arg http_proxy=$http_proxy --build-arg https_proxy=$https_proxy -t bt_router_scraper:latest .
# docker container run -dit -v $(pwd):/usr/src  -p 1234:80 -d bt_router_scraper:latest
# docker container exec -it <container-id> bash
# inside container cd /usr/src/bt_router_scraper; make rpm
FROM centos:7

# Set up proxies for the image build process
# I'm sure there's a way to do this on the host, but I couldn't find it.
RUN echo "proxy=$http_proxy" >> /etc/yum.conf
ENV http_proxy=$http_proxy
ENV https_proxy=$https_proxy

RUN yum -y update

# Install build tools and utils
RUN yum -y install python3-devel
RUN yum -y install make
RUN yum -y install rpm-build

#Install utils
RUN yum -y install wget
RUN yum -y install nano

#Install runtime tools
RUN yum -y install httpd
RUN yum -y install php

#Run apache on docker start
CMD ["/usr/sbin/httpd", "-D", "FOREGROUND"]
