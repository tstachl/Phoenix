#Phoenix
Phoenix is an open source software to setup and manage servers. It offers
to install and operate all necessery software for web server, mail server
development and production environments. Documentation and downlods are
available at http://phoenix.w3agency.net/

Phoenix is licensed under the MIT Licence
(http://creativecommons.org/licenses/MIT/).

##Installation
To install:

    python setup.py build
    sudo python setup.py install

Phoenix has been tested on Ubuntu 10.04 and Ubuntu 10.10 with Python 2.6.

##First Steps
1. **Initialize Phoenix**

        sudo phoenix-admin init --admin-email you@yourhost.com
    **Please use --help to find out what other options you have!**

2. **Add the key for the administrator**

        sudo phoenix-admin addkey --email you@yourhost.com < /tmp/myPubKey.pub
    **You can also add a deploy key to a specific repository (use --help).**

3. **Add a new repository**

        sudo phoenix-admin addrepo --email you@yourhost.com --repository-name Repo1

4. **Connect your local repository**

        git remote add origin git@yourhost.com:admin/Repo1.git
        
##Commands

###phoenix-admin
    init
        * -e --admin-email
          -n --admin-name
          -a --admin-username [admin]
          -u --git-user [git]
          -b --base-dir [/home]
          --repository-dir [repositories]
          --tarball-dir [tarballs
          -s --sql-connect [$base/phonix.db]
          -d --develop-me [NO]
    adduser
        * -u --username
        * -e --email
          -n --name
    addrepo
        * -n --repository-name
          -p --repository-path
          -e --email
          -u --username
    addkey
          -e --email
          -u --username
          -n --repository-name
          -p --repository-path
    addhook
        * -k --hook
        * -c --command
          -n --repository-name
          -p --repository-path
          -e --email
          -u --username
    removeuser
          -e --email
          -u --username
    removerepo
          -n --repository-name
          -p --repository-path
          -u --username
          -e --email
    removekey
        * -i --key-id
    removehook
        * -i --hook-id

        
*** Required arguments.**
Sometimes you have repository name and path only one of them is mandatory
but it will raise an exception if the repository can not be found. This is
also true for the actions where you have username and email.