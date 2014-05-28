# -*- coding: utf-8 -*-

# Help plug-in
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


import plugins.commands


def help_command(vkbuddy, from_id, params, att, subj, ts, msgid):
    if params and params[0] in ['?', 'помощь', 'help']:
        vkbuddy.send_message(from_id, vkbuddy.L('HELP_HELP'))
        return
    if len(params) >= 1:
        handlers = plugins.commands.get_cmd_handlers(
            vkbuddy, params[0], from_id
        )
        if handlers:
            for handler in handlers:
                handler(vkbuddy, from_id, ['?'], att, subj, ts, msgid)
        else:
            vkbuddy.send_message(from_id, vkbuddy.L('HELP_WRONGCOMMAND',
                                                    command=params[0]))
    else:
        vkbuddy.send_message(from_id, vkbuddy.L('HELP'))


commands = [
    ('помощь', 0, help_command)
]

__vkbuddyplugin__ = True