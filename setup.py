import re
from sys import argv

from setuptools import setup, find_packages

with open("requirements.txt", encoding="utf-8") as r:
    requires = [i.strip() for i in r]

with open("rubika/client.py", encoding="utf-8") as f:
    version = re.findall(r"__version__ = \"(.+)\"", f.read())[0]

with open("README.md", encoding="utf-8") as f:
    readme = f.read()

setup(
    name="rubika",
    version=version,
    description="this is an unofficial library for making bots in rubika. using this library you can make your own rubika bot and control that",
    long_description=readme,
    long_description_content_type="text/markdown",
    url="https://github.com/bahman-ahmadi/rubika",
    download_url="https://github.com/bahman-ahmadi/rubika/releases/latest",
    author="Bahman Ahmadi",
    author_email="bahmanahmadi.mail@gmail.com",
    license="LGPLv3",
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "Natural Language :: English",
        "License :: OSI Approved :: GNU Lesser General Public License v3 (LGPLv3)",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: Implementation",
        "Programming Language :: Python :: Implementation :: CPython",
        "Programming Language :: Python :: Implementation :: PyPy",
        "Topic :: Internet",
        "Topic :: Communications",
        "Topic :: Communications :: Chat",
        "Topic :: Software Development :: Libraries",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Software Development :: Libraries :: Application Frameworks"
    ],
    keywords="rubika self bot api library python",
    project_urls={
        "Tracker": "https://github.com/bahman-ahmadi/rubika/issues",
        "Community": "https://t.me/rubikalib",
        "Source": "https://github.com/bahman-ahmadi/rubika",
        "Documentation": "https://rubikalib.github.io",
    },
    python_requires="~=3.5",
    packages=find_packages(),
    zip_safe=False,
    install_requires=requires
)