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
from Phoenix.Conf import Config, logging
from Phoenix.Library import File
from sqlalchemy import Column, Integer
from sqlalchemy.ext.declarative import declarative_base

"""----------------------------------------------------------------------------
                                Exception
----------------------------------------------------------------------------"""
class Exception(Exception):
    pass

class KeyException(Exception):
    pass

class KeyMapperException(Exception):
    pass

"""----------------------------------------------------------------------------
                                Class
----------------------------------------------------------------------------"""
Base = declarative_base()
class Key(Base):
    __tablename__ = "key"
    id = Column(Integer, primary_key=True)
    uid = Column(Integer, nullable=False)
    rid = Column(Integer)
    
    def __init__(self, uid, rid=None, key=None):
        from Phoenix.Library import Validate
        
        if not Validate.user(uid):
            raise KeyException("User with the id `%s' doesn't exist." % uid)
        if rid and not Validate.repository(rid):
            raise KeyException("Repository with the id `%s' doesn't exist." % rid)

        
        self.uid = uid
        self.rid = rid
        self.setKey(key)
    
    def __repr__(self):
        return "<Key('%s', '%s'>" % (self.uid, self.rid)
    
    def setKey(self, key):
        if key and not key.strip():
            raise KeyException("Provided key is not valid.")
        self.key = key
    
    def save(self):
        create = False
        if not self.id:
            create = True
            if not self.key:
                raise KeyException("No key provided, can't create key without key.")
        
        logging.info("Is create: " + str(create))
        sess = Config.getSession()
        sess.add(self)
        sess.commit()
        
        if create:
            self._append()
        else:
            if self.key:
                self._remove()
                self._append()
        
    def delete(self):
        self._remove()
        sess = Config.getSession()
        sess.delete(sess.query(Key).get(self.id))
        sess.commit()
        
    def getUser(self):
        from Phoenix.Models import UserMapper
        return UserMapper.findById(self.uid)
    
    def getRepository(self):
        if not self.rid: return False
        from Phoenix.Models import RepositoryMapper
        return RepositoryMapper.findById(self.rid)
        
    def _prepareKey(self):
        tmp = """command="phoenix serve --key-id %s",""" % self.id
        tmp += "no-port-forwarding,no-x11-forwarding,no-agent-forwarding %s" % self.key
        return tmp
    
    def _append(self):
        File.appendToFile(Config.get("phoenix", "authorized_keys"), self._prepareKey())
        
    def _remove(self):
        logging.info("Removing key `%s' from authorized_keys ..." % self.id)
        File.removeLine(Config.get("phoenix", "authorized_keys"), "--key-id %s" % self.id)    

class KeyMapper(object):
    @classmethod
    def findById(cls, id):
        sess = Config.getSession()
        return sess.query(Key).get(id)
    
    @classmethod
    def findByUid(cls, uid):
        sess = Config.getSession()
        return sess.query(Key).filter(Key.uid == uid).all()
    
    @classmethod
    def findByRid(cls, rid):
        sess = Config.getSession()
        return sess.query(Key).filter(Key.rid == rid).all()
    
