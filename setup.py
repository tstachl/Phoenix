#!/usr/bin/env python
"""

    Phoenix
    
    LICENSE

    Permission is hereby granted, free of charge, to any person obtaining a copy
    of this software and associated documentation files (the "Software"), to deal
    in the Software without restriction, including without limitation the rights
    to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
    copies of the Software, and to permit persons to whom the Software is
    furnished to do so, subject to the following conditions:
    
    The above copyright notice and this permission notice shall be included in
    all copies or substantial portions of the Software.
    
    THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
    IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
    FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
    AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
    LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
    OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
    THE SOFTWARE.
    
    @copyright:    Copyright (c) 2011, w3agency.net
    @author:       Thomas Stachl <t.stachl@w3agency.net>
    @since:        Mar 21, 2011

"""

"""----------------------------------------------------------------------------
                                Imports
----------------------------------------------------------------------------"""
# we want to make sure setup tools is installed
# so we try and install if it isn't
try:
    from setuptools import setup, find_packages
except ImportError:
    from ez_setup import use_setuptools
    use_setuptools()
    from setuptools import setup, find_packages
from os import path

# get the version based on VERSION.
v = open(path.join(path.dirname(__file__), 'VERSION'))
VERSION = v.readline().strip()
v.close()

setup(
    name="Phoenix",
    version=VERSION,
    packages=find_packages(),
    
    install_requires=["GitPython >= 0.3.1-beta2", "argparse >= 1.1", "SQLObject >= 1.0.0b2dev-r4370"],
    
    author="Phoenix, w3agency.net",
    author_email="phoenix@w3agency.net",
    
    description="Phoenix is a server management tool in it's early stages.",
    long_description="""

At the moment Phoenix provides git repository management with a solid
user management, additionally you can add deployment keys directly to
repositories. Access to the repositories is provided over SSH but with
the built in access control there is no need for shell accounts.

The hook system allowes to add all git provided hooks to the repository
even though you might not need all of them.

""".strip(),
    license="http://creativecommons.org/licenses/MIT/",
    keywords="git scm version-control ssh web management",
    url="http://phoenix.w3agency.net/",
    download_url="http://phoenix.w3agency.net/download/",
    
    zip_safe=False,
    
    entry_points={
        'console_scripts': [
            'phoenix = Phoenix.Controllers:Client',
            'phoenix-admin = Phoenix.Controllers:Admin',
        ]
    },
    
    package_data={
        "Phoenix": ["Conf/phoenix.cfg", "data/hooks/*"]
    }
)
