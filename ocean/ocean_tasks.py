import sys, os, glob, shutil, numpy, math
import subprocess

from netCDF4 import *
from netCDF4 import Dataset as NetCDFFile
from pylab import *

from lettuce import *

from collections import defaultdict

dev_null = open(os.devnull, 'w')

def seconds_to_timestamp(seconds):
	days = 0
	hours = 0
	minutes = 0

	if seconds >= 24*3600:
		days = int(seconds/(24*3600))
		seconds = seconds - int(days * 24 * 3600)

	if seconds >= 3600:
		hours = int(seconds/3600)
		seconds = seconds - int(hours*3600)

	if seconds >= 60:
		minutes = int(seconds/60)
		seconds = seconds - int(minutes*60)

	timestamp = "%4.4d_%2.2d:%2.2d:%2.2d"%(days, hours, minutes, seconds)
	return timestamp

@step('A "([^"]*)" "([^"]*)" "([^"]*)" "([^"]*)" test')
def get_test_case(step, size, levs, test, time_stepper):
	world.basedir = os.getcwd()
	world.rundir = "%s_%s_%s"%(test, size, levs)
	world.num_runs = 0

	if not os.path.exists("%s/%s.tgz"%(world.basedir, world.rundir)):
		command = "wget"
		arg1 = "http://oceans11.lanl.gov/mpas_data/mpas_ocean/test_cases/staging/%s.tgz"%(world.rundir)
		subprocess.call([command, arg1], stdout=dev_null, stderr=dev_null)

	if not os.path.exists("%s/%s"%(world.basedir, world.rundir)):
		command = "tar"
		arg1 = "xzf"
		arg2 = "%s.tgz"%world.rundir
		subprocess.call([command, arg1, arg2], stdout=dev_null, stderr=dev_null)
		command = "cp"
		arg1 = "%s/namelist.input"%world.rundir
		arg2 = "%s/namelist.input.default"%world.rundir
		subprocess.call([command, arg1, arg2], stdout=dev_null, stderr=dev_null)

	os.chdir(world.rundir)
	if os.path.exists("%s/ocean_model_develop"%(world.basedir)):
		world.develop_exists = True
		command = "ln"
		arg1 = "-s"
		arg2 = "../ocean_model_develop"
		subprocess.call([command, arg1, arg2], stdout=dev_null, stderr=dev_null)
	else:
		world.develop_exists = False

	command = "ln"
	arg1 = "-s"
	arg2 = "../ocean_model"
	subprocess.call([command, arg1, arg2], stdout=dev_null, stderr=dev_null)

	command = "cp"
	arg1 = "namelist.input.default"
	arg2 = "namelist.input"
	subprocess.call([command, arg1, arg2], stdout=dev_null, stderr=dev_null)

	command = "rm"
	arg1 = "-f"
	arg2 = '\*.output.nc'
	subprocess.call([command, arg1, arg2], stdout=dev_null, stderr=dev_null)

	namelistfile = open('namelist.input', 'r+')
	lines = namelistfile.readlines()

	for line in lines:
		if line.find("config_dt") >= 0:
			line_split = line.split(" = ")
			world.dt = float(line_split[1])
		if line.find("config_time_integrator") >= 0:
			line_split = line.split(" = ")
			world.old_time_stepper = line_split[1].replace("'","")

	world.time_stepper_change = False
	if world.old_time_stepper.find(time_stepper) < 0:
		world.time_stepper_change = True
		if world.old_time_stepper.find("split_explicit") >= 0:
			world.dt /= 10.0
		elif time_stepper.find("split_explicit") >= 0:
			world.dt *= 10.0

	duration = seconds_to_timestamp(int(world.dt*2))

	namelistfile.seek(0)
	namelistfile.truncate()

	for line in lines:
		new_line = line
		if line.find("config_run_duration") >= 0:
			new_line = "    config_run_duration = '%s'\n"%(duration)
		elif line.find("config_output_interval") >= 0:
			new_line = "    config_output_interval = '0000_00:00:01'\n"
		elif line.find("config_restart_interval") >= 0:
			new_line = "    config_restart_interval = '1000_00:00:01'\n"
		elif line.find("config_stats_interval") >= 0:
			new_line = "    config_stats_interval = '1000_00:00:01'\n"
		elif line.find("config_dt") >= 0:
			new_line = "    config_dt = %f\n"%world.dt
		elif world.time_stepper_change:
			if line.find("config_time_integrator") >= 0:
				new_line = "    config_time_integrator = '%s'\n"%(time_stepper)

		namelistfile.write(new_line)

	namelistfile.close()

	del lines

	os.chdir(world.basedir)


