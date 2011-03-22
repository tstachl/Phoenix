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
from sqlalchemy import Column, String, Integer, and_
from sqlalchemy.ext.declarative import declarative_base
from git import Repo
from shutil import rmtree, move
from os import path, listdir, system, remove
from string import ascii_letters, digits, Template
from hashlib import sha1
from datetime import datetime

"""----------------------------------------------------------------------------
                                Exception
----------------------------------------------------------------------------"""
class Exception(Exception):
    pass

class RepositoryException(Exception):
    pass

class RepositoryMapperException(Exception):
    pass

"""----------------------------------------------------------------------------
                                Class
----------------------------------------------------------------------------"""
Base = declarative_base()
class Repository(Base):
    __tablename__ = "repository"
    id = Column(Integer, primary_key=True)
    uid = Column(Integer, nullable=False)
    name = Column(String, nullable=False)
    path = Column(String, nullable=False)
    hash = Column(String, nullable=False)
    
    def __init__(self, uid, name, path=None, hash=None):
        from Phoenix.Library import Validate
        if Validate.user(uid):
            self.uid = uid
        else:
            raise Exception()
        self.name = name
        self.setPath(path)
        self.hash = hash
    
    def __repr__(self):
        return "<Repository('%s', '%s', '%s', '%s'>" % (self.uid, self.name, self.path, self.hash)

    def setPath(self, path):
        path = path if path else self._sanitizePath()
        if path.find(".git") == -1:
            path += ".git"
        self.path = path

    def save(self):
        hooks = False
        if not self.id:
            self._hashPath()
            Repo.init(self.getFullpath(), mkdir=True, bare=True)
            hooks = True
        else:        
            self._checkChanges(RepositoryMapper.findById(self.id))
            
        sess = Config.getSession()
        sess.add(self)
        sess.commit()
        
        if hooks:
            self._addHooks()
    
    def delete(self):
        self._remove()
        for key in self.getKeys():
            key.delete()
        for hook in self.getHooks():
            hook.delete()
        sess = Config.getSession()
        sess.delete(sess.query(Repository).get(self.id))
        sess.commit()
        
    def getFullpath(self):
        return path.join(Config.get("phoenix", "repository_dir"), self.hash)
        
    def createHook(self, hook, command):
        from Phoenix.Models import Hook
        hook = Hook(self.id, hook, command)
        hook.save()
        return hook
        
    def createKey(self, key):
        from Phoenix.Models import Key
        key = Key(self.uid, self.id, key)
        key.save()
        return key
        
    def getKeys(self):
        from Phoenix.Models import KeyMapper
        return KeyMapper.findByRid(self.id)
    
    def getHooks(self):
        from Phoenix.Models import HookMapper
        return HookMapper.findByRid(self.id)
    
    def getUser(self):
        from Phoenix.Models import UserMapper
        return UserMapper.findById(self.uid)
        
    def getHooksByName(self, hook):
        from Phoenix.Models import HookMapper
        return HookMapper.findByRidAndHook(self.id, hook)
        
    def _remove(self):
        rmtree(self.getFullpath())

    def _sanitizePath(self):
        valid = "-_%s%s" % (ascii_letters, digits)
        return "".join(c for c in self.name.replace(" ", "-") if c in valid) + ".git"

    def _hashPath(self):
        m = sha1()
        m.update(self.path + datetime.now().isoformat())
        self.hash = m.hexdigest()
        
    def _checkChanges(self, old):
        if not old.path == self.path:
            self._hashPath()
            move(old.getFullpath(), self.getFullpath())
            
    def _addHooks(self):
        hooks = path.join(Config.get("ABS_PATH"), Config.get("phoenix", "hook_dir"))
        for f in listdir(hooks):
            t = Template(open(path.join(hooks, f), "r").read())
            open(path.join(self.getFullpath(), "hooks", f), "w").write(t.substitute(repo=self.id))
            system("chmod +x " + path.join(self.getFullpath(), "hooks", f))
            remove(path.join(self.getFullpath(), "hooks", f + ".sample"))

class RepositoryMapper(object):
    
    @classmethod
    def findById(cls, id):
        sess = Config.getSession()
        return sess.query(Repository).get(id)
    
    @classmethod
    def findByUid(cls, uid):
        sess = Config.getSession()
        return sess.query(Repository).filter(Repository.uid == uid).all()
    
    @classmethod
    def findByName(cls, uid, name):
        sess = Config.getSession()
        return sess.query(Repository).filter(and_(
            Repository.name == name,
            Repository.uid == uid
        )).first()

    @classmethod
    def findByPath(cls, uid, path):
        sess = Config.getSession()
        return sess.query(Repository).filter(and_(
            Repository.uid == uid,
            Repository.path == path
        )).first()
