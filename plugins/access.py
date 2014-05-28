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
    default_access = 0
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


def access_command_admin(vkbuddy, from_id, params, att, subj, ts, msgid):
    if params and params[0] in ['?', 'помощь', 'help']:
        message = '1) {}\n2) {}'.format(vkbuddy.L('GET_ACCESS_HELP'),
                                        vkbuddy.L('GIVE_ACCESS_HELP'))
        vkbuddy.send_message(from_id, message)
        return
    if len(params) <= 1:
        access_command(vkbuddy, from_id, params, att, subj, ts, msgid)
    else:
        user = params[0]
        access = params[1]
        found_user = vkbuddy.get_user_info(user, ncase='gen')
        if found_user:
            try:
                access = int(access)
            except ValueError:
                vkbuddy.send_message(from_id,
                                     vkbuddy.L('GIVE_ACCESS_WRONGACCESS'))
            else:
                if found_user['id'] in vkbuddy.cfg['admins']:
                    vkbuddy.send_message(from_id, vkbuddy.L('GIVE_ACCESS_ADMIN'))
                elif vkbuddy.access.get_access(from_id) < access:
                    vkbuddy.send_message(from_id, vkbuddy.L('GIVE_ACCESS_LARGER'))
                else:
                    vkbuddy.access.set_access(found_user['id'], access)
                    vkbuddy.send_message(
                        from_id,
                        vkbuddy.L('GIVE_ACCESS_SUCCESS',
                                  uid=found_user['id'],
                                  fname=found_user['first_name'],
                                  lname=found_user['last_name'],
                                  access=access)
                    )
        else:
            vkbuddy.send_message(from_id, vkbuddy.L('WRONG_USER', uid=user))



def access_command(vkbuddy, from_id, params, att, subj, ts, msgid):
    if params and params[0] in ['?', 'помощь', 'help']:
        vkbuddy.send_message(from_id, vkbuddy.L('GET_ACCESS_HELP'))
        return
    if not params:
        params = [str(from_id)]
    user = params[0]
    found_user = vkbuddy.get_user_info(user, ncase='gen')
    if found_user:
        access = vkbuddy.access.get_access(found_user['id'])
        if found_user['id'] == from_id:
            vkbuddy.send_message(
                from_id, vkbuddy.L('GET_SELF_ACCESS', access=access)
            )
        else:
            vkbuddy.send_message(
                from_id, vkbuddy.L('GET_USER_ACCESS', access=access,
                                   uid=found_user['id'],
                                   fname=found_user['first_name'],
                                   lname=found_user['last_name'])
            )
    else:
        vkbuddy.send_message(from_id, vkbuddy.L('WRONG_USER', uid=user))

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

commands = [
    ('доступ', 20, access_command_admin),
    ('доступ', 0, access_command)
]

__vkbuddyplugin__ = True
