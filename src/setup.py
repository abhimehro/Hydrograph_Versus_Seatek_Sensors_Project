# setup.py
import os

# Get the directory of the current script (safe fallback in case __file__ is unavailable)
try :
	current_directory = os.path.dirname ( os.path.abspath ( __file__ ) )
except NameError :
	current_directory = os.getcwd ( )  # Fallback to the working directory
print ( f"The current directory is: {current_directory}" )

# Define the filepath for README.md
try :
	readme_path = os.path.join ( current_directory , "README.md" )
except NameError :
	readme_path = "README.md"  # Fallback

# Safely read the long description if the README.md file exists
if os.path.isfile ( readme_path ) :
	try :
		with open ( readme_path , encoding = "utf-8" ) as f :
			long_description = f.read ( )
	except UnicodeDecodeError :
		print ( "Error: Unable to read README.md due to encoding issues." )
		long_description = "A project for processing hydrograph and Seatek sensor data."
else :
	long_description = "A project for processing hydrograph and Seatek sensor data."

# Define setup configuration
from setuptools import find_packages , setup

setup (
		name = "Hydrograph_Versus_Seatek_Sensors_Project" ,
		version = "0.1.0" ,
		packages = find_packages ( where = "src" ) ,
		package_dir = { "" : "src" } ,
		install_requires = [
				"requests>=2.25.0" ,
				"pandas>=1.3.3" ,
				"matplotlib>=3.4.0" ,
				"pytest>=6.0.0" ,
				"flake8" ,
				"black" ,
				] ,
		author = "Abhi Mehrotra" ,
		author_email = "abhimhrtr@pm.me" ,
		description = "A project for processing hydrograph and Seatek sensor data, "
		              "calculating correlations, and visualizing the results." ,
		long_description = long_description ,
		long_description_content_type = "text/markdown" ,
		url = "https://github.com/abhimehro/Hydrograph_Versus_Seatek_Sensors_Project" ,
		license = "MIT" ,
		classifiers = [
				"Programming Language :: Python :: 3" ,
				"Programming Language :: Python :: 3.8" ,
				"Programming Language :: Python :: 3.9" ,
				"Programming Language :: Python :: 3.10" ,
				"Programming Language :: Python :: 3.11" ,
				"License :: OSI Approved :: MIT License" ,
				"Operating System :: OS Independent" ,
				] ,
		python_requires = ">=3.8" ,
		entry_points = {
				"console_scripts" : [
						"hydrosensors=hydrosensors_project.cli:main" ,
						] ,
				} ,
		)
