from distutils.core import setup
setup(
  name = 'microgear',
  packages = ['microgear'], # this must be the same as the name above
  version = '1.1.10',
  description = 'Client library of Python, connect application code or hardware to netpie platform.',
  author = 'Chaiwith Santaweesuk',
  author_email = 'developer@netpie.io',
  url = 'https://github.com/netpieio/microgear-python', # use the URL to the github repo
  keywords = ['netpie','iot','mqtt'], # arbitrary keywords
  classifiers = [],
  install_requires=['paho-mqtt','oauth2'],
)
