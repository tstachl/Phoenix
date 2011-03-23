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
    @since:        Mar 23, 2011

"""

"""----------------------------------------------------------------------------
                                Imports
----------------------------------------------------------------------------"""
from Phoenix import Exception
from Phoenix.Conf import Config
from sqlalchemy import Column, String, Integer, Boolean, ForeignKey
from sqlalchemy.ext.declarative import declarative_base

"""----------------------------------------------------------------------------
                                Exception
----------------------------------------------------------------------------"""
class Exception(Exception):
    pass

class RuleException(Exception):
    pass

class RuleMapperException(Exception):
    pass

"""----------------------------------------------------------------------------
                                Class
----------------------------------------------------------------------------"""
Base = declarative_base()
class Rule(Base):
    __tablename__ = "rule"
    id = Column(Integer, primary_key=True)
    rid = Column(Integer, ForeignKey("repository.id"), nullable=False)
    tag = Column(String, nullable=False)
    branch = Column(String, nullable=False)
    crud = Column(String, nullable=False)
    uid = Column(Integer, ForeignKey("user.id"))
    gid = Column(Integer, ForeignKey("group.id"))
    pub = Column(Boolean)
    
    def __init__(self, rid, tag, branch, crud, uid=None, gid=None, pub=False):
        from Phoenix.Library import Validate
        if not Validate.repository(rid):
            raise RuleException("Repository with id `%s' doesn't exist." % rid)
        
        if uid and not Validate.user(uid):
            raise RuleException("User with id `%s' doesn't exist." % uid)
        
        if gid and not Validate.group(gid):
            raise RuleException("Group with id `%s' doesn't exist." % gid)
        
        self.rid = rid
        self.tag = tag
        self.branch = branch
        self.crud = crud
        self.uid = uid
        self.gid = gid
        self.pub = pub
    
    def __repr__(self):
        return "<Rule('%s', '%s', '%s', '%s', '%s', '%s', '%s'>" % (self.rid, self.tag, self.branch,
                                                                    self.crud, self.uid, self.gid,
                                                                    self.pub)
    
    def save(self):
        sess = Config.getSession()
        sess.add(self)
        sess.commit()
        
    def delete(self):
        sess = Config.getSession()
        sess.delete(sess.query(Rule).get(self.id))
        sess.commit()

class RuleMapper(object):
    @classmethod
    def findById(cls, id):
        sess = Config.getSession()
        return sess.query(Rule).get(id)
        
    @classmethod
    def findByRid(cls, rid):
        sess = Config.getSession()
        return sess.query(Rule).filter(Rule.rid == rid).all()
    
