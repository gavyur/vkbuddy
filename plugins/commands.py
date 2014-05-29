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
import shlex


def get_plugins_commands(vkbuddy):
    vkbuddy.commands = {}
    for plug_in in plugins.plugins:
        plugin = plugins.plugins[plug_in]
        for cmd in getattr(plugin, 'commands', []):
            vkbuddy.commands.setdefault(cmd['command'], {})
            vkbuddy.commands[cmd['command']].setdefault(cmd['access'], {})
            vkbuddy.commands[cmd['command']][cmd['access']].setdefault(
                'handlers', []
            )
            (vkbuddy.commands[cmd['command']][cmd['access']]['handlers']
                .append(cmd['handler']))
            ch = vkbuddy.commands[cmd['command']][cmd['access']].setdefault(
                'help', ''
            )
            if not ch:
                vkbuddy.commands[cmd['command']][cmd['access']]['help'] = (
                    cmd.get('help', '')
                )
            cs = vkbuddy.commands[cmd['command']][cmd['access']].setdefault(
                'syntax', None
            )
            if cs == None:
                vkbuddy.commands[cmd['command']][cmd['access']]['syntax'] = (
                    cmd.get('syntax', None)
                )
            ex = vkbuddy.commands[cmd['command']][cmd['access']].setdefault(
                'examples', []
            )
            for example in cmd.get('examples', []):
                if example in ex:
                    continue
                (vkbuddy.commands[cmd['command']][cmd['access']]['examples']
                    .append(example))


def get_cmd(vkbuddy, command, from_id):
    command = command.lower()
    if command in vkbuddy.commands:
        user_acc = vkbuddy.access.get_access(from_id)
        accesses = list(vkbuddy.commands[command].keys())
        accesses.sort()
        accesses.reverse()
        for access in accesses:
            if user_acc >= access:
                return vkbuddy.commands[command][access]
    return {}


def get_cmd_handlers(vkbuddy, command, from_id):
    cmd = get_cmd(vkbuddy, command, from_id)
    if cmd:
        return cmd['handlers']
    else:
        return []


def generate_cmd_help(vkbuddy, command, from_id):
    cmd = get_cmd(vkbuddy, command, from_id)
    if cmd:
        result = cmd['help']
        if result:
            result += '\n'
        syntax = cmd['syntax']
        if syntax != None:
            result += 'Синтаксис: {} {}\n'.format(command, syntax)
        examples = cmd['examples']
        if len(examples) == 1:
            example = examples[0]
            result += 'Пример: "{}'.format(command)
            if example[0]:
                result += ' {}"'.format(example[0])
            else:
                result += '"'
            if example[1]:
                result += ' - {}\n'.format(example[1])
            else:
                result += '\n'
        elif len(examples) > 1:
            result += 'Примеры: \n'
            for num, example in enumerate(examples):
                result += '{}) "{}'.format(num + 1, command)
                if example[0]:
                    result += ' {}"'.format(example[0])
                else:
                    result += '"'
                if example[1]:
                    result += ' - {}\n'.format(example[1])
                else:
                    result += '\n'
        return result.strip()
    else:
        return ''


def has_command(vkbuddy, text, from_id):
    try:
        splitted = shlex.split(text)
    except ValueError:
        return False
    else:
        if get_cmd_handlers(vkbuddy, splitted[0], from_id):
            return True
        return False


def send_cmd_help(vkbuddy, user_id, command):
    help = generate_cmd_help(vkbuddy, command, user_id)
    if help:
        vkbuddy.send_message(user_id, help)
    else:
        vkbuddy.send_message(
            user_id,
            ('Помощь по команде "{command}" не '
             'найдена'.format(command=command))
        )


def handle_message(vkbuddy, code, msgid, flags, from_id, ts, subj, text, att):
    if flags & 2:
        return
    try:
        splitted = shlex.split(text)
    except ValueError:
        pass
    else:
        handlers = get_cmd_handlers(vkbuddy, splitted[0], from_id)
        if handlers:
            vkbuddy.api.messages.markAsRead(
                message_ids=msgid, user_id=from_id
            )
            params = splitted[1:]
            if params and params[0] in ['?', 'помощь', 'хелп', 'help']:
                send_cmd_help(vkbuddy, from_id, splitted[0])
                return
            for handler in handlers:
                threading.Thread(
                    target=handler,
                    args=(vkbuddy, from_id, params, att, subj, ts, msgid)
                ).start()


def commands_command(vkbuddy, from_id, params, att, subj, ts, msgid):
    av_commands = []
    for command in vkbuddy.commands:
        if get_cmd_handlers(vkbuddy, command, from_id):
            av_commands.append(command)
    av_commands.sort()
    if av_commands:
        params = {'commands': ', '.join(av_commands)}
        vkbuddy.send_message(
            from_id, 'Список доступных команд: {commands}'.format(**params)
        )
    else:
        vkbuddy.send_message(from_id, 'Нет доступных команд')


before_auth_handlers = [get_plugins_commands]
longpoll_handlers = [(4, handle_message)]


commands = [
    {'command': 'команды',
     'access': 0,
     'handler': commands_command,
     'help': 'Отображает список всех доступных команд',
     'syntax': ''}
]


__vkbuddyplugin__ = True
