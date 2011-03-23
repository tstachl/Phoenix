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
    @since:        Mar 22, 2011

"""

"""----------------------------------------------------------------------------
                                Imports
----------------------------------------------------------------------------"""
from sqlalchemy import MetaData, Table, Column, Integer, String, ForeignKey
from sqlalchemy import Boolean
from Phoenix.Conf import Config

engine = Config.getEngine(True)

metadata = MetaData()
user = Table("user", metadata,
    Column("id", Integer, primary_key=True),
    Column("email", String, nullable=False),
    Column("username", String, nullable=False),
    Column("name", String, nullable=False),
)

group = Table("group", metadata,
    Column("id", Integer, primary_key=True),
    Column("name", String, nullable=False),
)

user_group = Table("user_group", metadata,
    Column("uid", Integer, ForeignKey("user.id")),
    Column("gid", Integer, ForeignKey("group.id")),
)

repository = Table("repository", metadata,
    Column("id", Integer, primary_key=True),
    Column("uid", Integer, ForeignKey("user.id"), nullable=False),
    Column("name", String, nullable=False),
    Column("path", String, nullable=False),
    Column("hash", String, nullable=False),
)

rule = Table("rule", metadata,
    Column("id", Integer, primary_key=True),
    Column("rid", Integer, ForeignKey("repository.id"), nullable=False),
    Column("tag", String, nullable=False),
    Column("branch", String, nullable=False),
    Column("crud", String, nullable=False),
    Column("uid", Integer, ForeignKey("user.id")),
    Column("gid", Integer, ForeignKey("group.id")),
    Column("pub", Boolean),
)

key = Table("key", metadata,
    Column("id", Integer, primary_key=True),
    Column("uid", Integer, ForeignKey("user.id"), nullable=False),
    Column("rid", Integer, ForeignKey("repository.id")),
)

hook = Table("hook", metadata,
    Column("id", Integer, primary_key=True),
    Column("rid", Integer, ForeignKey("repository.id"), nullable=False),
    Column("hook", String, nullable=False),
    Column("command", String, nullable=False),
)
metadata.create_all(engine)

from Phoenix.Models import User, UserMapper
from Phoenix.Models import Group, GroupMapper
from Phoenix.Models import Repository, RepositoryMapper
from Phoenix.Models import Rule, RuleMapper
from Phoenix.Models import Key, KeyMapper
from Phoenix.Models import Hook, HookMapper
