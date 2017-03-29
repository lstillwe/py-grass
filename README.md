# Python & GRASS Docker Image

This is an Ubuntu derived image containing [GRASS GIS](http://grass.osgeo.org)
software.
It supports python scripts as input that use the Grass GIS sysyem.
Currently Grass 7.2 is configured/supported.
## Usage

Running the container without any arguments will output the Python version:

    docker run lisastillwell/py-grass

All arguments passed to the image are passed as options to python, i.e. the
following is equivalent to the previous invocation:

    docker run lisastillwell/py-grass -V

You will most likely want to work with data on the host system from within the
docker container, in which case run the container with the `-v` option along the
following lines:

    docker run -it --rm -v $(pwd)/data:/data lisastillwell/py-grass mypythonscript.py arg1 arg2

The python script is responsible for any interaction with Grass and is required to create
a grass db/mapset/location. It will most likely also collect input args (Names of shapefiles, etc)
to use in any Grass processing commands. Since the image is not designed to be persistant, any desired
output, should be written to the mounted volume before the script finishes. 
A sample python script is included in this repo.
It is run like this:
    docker run -it --rm -v $(pwd)/data:/data lisastillwell/py-grass mypythonscript.py -b buildings -c cells -s shore
where buildings, cells, and shore are shape files in the mounted volume.

## Creating images with specific versions

You may want to create your own images based on specific versions of GRASS and
GDAL, in which case clone the GRASS docker repository and edit the
`grass-checkout.txt` and `gdal-checkout.txt` files to reference the desired
versions.  For example, the following will build GRASS 7.0.0 against GDAL 2.0.0:

```
git clone git://github.com/geo-data/grass-docker/ \
&& cd grass-docker \
&& echo "tags/release_20150220_grass_7_0_0" > grass-checkout.txt \
&& echo "2.0.0" > gdal-checkout.txt \
&& docker build -t geodata/grass:local .
```

`tags/release_20150220_grass_7_0_0` references a specific checkout of the
[GRASS subversion repository](https://svn.osgeo.org/grass/grass/).

If you want to include the most up-to-date
commits then you need to build the docker image yourself locally along these
lines:

    docker build -t geodata/grass:local git://github.com/geo-data/grass-docker/
