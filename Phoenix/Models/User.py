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
from Phoenix.Library import Validate
from Phoenix.Conf import Config
from Phoenix.Models import RepositoryMapper, KeyMapper, Repository, Key
from sqlalchemy import Column, String, Integer
from sqlalchemy.ext.declarative import declarative_base

"""----------------------------------------------------------------------------
                                Exception
----------------------------------------------------------------------------"""
class Exception(Exception):
    pass

class UserException(Exception):
    pass

class UserMapperException(Exception):
    pass

"""----------------------------------------------------------------------------
                                Class
----------------------------------------------------------------------------"""
Base = declarative_base()
class User(Base):
    __tablename__ = "user"
    id = Column(Integer, primary_key=True)
    username = Column(String, nullable=False)
    email = Column(String, nullable=False)
    name = Column(String, nullable=True)
    
    def __init__(self, username, email, name=None):
        if Validate.username(username):
            self.username = username
        else:
            raise UserException("Username `%s' is not valid." % username)
        
        self.name = name
        
        if Validate.email(email):
            self.email = email
        else:
            raise UserException("Email `%s' is not valid." % email)
        
    def __repr__(self):
        return "<User('%s', '%s', '%s'>" % (self.username, self.name, self.email)
    
    def save(self):
        sess = Config.getSession()
        sess.add(self)
        sess.commit()
        
    def delete(self):
        for repo in self.getRepositories():
            repo.delete()
        for key in self.getKeys():
            key.delete()
        sess = Config.getSession()
        sess.delete(self)
        sess.commit()
        
    def createRepository(self, name, path=None):
        repo = Repository(self.id, name, path)
        repo.save()
        return repo
        
    def createKey(self, key):
        key = Key(self.id, key)
        key.save()
        return key
        
    def getRepositories(self):
        return RepositoryMapper.findByUid(self.id)
    
    def getKeys(self):
        return KeyMapper.findByUid(self.id)
    
    def getRepositoryByName(self, name):
        return RepositoryMapper.findByName(self.id, name)
    
    def getRepositoryByPath(self, path):
        return RepositoryMapper.findByPath(self.id, path)

class UserMapper(object):
    
    @classmethod
    def findById(cls, id):
        sess = Config.getSession()
        return sess.query(User).get(id)
    
    @classmethod
    def findByEmail(cls, email):
        if not Validate.email(email):
            raise UserMapperException("Email `%s' not valid." % email)
        sess = Config.getSession()
        return sess.query(User).filter(User.email == email).first()
    
    @classmethod
    def findByUsername(cls, username):
        if not Validate.username(username):
            raise UserMapperException("Username `%s' not valid." % username)
        sess = Config.getSession()
        return sess.query(User).filter(User.username == username).first()
    
