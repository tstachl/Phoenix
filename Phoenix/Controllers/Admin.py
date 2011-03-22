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
from Phoenix.Models import User, UserMapper, KeyMapper, HookMapper
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
        addkey.add_argument("-n", "--repository-name", help="The name of the repository the key should be added to")
        addkey.add_argument("-p", "--repository-path", help="Optional, sometimes the path is shorter than the name")

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
        sql = self.args.sql_connect or "sqlite:///%s" % path.join(Config.get("ABS_PATH"), "data/phoenix.db")
        
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
        
        self._createDatabase()
            
        self._createDirectoryStructure(repo, tar, ssh)

        logging.info("Creating `%s' ..." % auth_keys)
        File.touch(auth_keys)
        Config.set("phoenix", "authorized_keys", auth_keys)
        
        logging.info("Saving admin user information `%s' and `%s' in database ..." % (name, email))
        admin = User(username, email, name)
        admin.save()
        
        if dev:
            logging.info("Initializing development repository at `%s/phoenix.git' ..." % repo)
            Config.set("phoenix", "develop_me", dev)
            admin.createRepository("Phoenix Server Management", "phoenix")
        
        Config.set("phoenix", "initialized", True)
        print "Done."
        
    def adduser(self):
        logging.info("Defining username, name and email ...")
        username = self.args.username
        name = self.args.name
        email = self.args.email
        
        dummy = self._getUserByUsernameOrEmail(username, email)
        
        logging.info("Creating and saving the new user ...")
        user = User(username, email, name)
        user.save()
        
        print "Done."
        
    def addrepo(self):
        logging.info("Defining username, email and repository name ...")
        username = self.args.username
        email = self.args.email
        name = self.args.repository_name
        path = self.args.repository_path
        
        user = self._getUserByUsernameOrEmail(username, email, True)
        dummy = self._getRepositoryByNameOrPath(user, name, path)

        logging.info("Changing to the git user ...")
        __import__("os").setgid(__import__("pwd").getpwnam(Config.get("phoenix", "user")).pw_gid)
        __import__("os").setuid(__import__("pwd").getpwnam(Config.get("phoenix", "user")).pw_uid)
        
        logging.info("Creating and saving the new repository ...")
        user.createRepository(name, path)
        
        print "Done."
        
    def addkey(self):
        logging.info("Read the key ...")
        key = __import__("sys").stdin.readline().strip()
        if key == "":
            raise Exception("Key can not be empty.")
        
        logging.info("Define username, email and repository ...")
        email = self.args.email
        username = self.args.username
        name = self.args.repository_name
        path = self.args.repository_path
        
        user = self._getUserByUsernameOrEmail(username, email, True)
        repo = self._getRepositoryByNameOrPath(user, name, path)
        
        logging.info("Save new key in database ...")
        if repo: repo.createKey(key)
        else: user.createKey(key)
        
        print "Done."
        
    def addhook(self):
        logging.info("Defining username, email, repository name, hook and command ...")
        username = self.args.username
        email = self.args.email
        name = self.args.repository_name
        path = self.args.repository_path
        hook = self.args.hook
        command = self.args.command
        
        user = self._getUserByUsernameOrEmail(username, email, True)
        repo = self._getRepositoryByNameOrPath(user, name, path, True)
        
        logging.info("Save new hook in database ...")
        repo.createHook(hook, command)
        
        print "Done."
        
    def removeuser(self):
        logging.info("Defining email and username ...")
        email = self.args.email
        username = self.args.username
        
        user = self._getUserByUsernameOrEmail(username, email, True)
        
        logging.info("Removing the user from the database ...")
        user.delete()
        
        print "Done."
        
    def removerepo(self):
        logging.info("Defining repository name, email and username ...")
        email = self.args.email
        username = self.args.username
        name = self.args.repository_name
        path = self.args.repository_path

        user = self._getUserByUsernameOrEmail(username, email, True)
        repo = self._getRepositoryByNameOrPath(user, name, path, True)
        
        logging.info("Removing the repository ...")
        repo.delete()
        
        print "Done."
        
    def removekey(self):
        logging.info("Defining key id ...")
        id = self.args.key_id
        
        logging.info("Checking if the key exists ...")
        key = KeyMapper.findById(id)
        
        if not key:
            raise Exception("The key with the id `%s' does not exits." % id)
                
        logging.info("Removing the key from the database ...")
        key.delete()
        
        print "Done."
        
    def removehook(self):
        logging.info("Defining hook id ...")
        id = self.args.hook_id
        
        logging.info("Checking if hook exists ...")
        hook = HookMapper.findById(id)
        
        if not hook:
            raise Exception("The hook with the id `%s' does not exist." % id)
        
        logging.info("Removing the hook from the database ...")
        hook.delete()
        
        print "Done."
        
    def _getUserByUsernameOrEmail(self, username, email, must=False):        
        logging.info("Trying to find the user by username or email ...")
        user = None
        if username:
            user = UserMapper.findByUsername(username)
        if email:
            user = UserMapper.findByEmail(email)
                
        logging.info("Checking if we have a user ...")
        if must and not user:
            raise AdminException("The user can not be found (username: `%s', email: `%s')" % (username, email))
        if not must and user:
            raise AdminException("The user `%s' with email `%s' already exists." % (user.username, user.email))
        
        return user
    
    def _getRepositoryByNameOrPath(self, user, name, path, must=False):
        repo = None
        logging.info("Trying to find a repository by name or path ...")
        if name:
            repo = user.getRepositoryByName(name)
        if path:
            repo = user.getRepositoryByPath(path)
            
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

    def _createDatabase(self):
        from sqlalchemy import MetaData, Table, Column, Integer, String
        metadata = MetaData()
        Table("user", metadata,
            Column("id", Integer, primary_key=True),
            Column("username", String, nullable=False),
            Column("name", String, nullable=True),
            Column("email", String, nullable=False),
        )
        Table("repository", metadata,
            Column("id", Integer, primary_key=True),
            Column("uid", Integer, nullable=False),
            Column("name", String, nullable=False),
            Column("path", String, nullable=False),
            Column("hash", String, nullable=False),
        )
        Table("key", metadata,
            Column("id", Integer, primary_key=True),
            Column("uid", Integer, nullable=False),
            Column("rid", Integer),
        )
        Table("hook", metadata,
            Column("id", Integer, primary_key=True),
            Column("rid", Integer, nullable=False),
            Column("hook", String, nullable=False),
            Column("command", String, nullable=False),
        )
        metadata.create_all(Config.getEngine())
