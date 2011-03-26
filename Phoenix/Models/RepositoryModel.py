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
from Phoenix import Exception
from Phoenix.Conf import Config
from sqlobject import SQLObject, ForeignKey, StringCol, MultipleJoin, events
from string import ascii_letters, digits, Template
from hashlib import sha1
from datetime import datetime
from git import Repo
from os import path, listdir, system, remove
from shutil import move, rmtree

"""----------------------------------------------------------------------------
                                Exception
----------------------------------------------------------------------------"""
class Exception(Exception):
    pass

class RepositoryException(Exception):
    pass

"""----------------------------------------------------------------------------
                                Class
----------------------------------------------------------------------------"""
class Repository(SQLObject):
    member = ForeignKey("Member")
    name = StringCol(length=255)
    path = StringCol(length=255, default=None)
    hash = StringCol(length=40, default=None)
    privileges = MultipleJoin("Privilege")
    hooks = MultipleJoin("Hook")

    def _init(self, *a, **kw):
        SQLObject._init(self, *a, **kw)
        if not self.hash: self._generateHash()
        if not path.exists(self.getFullpath()):
            Repo.init(self.getFullpath(), mkdir=True, bare=True)
            self._initHooks(self.getFullpath())
            self.addPrivilege(".*", ".*", "CRUD", self.member)
            self.addHook("update", "phoenix authorize")

    def _set_path(self, value):
        if not value: value = self.name
        self._SO_set_path(self._sanitizePath(value))
        if hasattr(self, 'id'): self._generateHash()

    def _set_hash(self, value=None):
        if hasattr(self, "id") and self.getFullpath() and path.exists(self.getFullpath()):
            move(self.getFullpath(), self.getFullpath(value))
        self._SO_set_hash(value)

    def _sanitizePath(self, value):
        valid = "-_%s%s" % (ascii_letters, digits)
        path = "".join(c for c in value.replace(" ", "-") if c in valid)
        return path if path.find(".git") != -1 else path + ".git"
        
    def _generateHash(self):
        m = sha1()
        m.update(self.path + datetime.now().isoformat())
        self.hash = m.hexdigest()
        
    def getFullpath(self, hash=None):
        if not hash and not self.hash: return False
        return path.join(Config.get("phoenix", "repository_dir"), hash or self.hash)

    def _initHooks(self, fullpath):
        hooks = path.join(Config.get("ABS_PATH"), Config.get("phoenix", "hook_dir"))
        for f in listdir(hooks):
            t = Template(open(path.join(hooks, f), "r").read())
            open(path.join(fullpath, "hooks", f), "w").write(t.substitute(repo=self.id))
            system("chmod +x " + path.join(fullpath, "hooks", f))
            remove(path.join(fullpath, "hooks", f + ".sample"))

    
    def addPrivilege(self, tag, branch, crud, member=None, role=None, public=False):
        from Phoenix.Models import Privilege
        privilege = Privilege(repository=self, tag=tag, branch=branch, crud=crud,
                              member=member, role=role, public=public)
        return privilege
    
    def addHook(self, hook, command):
        from Phoenix.Models import Hook
        hook = Hook(repository=self, hook=hook, command=command)
        return hook
    
    def getHooksByName(self, name):
        from Phoenix.Models import Hook
        return Hook.selectBy(repository=self, hook=name)
    
    def hasAccess(self, member=False, branch="master", tag="", action="R"):
        from Phoenix.Models import Privilege
        from re import match
        from sqlobject import AND, OR, IN
        if not member:
            privileges = Privilege.selectBy(repository=self, public=True)
        else:
            privileges = Privilege.select(AND(
                            Privilege.q.repository == self.id,
                            OR(
                               Privilege.q.member == member.id,
                               IN(Privilege.q.role, member.roles),
                               Privilege.q.public == 1)))
        print privileges
        if privileges.count() > 0:
            for p in privileges:
                if branch and match(p.branch, branch) and action in p.crud:
                    return True
                if tag and match(p.tag, tag) and action in p.crud:
                    return True
        return False
                    

    @classmethod
    def _beforedestroy(cls, repository, *a):
        for privilege in repository.privileges:
            privilege.destroySelf()
            
        for hook in repository.hooks:
            hook.destroySelf()
        
        rmtree(repository.getFullpath())
        
events.listen(Repository._beforedestroy, Repository, events.RowDestroySignal)
