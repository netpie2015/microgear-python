from setuptools import setup
setup(
  name = 'microgear',
  packages = ['microgear'], # this must be the same as the name above
  version = '1.2.7',
  description = 'Client library of Python, connect application code or hardware to netpie platform.',
  author = 'netpie',
  author_email = 'support@netpie.io',
  url = 'https://github.com/netpieio/microgear-python', # use the URL to the github repo
  keywords = ['netpie','iot','mqtt'], # arbitrary keywords
  classifiers = [],
  install_requires=['paho-mqtt==1.2.3','requests','certifi'],
)
