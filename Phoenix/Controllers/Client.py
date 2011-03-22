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
    @since:        Mar 18, 2011

"""

"""----------------------------------------------------------------------------
                                Imports
----------------------------------------------------------------------------"""
from Phoenix.Conf import Config, logging
from Phoenix.Library import Console, Validate
from Phoenix.Models import KeyMapper, UserMapper, RepositoryMapper
from socket import gethostname
from subprocess import Popen
from shlex import split
import os

"""----------------------------------------------------------------------------
                                Exception
----------------------------------------------------------------------------"""
class Exception(Exception):
    pass

class ClientException(Exception):
    pass

"""----------------------------------------------------------------------------
                                Class
----------------------------------------------------------------------------"""
class Client(Console):
    
    def __init__(self):        
        if not os.getuid() == __import__("pwd").getpwnam(Config.get("phoenix", "user")).pw_uid:
            raise ClientException("Only `%s' can run this script" % Config.get("phoenix", "user"))
        super(Client, self).__init__()
        
    def defineParser(self, parser):
        subparsers = parser.add_subparsers(dest='action', title="Phoenix Client Commands",
                                           description="Valid commands to use with phoenix")
        serve = subparsers.add_parser("serve", help="Serves git repositories")
        serve.add_argument("-k", "--key-id", help="The key which is requesting access", required=True)
        
        runhook = subparsers.add_parser("runhook", help="This action will be call from each hook of the repository")
        runhook.add_argument("-k", "--hook", help="The hook to run")
        runhook.add_argument("-r", "--repository-id", help="The repository to run it for.")
        runhook.add_argument("-a", "--arguments", help="The original arguments.")
        
    def serve(self):
        logging.disable(logging.INFO)
        
        key = KeyMapper.findById(self.args.key_id)
        userKey = key.getUser()
        repoKey = key.getRepository()
        
        if not os.environ.get("SSH_ORIGINAL_COMMAND"):
            print "Hi %s!" % userKey.username
            print "You've successfully authenticated, but %s does not provide shell access." % Config.get("phoenix", "app_name", "Phoenix")
            print "Use the following command to clone a repository:"
            print "    > git clone git@%s:%s/repository.git" % (gethostname(), userKey.username)
            return False
        else:
            (command, path) = os.environ.get("SSH_ORIGINAL_COMMAND").replace("'", "").split()
            if not Validate.gitcommand(command):
                raise Exception(command)
                print "Hi %s!" % userKey.username
                print "You've successfully authenticated, but %s does not provide shell access." % Config.get("phoenix", "app_name", "Phoenix")
                print "Use the following command to clone a repository:"
                print "    > git clone git@%s:%s/repository.git" % (gethostname(), userKey.username)
                return False
            
        (username, repopath) = path.split("/")
        user = UserMapper.findByUsername(username)
        repo = user.getRepositoryByPath(repopath)
        
        if not repo:
            logging.error("Repository `%s' not found but requested ..." % path)
            raise ClientException("You are not allowed in this repository!")
        
        if repoKey:
            if repoKey.id == repo.id:
                __import__("os").execvp("git", ["git", "shell", "-c", "%s '%s'" % (command, repo.getFullpath())])
            else:
                logging.error("User `%s' tried to access repository `%s' ..." % (userKey.id, repo.id))
                raise ClientException("You are not allowed in this repository!")
        else:
            if userKey.id == repo.uid:
                __import__("os").execvp("git", ["git", "shell", "-c", "%s '%s'" % (command, repo.getFullpath())])
            else:
                logging.error("User `%s' tried to access repository `%s' ..." % (userKey.id, repo.id))
                raise ClientException("You are not allowed in this repository!")
    
    def runhook(self):   
        logging.disable(logging.INFO)     
        logging.info("Defining hook, repo and arguments ...")
        repo = RepositoryMapper.findById(self.args.repository_id)
        arguments = " " + self.args.arguments if self.args.arguments else ""
        
        logging.info("Looking up all hooks for repository `%s' and hook `%s' ..." % (repo.id, self.args.hook))
        for hook in repo.getHooksByName(self.args.hook):
            logging.info("Running command `%s' ..." % hook.command + arguments)
            Popen(split(str(hook.command + arguments)))
            
