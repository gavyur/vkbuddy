# -*- coding: utf-8 -*-

# Commands handler plug-in
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


import plugins
import threading


def get_plugins_commands(vkbuddy):
    vkbuddy.commands = {}
    for plug_in in plugins.plugins:
        plugin = plugins.plugins[plug_in]
        for command in getattr(plugin, 'commands', []):
            vkbuddy.commands.setdefault(command[0], {})
            vkbuddy.commands[command[0]].setdefault(command[1], [])
            vkbuddy.commands[command[0]][command[1]].append(command[2])


def handle_message(vkbuddy, code, msgid, flags, from_id, ts, subj, text, att):
    if flags & 2 and flags & 4:
        return
    for command in vkbuddy.commands:
        if text.lower().startswith(command + ' ') or text.lower() == command:
            params = text[len(command) + 1:]
            user_acc = vkbuddy.access.get_access(from_id)
            accesses = list(vkbuddy.commands[command].keys())
            accesses.sort()
            accesses.reverse()
            for access in accesses:
                if user_acc >= access:
                    vkbuddy.api.messages.markAsRead(message_ids=msgid,
                                                    user_id=from_id)
                    for handler in vkbuddy.commands[command][access]:
                        threading.Thread(
                            target=handler,
                            args=(vkbuddy, from_id, params, att,
                                  subj, ts, msgid)
                        ).start()
                    break


before_auth_handlers = [get_plugins_commands]
longpoll_handlers = [(4, handle_message)]

__vkbuddyplugin__ = True