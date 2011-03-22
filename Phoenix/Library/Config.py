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
from ConfigParser import ConfigParser, RawConfigParser, NoOptionError, NoSectionError

"""----------------------------------------------------------------------------
                                Class
----------------------------------------------------------------------------"""
class Config(object):

    SESSION = None
    ENGINE = None
    CP = ConfigParser()
    CR = RawConfigParser()

    @classmethod
    def getSession(cls):
        if not cls.get("SESSION"):
            from sqlalchemy.orm import sessionmaker
            cls.SESSION = sessionmaker(bind=cls.getEngine())
        return (cls.get("SESSION"))()
    
    @classmethod
    def getEngine(cls):
        if not cls.get("ENGINE"):
            from sqlalchemy import create_engine
            echo = True if Config.get("phoenix", "loglevel") == "DEBUG" else False
            cls.ENGINE = create_engine(cls.get("phoenix", "sql_connect"), echo=echo)
        return cls.get("ENGINE")

    @classmethod
    def get(cls, section, option=None, default=""):
        if not option:
            if cls.__dict__.has_key(section): return cls.__dict__[section]
            else:
                msg = 'Configuration item "' + section + '" not found' 
                raise Exception(msg, "Test")
        else:
            cls.get("CP").readfp(open(cls.get("CONF_FILE")))
            try:
                return cls.get("CP").get(section, option)
            except NoOptionError:
                if default != "":
                    cls.set(section, option, default)
                    return str(default)
                return False
            except NoSectionError:
                return False

    @classmethod
    def set(cls, *args):
        cls.get("CR").readfp(open(cls.get("CONF_FILE")))
        try:
            cls.get("CR").set(*args)
        except NoSectionError:
            cls.get("CR").add_section(args[0])
            cls.get("CR").set(*args)
        cls.get("CR").write(open(cls.get("CONF_FILE"), "w"))

"""----------------------------------------------------------------------------
                                Exception
----------------------------------------------------------------------------"""
class Exception(Exception):
    pass
