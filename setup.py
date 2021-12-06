from distutils.core import setup
setup(
  name = 'rubika',
  packages = ['rubika'],
  version = '2.0',
  license='MIT', 
  description = 'rubika library is a unofficial library for making bot in the rubika. this library works with rubika’s API',
  author = 'Bahman Ahmadi',
  author_email = 'bahmanahmadi.mail@gmail.com',
  url = 'https://github.com/Bahman-Ahmadi/rubika',
  download_url = 'https://github.com/Bahman-Ahmadi/rubika/archive/refs/tags/v_20.tar.gz',
  keywords = [],
  install_requires=[
          'requests',
          'pycryptodome',
          'requests',
          'urllib3',
          'tqdm'
      ],
  classifiers=[
    'Development Status :: 3 - Alpha',
    'Intended Audience :: Developers',
    'Topic :: Software Development :: Build Tools',
    'License :: OSI Approved :: MIT License',
    'Programming Language :: Python :: 3',   
    'Programming Language :: Python :: 3.4',
    'Programming Language :: Python :: 3.5',
    'Programming Language :: Python :: 3.6',
    'Programming Language :: Python :: 3.7',
    'Programming Language :: Python :: 3.8',
    'Programming Language :: Python :: 3.9',
  ],
)
