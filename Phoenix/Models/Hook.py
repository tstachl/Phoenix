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

"""----------------------------------------------------------------------------
                                Exception
----------------------------------------------------------------------------"""
class Exception(Exception):
    pass

class HookException(Exception):
    pass

class HookMapperException(Exception):
    pass

"""----------------------------------------------------------------------------
                                Class
----------------------------------------------------------------------------"""
Base = declarative_base()
class Hook(Base):
    __tablename__ = "hook"
    id = Column(Integer, primary_key=True)
    rid = Column(Integer, nullable=False)
    hook = Column(String, nullable=False)
    command = Column(String, nullable=False)
    
    def __init__(self, rid, hook, command):
        from Phoenix.Library import Validate
        if not Validate.repository(rid):
            raise HookException("Repository with id `%s' doesn't exist." % rid)
        
        if not Validate.hookName(hook):
            raise HookException("Hook with the name `%s' doesn't exist." % hook)
        
        self.rid = rid
        self.hook = hook
        self.command = command
    
    def __repr__(self):
        return "<Hook('%s', '%s', '%s'>" % (self.rid, self.hook, self.command)
    
    def save(self):
        sess = Config.getSession()
        sess.add(self)
        sess.commit()
        
    def delete(self):
        sess = Config.getSession()
        sess.delete(sess.query(Hook).get(self.id))
        sess.commit()

class HookMapper(object):
    @classmethod
    def findById(cls, id):
        sess = Config.getSession()
        return sess.query(Hook).get(id)
        
    @classmethod
    def findByRid(cls, rid):
        sess = Config.getSession()
        return sess.query(Hook).filter(Hook.rid == rid).all()
    
    @classmethod
    def findByRidAndHook(cls, rid, hook):
        sess = Config.getSession()
        return sess.query(Hook).filter(and_(
            Hook.rid == rid,
            Hook.hook == hook
        )).all()
