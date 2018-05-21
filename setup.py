"""A setuptools based setup module.
See:
https://packaging.python.org/en/latest/distributing.html
https://github.com/pypa/sampleproject
"""

# Always prefer setuptools over distutils
from setuptools import setup, find_packages
# To use a consistent encoding
from codecs import open
from os import path

here = path.abspath(path.dirname(__file__))

# Get the long description from the README file
with open(path.join(here, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()



#from setuptools import setup, find_packages 
#from setuptools import setup

# See https://medium.com/small-things-about-python/lets-talk-about-python-packaging-6d84b81f1bb5#.pjxrklmi6

setup(name='OGN_Flogger', 
      version='0.3.2a12',
      scripts=['flogger_gui.py'],      # Command to run 
      description='Realtime logging of glider flights from Flarm data',
      long_description='Realtime logging and tracking of gliders from Flarm signals using APRS.',
      classifiers=[
        'Development Status :: 3 - Alpha',
        'License :: OSI Approved :: GNU General Public License (GPL)',
        'Programming Language :: Python :: 2.7',
        'Topic :: Scientific/Engineering :: Information Analysis',
      ],
      project_urls = {
          'tracker': 'http://github.com/tobiz/OGN-Flight-Logger_V3/issues',
          },
      keywords='OGN Open Glider Flarm Logging Tracking',
      url='http://github.com/tobiz/OGN-Flight-Logger_V3',
      author='tobiz',
      author_email='pjrobinson@metronet.co.uk',
      license='GPL', 
      python_requires = '>=2.7, <3',
#      packages = find_packages(),
      py_modules=[
                'flarm_db',
                'flogger3',
                'flogger_dump_flights',
                'flogger_dump_IGC',
                'flogger_dump_tracks',
                'flogger_email_log',
                'flogger_email_msg',
                'flogger_find_tug',
                'flogger_functions',
                'flogger_get_coords',
                'flogger_gui',
                'flogger_landout',
                'flogger_moviesplash',
                'flogger_OGN_db',
#                'flogger_process_log',
#                'flogger_progress_indicator',
                'flogger_resources_rc',
                'flogger_settings',
                'flogger_signals',
#                'flogger_splash',
                'flogger_test_YorN',
                'flogger_ui',
                'flogger_aprs_parser',
                'gpxTracks',
                'open_db'
                ],
                
      install_requires=[
                        'geocoder>=1.4.0',
                        'parse>=1.8.0',
                        'configobj>=4.7.2',
                        'geopy>=1.11.0',
                        'aerofiles>=0.3',
                        'aprslib>=0.6.46',
                        'gpxpy>=1.1.2',
                        'setuptools>=3.3',
                        'pytz>=2012c',
                        'requests>=2.13.0',
                        'mplleaflet>=0.0.5',
                        'LatLon>=1.0.2',
#                        'PyQt4>=4.11.4',
                        'pyephem>=3.7.6.0',
                        'protobuf>=3.5.2.post1',
                        'adhocracy_pysqlite>=2.6.3',
                        'pysqlite3>=0.1.0',
                        'matplotlib',
                        ],
#      data_files=[('', ['data/flogger_help_icon-1.png']),
#                  ('', ['data/flogger_icon-08.png']),
#                  ('', ['data/flogger_start.png']),
#                  ('', ['data/flogger_stop.png']),
#                  ('', ['data/flogger_settings_file.txt']),
##                  ('', ['data/requirements.txt']),
#                  ('', ['data/flogger_about.ui']),  
#                  ('', ['data/flogger_config_1.ui']),  
#                  ('', ['data/flogger_help.ui']),  
#                  ('', ['data/flogger.ui']),
#                  ('', ['data/flogger_resources.qrc']), 
#                  ('', ['data/flogger_schema-1.0.4.sql']),
#                  ('', ['data/ogn-logo-ani.gif']), 
##                  ('', ['flarm_data']),
#                  ],

 
#       packages=find_packages(),
      include_package_data=True,
      zip_safe=False)
