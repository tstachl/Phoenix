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
from sqlobject import (SQLObject, StringCol, RelatedJoin, MultipleJoin,
                       ForeignKey, events)

"""----------------------------------------------------------------------------
                                Exception
----------------------------------------------------------------------------"""
class Exception(Exception):
    pass

class RoleException(Exception):
    pass

"""----------------------------------------------------------------------------
                                Class
----------------------------------------------------------------------------"""
class Role(SQLObject):
    name = StringCol(length=255)
    member = ForeignKey("Member")
    members = RelatedJoin("Member")
    privileges = MultipleJoin("Privilege")
    
    @classmethod
    def _beforedestroy(cls, role, *a):
        for member in role.members:
            member.removeRole(role)
        
events.listen(Role._beforedestroy, Role, events.RowDestroySignal)
