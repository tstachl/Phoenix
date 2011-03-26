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
    @since:        Mar 17, 2011

"""

"""----------------------------------------------------------------------------
                                Imports
----------------------------------------------------------------------------"""
from Phoenix.Conf import Config, logging
from Phoenix.Library import Console, SysUser, File
from Phoenix.Models import Member, Key, Hook
from os import path, mkdir

"""----------------------------------------------------------------------------
                                Exception
----------------------------------------------------------------------------"""
class Exception(Exception):
    pass

class AdminException(Exception):
    pass

"""----------------------------------------------------------------------------
                                Class
----------------------------------------------------------------------------"""
class Admin(Console):
    
    def __init__(self):
        if not __import__("os").getuid() == 0:
            raise AdminException("Only root can run this script")
        super(Admin, self).__init__()
    
    def defineParser(self, parser):
        subparsers = parser.add_subparsers(dest='action', title="Phoenix Admin Commands",
                                           description="Valid commands to use with phoenix-admin")
        init = subparsers.add_parser("init", help="Initalize and configure Phoenix")
        init.add_argument("-e", "--admin-email", help="The email address of the administrator", required=True)
        init.add_argument("-n", "--admin-name", help="The name of the administrator")
        init.add_argument("-a", "--admin-username", help="The username of the administrator", default="admin")
        init.add_argument("-u", "--git-user", help="User which is running the git daemon", default="git")
        init.add_argument("-b", "--base-dir", help="base directory for the home directory of the user [/home]", default="/home")
        init.add_argument("--repository-dir", help="The path where git repositories are stored [$base-dir/repositories]", default="repositories")
        init.add_argument("--tarball-dir", help="The path where generated tarballs are stored [$base-dir/tarballs]", default="tarballs")
        init.add_argument("-s", "--sql-connect", help="The connection string for the database to use [sqlite:///$BASE_DIR/phoenix.db]")
        init.add_argument("-d", "--develop-me", action="store_const", const=True, help="If this flag is set, the source code of this application will initialize itself as a git repository and will become developable")

        adduser = subparsers.add_parser("adduser", help="Add a new user to the database")
        adduser.add_argument("-u", "--username", help="The new users username", required=True)
        adduser.add_argument("-e", "--email", help="The new users email address", required=True)
        adduser.add_argument("-n", "--name", help="The new users name")

        addrepo = subparsers.add_parser("addrepo", help="Add a repository")
        addrepo.add_argument("-n", "--repository-name", help="The name of the new repository", required=True)
        addrepo.add_argument("-p", "--repository-path", help="Optional, by default the path is the sanitized name of the repository")
        addrepo.add_argument("-u", "--username", help="Username of the owner (use email if not known)")
        addrepo.add_argument("-e", "--email", help="Email of the owner (if username not known)")

        addkey = subparsers.add_parser("addkey", help="Add a new key to a user or a deploy key to a repository")
        addkey.add_argument("-e", "--email", help="The email of the user the key should be added to")
        addkey.add_argument("-u", "--username", help="The username of the user the key should be added to")
        
        addhook = subparsers.add_parser("addhook", help="Add a hook to a repository.")
        addhook.add_argument("-k", "--hook", help="The hook you want to add", required=True)
        addhook.add_argument("-c", "--command", help="The command to execute on this hook", required=True)
        addhook.add_argument("-n", "--repository-name", help="The name of the repository for the new hook")
        addhook.add_argument("-p", "--repository-path", help="Optional, sometimes the path is shorter than the name")
        addhook.add_argument("-e", "--email", help="The email of the owner of the repository")
        addhook.add_argument("-u", "--username", help="The username of the owner of the repository")
        
        removeuser = subparsers.add_parser("removeuser", help="Remove a user (deletes all repositories and keys too)")
        removeuser.add_argument("-u", "--username", help="The username of the user who shall be removed")
        removeuser.add_argument("-e", "--email", help="The email address of the user who shall be removed")
        
        removerepo = subparsers.add_parser("removerepo", help="Remove a repository from the filesystem and database")
        removerepo.add_argument("-n", "--repository-name", help="The name of the repository which should be deleted")
        removerepo.add_argument("-p", "--repository-path", help="Optional, sometimes the path is shorter than the name")
        removerepo.add_argument("-e", "--email", help="The email of the owner of the repository which should be deleted")
        removerepo.add_argument("-u", "--username", help="The username of the owner of the repository which should be deleted")
        
        removekey = subparsers.add_parser("removekey", help="Removes a key from the key file and database")
        removekey.add_argument("-i", "--key-id", help="The id of the key to remove", required=True)

        removehook = subparsers.add_parser("removehook", help="Remove a hook from a repository")
        removehook.add_argument("-i", "--hook-id", help="The id of the hook to remove", required=True)

        debug = subparsers.add_parser("debug")

    def init(self):
        if Config.get("phoenix", "initialized") == "True":
            raise AdminException("Already initialized.")
        
        logging.info("Defining variables for init ...")
        user = self.args.git_user
        base = path.join(self.args.base_dir, user)
        repo = path.join(base, self.args.repository_dir)
        tar = path.join(base, self.args.tarball_dir)
        ssh = path.join(base, ".ssh")
        auth_keys = path.join(ssh, "authorized_keys")
        dev = self.args.develop_me
        email = self.args.admin_email
        name = self.args.admin_name
        username = self.args.admin_username
        sql = self.args.sql_connect or "sqlite://%s" % path.join(Config.get("ABS_PATH"), "data/phoenix.db")
        
        logging.info("Checking for permission to write the config file ...")
        if not File.writePermission(Config.get("CONF_FILE")):
            raise AdminException("You don't have permission to write the config file `%s' ..." % Config.get("CONF_FILE"))
        
        if not SysUser.exists(self.args.git_user):
            logging.info("Creating user `%s' ... " % user)
            SysUser.create(user, base)
            Config.set("phoenix", "user", user)
            Config.set("phoenix", "base", base)
        else:
            raise AdminException("The user `%s' already exists." % user)
        
        __import__("os").setgid(__import__("pwd").getpwnam(user).pw_gid)
        __import__("os").setuid(__import__("pwd").getpwnam(user).pw_uid)
        
        logging.info("Checking for permission to write the config file as `%s' ...")
        if not File.writePermission(Config.get("CONF_FILE")):
            raise AdminException("You don't have permission to write the config file `%s' ..." % Config.get("CONF_FILE"))
        
        logging.info("Saving SQL connection string `%s' ..." % sql)
        Config.set("phoenix", "sql_connect", sql)
        
        from sqlobject import connectionForURI, sqlhub
        connection = connectionForURI(Config.get("phoenix", "sql_connect"))
        sqlhub.processConnection = connection
        
        self._sqlChanges()
        self._createDirectoryStructure(repo, tar, ssh)

        logging.info("Creating `%s' ..." % auth_keys)
        File.touch(auth_keys)
        Config.set("phoenix", "authorized_keys", auth_keys)
        
        logging.info("Saving admin user information `%s' and `%s' in database ..." % (name, email))
        admin = Member(username=username, email=email, name=name)
        
        if dev:
            logging.info("Initializing development repository at `%s/phoenix.git' ..." % repo)
            Config.set("phoenix", "develop_me", dev)
            admin.addRepository("Phoenix Server Management", "phoenix.git")
        
        Config.set("phoenix", "initialized", True)
        print "Done."
        
    def adduser(self):
        logging.info("Defining username, name and email ...")
        username = self.args.username
        name = self.args.name
        email = self.args.email
        
        dummy = self._getMemberByUsernameOrEmail(username, email)
        
        logging.info("Creating and saving the new user ...")
        Member(username=username, email=email, name=name)
        
        print "Done."
        
    def addrepo(self):
        logging.info("Defining username, email and repository name ...")
        username = self.args.username
        email = self.args.email
        name = self.args.repository_name
        path = self.args.repository_path
        
        member = self._getMemberByUsernameOrEmail(username, email, True)
        dummy = self._getRepositoryByNameOrPath(member, name, path)

        logging.info("Changing to the git user ...")
        __import__("os").setgid(__import__("pwd").getpwnam(Config.get("phoenix", "user")).pw_gid)
        __import__("os").setuid(__import__("pwd").getpwnam(Config.get("phoenix", "user")).pw_uid)
        
        logging.info("Creating and saving the new repository ...")
        member.addRepository(name, path)
        
        print "Done."
        
    def addkey(self):
        logging.info("Read the key ...")
        key = __import__("sys").stdin.readline().strip()
        if key == "":
            raise Exception("Key can not be empty.")
        
        logging.info("Define username, email and repository ...")
        email = self.args.email
        username = self.args.username
        
        member = self._getMemberByUsernameOrEmail(username, email, True)
        
        logging.info("Save new key in database ...")
        member.addKey(key)
        
        print "Done."
        
    def addhook(self):
        logging.info("Defining username, email, repository name, hook and command ...")
        username = self.args.username
        email = self.args.email
        name = self.args.repository_name
        path = self.args.repository_path
        hook = self.args.hook
        command = self.args.command
        
        member = self._getMemberByUsernameOrEmail(username, email, True)
        repo = self._getRepositoryByNameOrPath(member, name, path, True)
        
        logging.info("Save new hook in database ...")
        repo.addHook(hook, command)
        
        print "Done."
        
    def removeuser(self):
        logging.info("Defining email and username ...")
        email = self.args.email
        username = self.args.username
        
        member = self._getMemberByUsernameOrEmail(username, email, True)
        
        logging.info("Removing the user from the database ...")
        member.destroySelf()
        
        print "Done."
        
    def removerepo(self):
        logging.info("Defining repository name, email and username ...")
        email = self.args.email
        username = self.args.username
        name = self.args.repository_name
        path = self.args.repository_path

        member = self._getMemberByUsernameOrEmail(username, email, True)
        repo = self._getRepositoryByNameOrPath(member, name, path, True)
        
        logging.info("Removing the repository ...")
        repo.destroySelf()
        
        print "Done."
        
    def removekey(self):
        logging.info("Defining key id ...")
        id = self.args.key_id
        
        logging.info("Checking if the key exists ...")
        key = Key.get(id)
        
        if not key:
            raise Exception("The key with the id `%s' does not exits." % id)
                
        logging.info("Removing the key from the database ...")
        key.destroySelf()
        
        print "Done."
        
    def removehook(self):
        logging.info("Defining hook id ...")
        id = self.args.hook_id
        
        logging.info("Checking if hook exists ...")
        hook = Hook.get(id)
        
        if not hook:
            raise Exception("The hook with the id `%s' does not exist." % id)
        
        logging.info("Removing the hook from the database ...")
        hook.destroySelf()
        
        print "Done."
        
    def _getMemberByUsernameOrEmail(self, username, email, must=False):        
        logging.info("Trying to find the user by username or email ...")
        member = None
        try:
            if username:
                member = Member.selectBy(username=username)[0]
            if email:
                member = Member.selectBy(email=email)[0]
        except IndexError:
            if must and not member:
                raise AdminException("The user can not be found (username: `%s', email: `%s')" % (username, email))
        if not must and member:
            raise AdminException("The user `%s' with email `%s' already exists." % (member.username, member.email))
        
        return member
    
    def _getRepositoryByNameOrPath(self, member, name, path, must=False):
        repo = None
        logging.info("Trying to find a repository by name or path ...")
        if name:
            repo = member.repositoryByName(name)
        if path:
            repo = member.repositoryByPath(path)
            
        if must and not repo:
            raise AdminException("Repository with name `%s' or path `%s' can not be found." % (name, path))
        elif not must and repo:
            raise AdminException("The repository `%s' already exists." % repo.name)
            
        return repo
        
    def _createDirectoryStructure(self, repo, tar, ssh):
        if not path.exists(repo):
            logging.info("Creating repository dir at `%s' ..." % repo)
            mkdir(repo)
        else:
            logging.warning("The folder `%s' already exists." % repo)
        Config.set("phoenix", "repository_dir", repo)
        
        if not path.exists(tar):
            logging.info("Creating tarball dir at `%s' ..." % tar)
            mkdir(tar)
        else:
            logging.warning("The folder `%s' already exists." % tar)
        Config.set("phoenix", "tarball_dir", tar)
        
        if not path.exists(ssh):
            logging.info("Creating ssh dir at `%s' ..." % ssh)
            mkdir(ssh, 0700)
        else:
            logging.warning("The folder `%s' already exists." % ssh)
        Config.set("phoenix", "ssh_dir", ssh)
        
    def _sqlChanges(self):
        from Phoenix.Models import Privilege, Repository, Role
        Member.createTable(ifNotExists=True)
        Role.createTable(ifNotExists=True)
        Repository.createTable(ifNotExists=True)
        Privilege.createTable(ifNotExists=True)
        Hook.createTable(ifNotExists=True)
        Key.createTable(ifNotExists=True)

    def debug(self):
        print Config.get("ABS_PATH")
        print Config.get("phoenix", "hook_dir")
