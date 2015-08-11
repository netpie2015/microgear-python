from distutils.core import setup
setup(
  name = 'microgear',
  packages = ['microgear'], # this must be the same as the name above
  version = '0.2.2',
  description = 'Client library of Python, connect application code or hardware to netpie platform.',
  author = 'nectec',
  author_email = 'info@nectec.or.th',
  url = 'https://bitbucket.org/ridnarong/microgear-python', # use the URL to the github repo
  download_url = 'https://4ARMER@bitbucket.org/ridnarong/microgear-python.git', # I'll explain this in a second
  keywords = [], # arbitrary keywords
  classifiers = [],
  install_requires=['paho.mqtt','oauth2'],
)