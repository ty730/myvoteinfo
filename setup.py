from setuptools import setup

setup(name='myvoteinfo',
      version='0.1',
      description='Query the KS SOS site for voter registration',
      url='https://github.com/ty730/myvoteinfo',
      author='Peter Karman',
      author_email='peter@peknet.com',
      license='MIT',
      packages=['myvoteinfo'],
      zip_safe=False,
      install_requires=['python-dateutil', 'requests', 'beautifulsoup4'])

