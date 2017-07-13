##
# lisastillwell/py-grass
#
# This creates an Ubuntu derived base image that installs GRASS from a specific
# subversion checkout compiled against a specific GDAL version.
#

# Ubuntu 14.04 Trusty Tahyr
FROM ubuntu:trusty

MAINTAINER Lisa Stillwell <lisa@renci.org>

# Set the locale
RUN locale-gen en_US.UTF-8  
ENV LANG en_US.UTF-8  
ENV LANGUAGE en_US:en  
ENV LC_ALL en_US.UTF-8 

# Install the application.
ADD . /usr/local/src/grass-docker/
RUN apt-get update -y && \
    apt-get install -y make && \
    make -C /usr/local/src/grass-docker install clean && \
    apt-get purge -y make

# Externally accessible data is by default put in /data.
#WORKDIR /data
#VOLUME ["/data"] - don't need this for Discovery Env use

# Ensure the SHELL is picked up by grass.
ENV SHELL /bin/bash

# All commands are executed by grass.
ENTRYPOINT ["python"]

# Output GRASS version by default.
CMD ["-V"]
#for testing
#CMD ["/bin/bash"]
