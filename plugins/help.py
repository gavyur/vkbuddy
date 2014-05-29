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
    if len(params) >= 1:
        handlers = plugins.commands.get_cmd_handlers(
            vkbuddy, params[0], from_id
        )
        if handlers:
            help = plugins.commands.generate_cmd_help(
                vkbuddy, params[0], from_id
            )
            if help:
                vkbuddy.send_message(from_id, help)
            else:
                params = {'command': params[0]}
                vkbuddy.send_message(
                    from_id,
                    ('Помощь по команде "{command}" не '
                     'найдена'.format(**params))
                )
        else:
            params = {'command': params[0]}
            vkbuddy.send_message(
                from_id, 'Команда "{command}" не найдена'.format(**params)
            )
    else:
        vkbuddy.send_message(
            from_id,
            '''VKBuddy (C) 2014 Yury Gavrilov <yuriy@igavrilov.ru>
Для просмотра списка команд наберите "команды"
Для получения справки по команде наберите "<команда> ?"'''
        )



commands = [
    {'command': 'помощь',
     'access': 0,
     'handler': help_command,
     'help': 'Отображает справочное сообщение',
     'syntax': ''}
]

__vkbuddyplugin__ = True
