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
from re import match

"""----------------------------------------------------------------------------
                                Class
----------------------------------------------------------------------------"""
class Validate(object):
    @classmethod
    def email(cls, email):
        if len(email) > 7:
            if match("^.+\\@(\\[?)[a-zA-Z0-9\\-\\.]+\\.([a-zA-Z]{2,3}|[0-9]{1,3})(\\]?)$", email):
                return True
        return False
    
    @classmethod
    def username(cls, username):
        if len(username) > 2:
            if match("^[A-Za-z0-9_\\-\\.]*$", username):
                return True
        return False
    
    @classmethod
    def reponame(cls, reponame):
        if len(reponame) > 3:
            if match("^[A-Za-z0-9_\\-]*$", reponame):
                return True
        return False

    @classmethod
    def user(cls, uid):
        from Phoenix.Models import UserMapper
        if UserMapper.findById(uid):
            return True
        return False

    @classmethod
    def repository(cls, rid):
        from Phoenix.Models import RepositoryMapper
        if RepositoryMapper.findById(rid):
            return True
        return False
    
    @classmethod
    def key(cls, kid):
        from Phoenix.Models import KeyMapper
        if KeyMapper.findById(kid):
            return True
        return False
    
    @classmethod
    def hook(cls, hid):
        from Phoenix.Models import HookMapper
        if HookMapper.findById(hid):
            return True
        return False

    @classmethod
    def hookName(cls, name):
        if name in ("applypatch-msg", "commit-msg", "post-commit", "post-receive",
                    "post-update", "pre-applypatch", "pre-commit",
                    "prepare-commit-msg", "pre-rebase", "update"):
            return True
        return False

    @classmethod
    def gitcommand(cls, command):
        if command in ("git-upload-pack", "git-receive-pack"):
            return True
        return False
