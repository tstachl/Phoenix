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
from re import search

"""----------------------------------------------------------------------------
                                Class
----------------------------------------------------------------------------"""
class File():
    
    @classmethod
    def touch(cls, filename):
        open(filename, "a").close()
        
    @classmethod
    def appendToFile(cls, filename, text):
        f = open(filename, "a")
        f.write(text + "\n")
        f.close()
        
    @classmethod
    def replaceLine(cls, filename, regex, newline=None):
        lines = []; cls.touch(filename)
        for line in file(filename).readlines():
            if not search(regex, line):
                lines.append(line)
        if newline: lines.append(newline)
        if len(lines) > 0: file(filename, "w").writelines(lines)
        else: open(filename, "w").close()
        
    @classmethod
    def writePermission(cls, filename):
        try:
            open(filename, "a").close()
            return True
        except:
            pass
        return False

    @classmethod
    def extractKey(cls, filename, id):
        key = ""; add = len("no-agent-forwarding") + 1
        for line in file(filename, "r").readlines():
            if search("--key-id %s" % id, line):
                key = line[line.find("no-agent-forwarding") + add:]
        return key
