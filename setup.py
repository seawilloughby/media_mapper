print '''
Installing media_mapper....
                         
 ____ _____ _____ _   _  ____ ___ _     
/ ___|_   _| ____| \ | |/ ___|_ _| |    
\___ \ | | |  _| |  \| | |    | || |    
 ___) || | | |___| |\  | |___ | || |___ 
|____/ |_| |_____|_| \_|\____|___|_____|
                                        
'''
try:
    from setuptools import setup, find_packages
except ImportError:
    from distutils.core import setup


import versioneer
import sys


config = {
    'description': 'media_mapper is a simple example python package',
    'author': 'Jason Shiverick',
    'url': 'here',
    'download_url': 'Where to download it.',
    'author_email': 'jshiv00@gmail.com',
    'version': versioneer.get_version(),
    'cmdclass': versioneer.get_cmdclass(),
    
    'install_requires': [
    'numpy',
    'pandas',
    'nose',
    'tweepy'
    ],

    'packages': find_packages(),#['media_mapper'],
    'scripts': [],
    'name': 'media_mapper'
}



print "system is: "+sys.platform
print ''
print "installing media_mapper dependencies... "
print config['install_requires']

setup(**config)
