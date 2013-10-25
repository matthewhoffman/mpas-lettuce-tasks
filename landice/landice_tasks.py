import sys, os, glob, shutil, numpy, math
import subprocess

from netCDF4 import *
from netCDF4 import Dataset as NetCDFFile
from pylab import *

from lettuce import *

from collections import defaultdict

dev_null = open(os.devnull, 'w')


@step('A "([^"]*)" "([^"]*)" test')
def get_test_case(step, test, velocity_solver):
	world.basedir = os.getcwd()
	world.rundir = "%s"%(test)
	world.num_runs = 0

	# If we don't have the test case tarball, then go get it.
	if not os.path.exists("%s/%s.tar.gz"%(world.basedir, world.rundir)):
		arg = "https://dl.dropboxusercontent.com/u/30481359/%s.tar.gz"%(world.rundir)
		subprocess.call(['wget', '--no-check-certificate', arg], stdout=dev_null, stderr=dev_null)

	if not os.path.exists("%s/%s"%(world.basedir, world.rundir)):
		# unpack the test
		arg = "%s.tar.gz"%world.rundir
		subprocess.call(['tar', 'zxf', arg], stdout=dev_null, stderr=dev_null)

		# Setup a default namelist that we can modify later
		arg1 = "%s/namelist.input"%world.rundir
		arg2 = "%s/namelist.input.default"%world.rundir 
		subprocess.call(['cp', arg1, arg2], stdout=dev_null, stderr=dev_null)

	os.chdir(world.rundir)
	if os.path.exists("%s/landice_model_develop"%(world.basedir)):
		world.develop_exists = True
		command = "ln"
		arg1 = "-s"
		arg2 = "../landice_model_develop"
		subprocess.call([command, arg1, arg2], stdout=dev_null, stderr=dev_null)
	else:
		world.develop_exists = False

	command = "ln"
	arg1 = "-s"
	arg2 = "../landice_model"
	subprocess.call([command, arg1, arg2], stdout=dev_null, stderr=dev_null)

#	command = "cp"
#	arg1 = "namelist.input.default"
#	arg2 = "namelist.input"
#	subprocess.call([command, arg1, arg2], stdout=dev_null, stderr=dev_null)

	command = "rm"
	arg1 = "-f"
	arg2 = '\*.output.nc'
	subprocess.call([command, arg1, arg2], stdout=dev_null, stderr=dev_null)

	# Modify the default namelist as needed
###	namelistfile = open('namelist.input', 'r+')
###	lines = namelistfile.readlines()

###	for line in lines:
###		if line.find("config_dt") >= 0:
###			line_split = line.split(" = ")
###			world.dt = float(line_split[1])
###		if line.find("config_time_integrator") >= 0:
###			line_split = line.split(" = ")
###			world.old_time_stepper = line_split[1].replace("'","")

###	world.time_stepper_change = False
###	if world.old_time_stepper.find(time_stepper) < 0:
###		world.time_stepper_change = True
###		if world.old_time_stepper.find("split_explicit") >= 0:
###			world.dt /= 10.0
###		elif time_stepper.find("split_explicit") >= 0:
###			world.dt *= 10.0

###	duration = seconds_to_timestamp(int(world.dt*2))

###	namelistfile.seek(0)
###	namelistfile.truncate()

###	for line in lines:
###		new_line = line
###		if line.find("config_run_duration") >= 0:
###			new_line = "    config_run_duration = '%s'\n"%(duration)
###		elif line.find("config_output_interval") >= 0:
###			new_line = "    config_output_interval = '0000_00:00:01'\n"
###		elif line.find("config_restart_interval") >= 0:
###			new_line = "    config_restart_interval = '1000_00:00:01'\n"
###		elif line.find("config_stats_interval") >= 0:
###			new_line = "    config_stats_interval = '1000_00:00:01'\n"
###		elif line.find("config_dt") >= 0:
###			new_line = "    config_dt = %f\n"%world.dt
###		elif world.time_stepper_change:
###			if line.find("config_time_integrator") >= 0:
###				new_line = "    config_time_integrator = '%s'\n"%(time_stepper)

###		namelistfile.write(new_line)

###	namelistfile.close()

###	del lines

	os.chdir(world.basedir)



@step('I compute the Halfar RMS')
def compute_rms(step):
	world.halfarRMS=float(subprocess.check_output('python ' + world.rundir + '/halfar.py -f ' + world.rundir + '/' +  world.run1 + ' -n | grep "^* RMS error =" | cut -d "=" -f 2 \n', shell='/bin/bash'))

@step('I see Halfar RMS of <20')
def check_rms_values(step):
	if world.halfarRMS == []:
		assert False, 'Calculation of Halfar RMS failed.'
	else:
		assert world.halfarRMS < 20.0, 'Halfar RMS of %s is greater than 20.0 m'%world.halfarRMS



