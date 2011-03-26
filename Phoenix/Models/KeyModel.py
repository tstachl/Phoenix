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
from sqlobject import SQLObject, ForeignKey, events
from Phoenix.Library import File
from Phoenix.Conf import Config

"""----------------------------------------------------------------------------
                                Exception
----------------------------------------------------------------------------"""
class Exception(Exception):
    pass

class KeyException(Exception):
    pass

"""----------------------------------------------------------------------------
                                Class
----------------------------------------------------------------------------"""
class Key(SQLObject):
    member = ForeignKey("Member")
    initialized = False

    def _init(self, *args, **kw):
        SQLObject._init(self, *args, **kw)
        if hasattr(self, "keystring"):
            Key._writeKey(self.id, self.keystring)
            del self.keystring
        self.initialized = True

    def _set_pubkey(self, value):
        if value and not value.strip():
            raise KeyException("Provided key is not valid.")
        if self.initialized:
            Key._writeKey(self.id, value)
        else:
            self.keystring = value
    
    def _get_pubkey(self):
        return File.extractKey(Config.get("phoenix", "authorized_keys"), self.id)
    
    def getMember(self):
        from Phoenix.Models import Member
        return Member.get(self.member.id)
    
    @classmethod
    def _writeKey(cls, id, key):
        File.replaceLine(Config.get("phoenix", "authorized_keys"),
                         "--key-id %s" % id, cls._prepareKey(id, key))
    
    @classmethod
    def _prepareKey(cls, id, key):
        tmp = """command="phoenix serve --key-id %s",""" % id
        tmp += "no-port-forwarding,no-x11-forwarding,no-agent-forwarding %s" % key
        return tmp

    @classmethod
    def _beforedestroy(cls, key, *a):
        File.replaceLine(Config.get("phoenix", "authorized_keys"), "--key-id %s" % key.id)
        
events.listen(Key._beforedestroy, Key, events.RowDestroySignal)
