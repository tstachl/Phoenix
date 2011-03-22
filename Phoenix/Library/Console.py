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
from argparse import ArgumentParser
from subprocess import Popen, PIPE
from traceback import format_exc, print_exc

"""----------------------------------------------------------------------------
                                Exception
----------------------------------------------------------------------------"""
class Exception(Exception):
    pass

class ConsoleException(Exception):
    pass

"""----------------------------------------------------------------------------
                                Class
----------------------------------------------------------------------------"""
class Console(object):
    
    args = None
    
    def __init__(self):
        from Phoenix.Conf import Config, logging
        
        parser = ArgumentParser()
        self.defineParser(parser)
        self.args = parser.parse_args()
        
        if self.args.action != "init" and Config.get("phoenix", "initialized", False) != "True":
            print "Please initalize `Phoenix' first."
            print "On Ubuntu simply type: "
            print "    > sudo phoenix-admin init"
            print "To find out about all options type:"
            print "    > sudo phoenix-admin init --help"
            exit()
        
        try:
            p = Popen(["git", "--help"], stdout=PIPE)
            if p.wait() != 0:
                raise ConsoleException("Git not installed.")
        except OSError, ConsoleException:
            print "Please install `git' first."
            print "On Ubuntu simply type:"
            print "    > sudo apt-get install git git-core"
            exit()
        
        try:
            getattr(self, self.args.action)()
        except:
            logging.debug(format_exc())
            print_exc(0)
        exit()
