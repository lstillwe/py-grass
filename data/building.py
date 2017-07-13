a# NOTE: Windows OS support not complete
import os
import sys
import subprocess
import binascii
import tempfile
import shutil
import getopt
import random

def usage():
	print '\nUsage:'
	print sys.argv[0] + ' -b <buildings_shapefile_name> -c <cells_shapefile_name> -s <shore_shapefile_name> -d <shapefile_dir_path>'
	print ' ' 


def main(argv):
	grass7bin_win = ''
	grass7bin_lin = 'grass'
	buildings = ''
	cells = ''
	shore = ''
	shp_dir = ''
	
	# look for 4 arguments:
	# buildings, cells, shore and shapefiles dir path
	# all shapefiles - do not add '.shp'
	if((len(sys.argv)) < 9):
		usage()
		sys.exit(-1)
	try:
		opts, args = getopt.getopt(argv,"b:c:s:d:")
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
		elif opt in ("-d"):
			shp_dir = os.path.basename(arg)

	#specify input and output locations
	cwd = os.getcwd()
	outputloc = cwd
	inputloc = cwd + '/' + shp_dir + '/'

	myfile = inputloc + shore + '.shp'

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

	# setup tmp output file
	tmp_houses = outputloc+'tmp_houses_sm_grid.txt'

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
	gscript.run_command('v.out.ascii',flags='c',  input='overlay_out', output=tmp_houses,
		columns='a_OCCUP_TYPE,a_YEAR_BUILT,a_BLDG_VALUE,a_FFE,a_FOUND_TYPE,b_cat,b_Cellnumber', format='point', separator='space', overwrite=True)

	#format output

	lines=open(tmp_houses).readlines()
	lines=lines[1:]
	b=[[]]
	occ_type={'NP':5,'1000':1,'1005':2,'1020':2,'1015':3,'1025':2,'1030':2,'1045':2,'1095':3,'1040':3,'1110':2,'1100':3,'1115':2,'1245':2,'1240':0,'1130':2,'1120':2,'1255':1,'1250':1,'1265':4,'1260':4,'1270':4,'1275':4,'1285':4,'1340':2,'1335':2,'1330':2,'1350':3,'1355':3,'1360':3,'1350':3,'1375':3,'1380':3,'1385':3,'1430':3,'1465':3,'1575':0,'1580':1,'1585':1,'1590':2,'1595':2,'1600':4,'1620':3,'2005':2,'2015':2,'2020':2,'2025':2,'2030':2,'2040':2,'2045':4,'2055':3,'2095':3,'2100':3,'2110':2,'2125':3,'2235':0,'2240':0,'2245':1,'2250':1,'2255':5,'2265':5,'2270':1,'2275':1,'2285':2,'2340':2,'2350':2,'2355':2,'2360':2,'2365':2,'2380':2,'2390':3,'2430':3,'2435':3,'2445':3,'2460':3,'2575':0,'2580':1,'2585':1,'2590':1,'2605':1,'2610':1,'2620':4,'2630':3,'3005':4,'3015':2,'3020':6,'3025':1,'3035':3,'3040':3,'3045':1,'3055':3,'3060':3,'3095':3,'3110':1,'3115':1,'3130':5,'3240':5,'3245':5,'3250':5,'3255':2,'3260':5,'3265':5,'3270':5,'3275':1,'3280':1,'3285':1,'3290':1,'4005':5,'4015':1,'4030':5,'4045':5,'4110':3,'4245':3,'4285':3,'5000':2,'5005':2,'5020':2,'5025':2,'5030':2,'5035':2,'5040':3,'5045':3,'5055':3,'5075':3,'5085':3,'5095':3,'5100':3,'5115':3,'5130':3,'5240':3,'5270':1,'5285':5,'5290':5,'5310':3,'5315':5,'5330':3,'5340':3,'5410':3,'5460':3}
	for line in lines:
    		a=line.split(' ')
    		
		if a[8]<70:
        		row=1
    		else:
        		row =2
    		if a[4]=='':
        		a[4]=0
    		if a[5]=='NP':
        		a[5]==50000
    		if a[4]=='NP':
        		a[4]==1900
    		if a[6]=='NP':
        		a[6]=15
    		b.append([occ_type[a[3]],(random.randint(0, 9) * int(a[9])+ random.randint(1, 15)), float(a[5]),float(a[5]), int(a[4]),int(row),int(a[8]),float(a[6])*0.3048])
	b=b[1:]
	os.remove(tmp_houses)
	buildingout=open("houses_sm_grid.txt",'w+')
    #buildingout=open(outputloc+"houses_sm_grid.txt",'w+')
	n=0
	while n < len(b):
    		buildingprop=str(b[n][0])+'\t'+str(b[n][1])+'\t'+str(b[n][2])+'\t'+str(b[n][3])+'\t'+str(b[n][4])+'\t'+str(b[n][5])+'\t'+str(b[n][6])+'\t'+str(b[n][7])+'\n'
    		buildingout.write(buildingprop)
    		n=n+1
	
if __name__ == "__main__":
    main(sys.argv[1:])
