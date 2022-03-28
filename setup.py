from setuptools import setup

setup(name='myvoteinfo',
      version='0.3',
      description='Query the KS SOS site or Rock the Vote site for voter registration',
      url='https://github.com/ty730/myvoteinfo',
      author='Tyler Wong',
      author_email='tylerwong2000@gmail.com',
      license='MIT',
      packages=['myvoteinfo'],
      zip_safe=False,
      install_requires=['python-dateutil', 'requests', 'beautifulsoup4'])

