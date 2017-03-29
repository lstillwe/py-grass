# NOTE: Windows OS support not complete
import os
import sys
import subprocess
import binascii
import tempfile
import shutil
import getopt

def usage():
	print '\nUsage:'
	print sys.argv[0] + ' -b <buildings_shapefile_name> -c <cells_shapefile_name> -s <shore_shapefile_name>'
	print ' ' 


def main(argv):
	grass7bin_win = ''
	grass7bin_lin = 'grass'
	buildings = ''
	cells = ''
	shore = ''
	
	# look for 3 arguments:
	# buildings, cells, and shore
	# all shapefiles - do not add '.shp'
	if((len(sys.argv)) < 7):
		usage()
		sys.exit(-1)
	try:
		opts, args = getopt.getopt(argv,"b:c:s:")
	except getopt.GetoptError as err:
		print '\nCommand line option error: ' + str(err)
		usage()
		sys.exit(-1)

	for opt, arg in opts:
		if arg.endswith('.shp'):
    			arg = arg[:-4]
	
		if opt in ("-b"):
			buildings = arg
		elif opt in ("-c"):
			cells = arg
		elif opt in ("-s"):
			shore = arg

	#specify input-output locations
	inputloc = '/data/'
	outputloc = '/data/'
	myfile = shore + '.shp'

	##Software
	if sys.platform.startswith('linux'):
    		grass7bin=grass7bin_lin
	elif sys.platform.startswith('win'):
    		grass7bin=grass7bin_win
	else:
    		OSError('Platform not configured')
	#print sys.platform
	#print grass7bin

	startcmd = [grass7bin, '--config', 'path']
	p = subprocess.Popen(startcmd, shell=False, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
	out, err = p.communicate()

	if p.returncode != 0:
    		print >>sys.stderr, "ERROR: Cannot find GRASS GIS 7 start script (%s)" % startcmd
    		sys.exit(-1)

	if sys.platform.startswith('linux'):
    		gisbase = out.strip('\n')
	elif sys.platform.startswith('win'):
    		gisbase = out.strip('\n\r')
    		os.environ['GRASS_SH'] = os.path.join(gisbase,'mys','bin','sh.exe')

	# TODO: need to fix this for LINUX???
	#os.environ['PATH'] += ';' + r"C:\OSGEO4W64\apps\grass\grass-7.0.4\lib"

	# Set GISBASE environment variable
	os.environ['GISBASE'] = gisbase
	# define GRASS-Python environment
	gpydir = os.path.join(gisbase, "etc", "python")
	sys.path.append(gpydir)
	# define GRASS DATABASE
	if sys.platform.startswith('win'):
    		gisdb = os.path.join(os.getenv('APPDATA', 'grassdata'))
	else:
    		gisdb = os.path.join(os.getenv('HOME', 'grassdata'))

	# override for now with TEMP dir
	gisdb = os.path.join(tempfile.gettempdir(), 'grassdata')
	try:
    		os.stat(gisdb)
	except:
    		os.mkdir(gisdb)

	#Location/mapset:random names
	string_length = 16
	location = binascii.hexlify(os.urandom(string_length))
	mapset   = 'PERMANENT'
	location_path = os.path.join(gisdb, location)
	
	#create new location
	startcmd = [grass7bin, '-c', myfile, '-e', location_path]  
	
	print startcmd
	p = subprocess.Popen(startcmd, shell=False, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
	out, err = p.communicate()
	if p.returncode != 0:
    		print >>sys.stderr, 'ERROR: %s' % err
    		print >>sys.stderr, 'ERROR: Cannot generate location (%s)' % startcmd
    		sys.exit(-1)
	else:
    		print 'Created location %s' % location_path

	# import GRASS Python bindings
	import grass.script as gscript
	import grass.script.setup as gsetup
	
	# launch session
	gsetup.init(gisbase, gisdb, location, mapset) 

	gscript.run_command('v.in.ogr', input=inputloc + buildings + '.shp', output=buildings, overwrite=True)
	gscript.run_command('v.in.ogr', input=inputloc + cells + '.shp', output=cells, overwrite=True)
	gscript.run_command('v.in.ogr', input=inputloc + shore + '.shp', output=shore, overwrite=True)
	gscript.run_command('v.overlay', ainput=buildings, binput=cells, operator='and', output='overlay_out',overwrite=True)
	gscript.run_command('v.to.rast', input=cells, output=cells, use='attr', attribute_column='Cellnumber',overwrite=True)
	gscript.run_command('v.distance', from_='overlay_out', to=shore, upload='dist', column='b_cat')
	gscript.run_command('v.out.ascii',flags='c',  input='overlay_out', output=outputloc+'Buildings_data.txt',
		columns='a_OCCUP_TYPE,a_YEAR_BUILT,a_BLDG_VALUE,a_FFE,a_FOUND_TYPE,b_cat,b_Cellnumber', format='point', separator='space', overwrite=True)

if __name__ == "__main__":
    main(sys.argv[1:])
