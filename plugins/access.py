# -*- coding: utf-8 -*-

# Access plug-in
# Copyright (C) 2014 Yury Gavrilov <yuriy@igavrilov.ru>

# This file is part of VKBuddy.

# VKBuddy is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# VKBuddy is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with VKBuddy.  If not, see <http://www.gnu.org/licenses/>.


class Access:
    default_access = 10
    admin_access = 20

    def __init__(self, vkbuddy):
        self.vkbuddy = vkbuddy

    def __get_db_access(self, uid):
        result = self.vkbuddy.db.execute(
            'SELECT access FROM access_main WHERE id=?', 'fetchone', (uid,)
        )
        if result:
            return result[0]
        return result

    def __set_db_access(self, uid, access):
        self.vkbuddy.db.execute(
            'INSERT INTO access_main VALUES (?, ?)', 'commit', (uid, access)
        )

    def __remove_db_access(self, uid):
        self.vkbuddy.db.execute(
            'DELETE FROM access_main WHERE id=?', 'commit', (uid,)
        )

    def set_access(self, uid, access):
        if uid not in self.vkbuddy.cfg['admins']:
            if access == self.default_access:
                self.__remove_db_access(uid)
            else:
                self.__set_db_access(uid, access)

    def get_access(self, uid):
        if uid in self.vkbuddy.cfg['admins']:
            return self.admin_access
        else:
            dbacc = self.__get_db_access(uid)
            if dbacc == None:
                return self.default_access
            else:
                return dbacc

sql_tables = [
    {'name': 'access_main',
     'structure':(
        ('id', int),
        ('access', int)
     )}
]

shared_classes = [('access', Access)]

config_parameters = [
    {'name': 'admins',
     'required': False,
     'description': 'VKBuddy administrators\' IDs',
     'default': [],
     'typ': list}
]

__vkbuddyplugin__ = True