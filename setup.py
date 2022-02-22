from setuptools import setup, find_packages

with open('requirements.txt') as f:
	requirements = f.readlines()

long_description = 'A command line tool for interacting with RSMQ queues and messages.'

setup(
		name ='rsmqctl',
		version ='1.0.0',
		author ='Keith Sharp',
		author_email ='kms@passback.co.uk',
		url ='https://github.com/keithsharp/rsmqctl',
		description ='RSMQ Command line tool.',
		long_description = long_description,
		long_description_content_type ="text/markdown",
		license ='AGPL',
		packages = find_packages(),
		entry_points ={
			'console_scripts': [
				'rsmqctl = rsmqctl.rsmqctl:cli'
			]
		},
		classifiers =[
			"Programming Language :: Python :: 3",
			"License :: OSI Approved :: GNU Affero General Public License v3 or later (AGPLv3+)",
			"Operating System :: OS Independent",
		],
		keywords ='redis rsmq message queue',
		install_requires = requirements,
		zip_safe = False
)

