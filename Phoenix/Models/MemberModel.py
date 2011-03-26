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
from sqlobject import SQLObject, StringCol, RelatedJoin, MultipleJoin, events

"""----------------------------------------------------------------------------
                                Exception
----------------------------------------------------------------------------"""
class Exception(Exception):
    pass

class MemberException(Exception):
    pass

"""----------------------------------------------------------------------------
                                Class
----------------------------------------------------------------------------"""
class Member(SQLObject):
    username = StringCol(alternateID=True, length=20)
    email = StringCol(alternateID=True, length=254)
    name = StringCol(length=255, default=None)
    ownedroles = MultipleJoin("Role")
    roles = RelatedJoin("Role")
    repositories = MultipleJoin("Repository")
    privileges = MultipleJoin("Privilege")
    keys = MultipleJoin("Key")
    
    def addRepository(self, name, path=None):
        from Phoenix.Models import Repository
        repo = Repository(member=self, name=name, path=path)
        return repo
    
    def addRole(self, name):
        from Phoenix.Models import Role
        role = Role(name=name, member=self)
        return role
    
    def addKey(self, key):
        from Phoenix.Models import Key
        key = Key(member=self, pubkey=key)
        return key
    
    def removeKey(self, key):
        key.destroySelf()
        
    def repositoryByName(self, name):
        from Phoenix.Models import Repository
        try:
            return Repository.selectBy(member=self, name=name)[0]
        except IndexError:
            return None
    
    def repositoryByPath(self, path):
        from Phoenix.Models import Repository
        try:
            return Repository.selectBy(member=self, path=path)[0]
        except IndexError:
            return None

    @classmethod
    def _beforedestroy(cls, member, *a):
        for role in member.ownedroles:
            role.destroySelf()
        
        for repository in member.repositories:
            repository.destroySelf()
            
        for key in member.keys:
            key.destroySelf()
        
events.listen(Member._beforedestroy, Member, events.RowDestroySignal)
