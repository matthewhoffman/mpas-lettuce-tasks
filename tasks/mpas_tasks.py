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

@step('A (\d+) processor MPAS "([^"]*)" run')
def run_mpas(step, procs, executable):
	if not world.develop_exists:
		print "Develop not built. Skipping develop run..."
	else:
		os.chdir(world.basedir)
		os.chdir(world.rundir)
		command = "mpirun"
		arg1 = "-n"
		arg2 = "%s"%procs
		arg3 = "%s"%executable
		subprocess.call([command, arg1, arg2, arg3], stdout=dev_null, stderr=dev_null)
		command = "mv"
		arg1 = "output.0000-01-01_00.00.00.nc"
		arg2 = "%sprocs.output.nc"%procs
		subprocess.call([command, arg1, arg2], stdout=dev_null, stderr=dev_null)
		if world.num_runs == 0:
			world.num_runs = 1
			world.run1 = arg2
			try:
				del world.rms_values
				world.rms_values = defaultdict(list)
			except:
				world.rms_values = defaultdict(list)
		elif world.num_runs == 1:
			world.num_runs = 2
			world.run2 = arg2
		os.chdir(world.basedir)

@step('A (\d+) processor MPAS  "([^"]*)" run with restart')
def run_mpas_with_restart(step, procs, executable):
	os.chdir(world.basedir)
	os.chdir(world.rundir)

	duration = seconds_to_timestamp(world.dt)
	final_time = seconds_to_timestamp(world.dt + 24*3600)

	namelistfile = open('namelist.input', 'r+')
	lines = namelistfile.readlines()
	namelistfile.seek(0)
	namelistfile.truncate()

	for line in lines:
		if line.find('config_start_time') >= 0:
			new_line = "    config_start_time = 'file'\n"
		elif line.find('config_run_duration') >= 0:
			new_line = "    config_run_duration = '%s'\n"%duration
		elif line.find('config_restart_interval') >= 0:
			new_line = "    config_restart_interval = '0000_00:00:01'\n"
		elif line.find('config_output_interval') >= 0:
			new_line = "    config_output_interval = '0000_00:00:01'\n"
		else:
			new_line = line

		namelistfile.write(new_line)

	namelistfile.close()
	del lines

	restart_file = open('restart_timestamp', 'w+')
	restart_file.write('0000-01-01_00:00:00')
	restart_file.close()

	command = "mpirun"
	arg1 = "-n"
	arg2 = "%s"%procs
	arg3 = "%s"%executable
	subprocess.call([command, arg1, arg2, arg3], stdout=dev_null, stderr=dev_null)

	command = "rm"
	arg1 = "-f"
	arg2 = "output.0000-01-01_00.00.00.nc"
	subprocess.call([command, arg1, arg2], stdout=dev_null, stderr=dev_null)

	namelistfile = open('namelist.input', 'r+')
	lines = namelistfile.readlines()
	namelistfile.seek(0)
	namelistfile.truncate()

	for line in lines:
		if line.find('config_do_restart') >= 0:
			new_line = "    config_do_restart = .true.\n"
		elif line.find('config_restart_interval') >= 0:
			new_line = "    config_restart_interval = '1000_00:00:01'\n"
		else:
			new_line = line

		namelistfile.write(new_line)

	namelistfile.write("mv output.0000-01-%s.nc %sprocs.restarted.output.nc"%(final_time[2:].replace(":","."), procs))
	namelistfile.close()
	del lines

	command = "mpirun"
	arg1 = "-n"
	arg2 = "%s"%procs
	arg3 = "ocean_model"
	subprocess.call([command, arg1, arg2, arg3], stdout=dev_null, stderr=dev_null)

	command = "mv"
	arg1 = "output.0000-01-%s.nc"%(final_time[2:].replace(":","."))
	arg2 = "%sprocs.restarted.output.nc"%procs
	subprocess.call([command, arg1, arg2], stdout=dev_null, stderr=dev_null)

	if world.num_runs == 0:
		world.num_runs = 1
		world.run1 = arg2
		try:
			del world.rms_values
			world.rms_values = defaultdict(list)
		except:
			world.rms_values = defaultdict(list)
	elif world.num_runs == 1:
		world.num_runs = 2
		world.run2 = arg2
	os.chdir(world.basedir)


@step('I compute the RMS of "([^"]*)"')
def compute_rms(step, variable):
	if world.num_runs == 2:
		f1 = NetCDFFile("%s/%s"%(world.rundir,world.run1),'r')
		f2 = NetCDFFile("%s/%s"%(world.rundir,world.run2),'r')

		field1 = f1.variables["%s"%variable][-1,:,:]
		field2 = f2.variables["%s"%variable][-1,:,:]

		field1 = field1 - field2
		field1 = field1 * field1
		rms = sum(field1)
		rms = rms / sum(field1.shape[:])
		rms = math.sqrt(rms)
		world.rms_values[variable].append(rms)
		f1.close()
		f2.close()
		os.chdir(world.basedir)
	else:
		print 'Less than two runs. Skipping RMS computation.'

@step('I see "([^"]*)" RMS of 0')
def check_rms_values(step, variable):
	if world.num_runs == 2:
		assert world.rms_values[variable][0] == 0.0, '%s RMS failed.'%variable
	else:
		print 'Less than two runs. Skipping RMS check.'


@step('I clean the test directory')
def clean_test(step):
	command = "rm"
	arg1 = "-rf"
	arg2 = world.rundir
	subprocess.call([command, arg1, arg2], stdout=dev_null, stderr=dev_null)
