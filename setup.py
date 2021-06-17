import setuptools
from distutils.core import setup

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
  name = 'cloudlink',
  packages = ['cloudlink'],
  version = '0.1.1',
  license='Unlicense',
  description = 'Server-side code for a powerful Scratch 3.0 websocket extension.',
  long_description=long_description,
  long_description_content_type="text/markdown",
  author = 'MikeDEV',
  author_email = 'mikierules109@gmail.com',
  url = 'https://github.com/MikeDev101/cloudlink',
  keywords = ['scratch', 'cloud variable', 'cloud variables', 'cloudlink', 'scratch3'],
  install_requires=[
          'websocket-server',
          'websocket-client'
      ],
  classifiers=[
    'Development Status :: Stable',
    'License :: OSI Approved :: Unlicense',
    'Programming Language :: Python :: 3',
    'Operating System :: OS Independent'
  ],
)