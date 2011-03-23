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

"""

    Access Control Test Case
    ===========================================================================
    Purpose:       This test case has to try and gain access to repositories on
                   defined rules.
    Prereq:        Database
    Test Data:     
    Steps:         Steps to carry out the test.
    Notes:         Notes
    Questions:     Questions
    ===========================================================================

"""

"""----------------------------------------------------------------------------
                                Imports
----------------------------------------------------------------------------"""
from Phoenix.Tests import Db
import unittest

"""----------------------------------------------------------------------------
                                TestCase
----------------------------------------------------------------------------"""
class TestOwner(unittest.TestCase):


    def setUp(self):
        self.owner = Db.User("owner", "owner@example.com", "Repository Owner")
        self.owner.save()
        self.owner.createRepository("OwnerRepository", "owner.git")

    def tearDown(self):
        self.owner.delete()


    def testName(self):
        print self.owner.repositories

"""----------------------------------------------------------------------------
                                EntryPoint
----------------------------------------------------------------------------"""
if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
