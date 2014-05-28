# -*- coding: utf-8 -*-

# Typical programmer community counter plug-in
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


import threading
import random


class TProgerCounter:
    def __init__(self):
        self.vkbuddy = None
        self.timer = None

    def parse_digit(self, text):
        digit = text.split()[0]
        ruseng = {
            'А': 'A',
            'В': 'B',
            'С': 'C',
            'Е': 'E',
            'а': 'a',
            'с': 'c',
            'е': 'e',
            'х': 'x',
        }
        for rus in ruseng:
            digit = digit.replace(rus, ruseng[rus])
        digit = int(digit, 16)
        return digit

    def get_last_digit(self):
        if not self.vkbuddy:
            return
        last_message = self.vkbuddy.api.board.getComments(
            group_id=self.vkbuddy.cfg['tproger_id'],
            topic_id=self.vkbuddy.cfg['tproger_boardid'],
            count=1,
            sort='desc'
        )
        cnt = last_message['count']
        from_id = last_message['items'][0]['from_id']
        lastmsg = last_message['items'][0]['text']
        try:
            digit = self.parse_digit(lastmsg)
        except:
            return
        else:
            if ((digit == (cnt - 1)) and
                (from_id != self.vkbuddy.myid) and
                (digit < 0x100000)):
                return digit
            else:
                return

    def post_digit(self, digit):
        texts = ['0x{:06x}', '0x{:06X}', '0x{:x}', '0x{:X}']
        text = random.choice(texts).format(digit)
        self.vkbuddy.api.board.addComment(
            group_id=self.vkbuddy.cfg['tproger_id'],
            topic_id=self.vkbuddy.cfg['tproger_boardid'],
            text=text
        )

    def after_posting_check(self):
        last_messages = self.vkbuddy.api.board.getComments(
            group_id=self.vkbuddy.cfg['tproger_id'],
            topic_id=self.vkbuddy.cfg['tproger_boardid'],
            count=4,
            sort='desc'
        )
        counts = {}
        for message in last_messages['items']:
            try:
                digit = self.parse_digit(message['text'])
            except:
                continue
            else:
                counts.setdefault(digit, [])
                counts[digit].append(message)
        for messages in counts:
            if len(counts[messages]) > 1:
                for message in counts[messages]:
                    if message['from_id'] == self.vkbuddy.myid:
                        self.vkbuddy.api.board.deleteComment(
                            group_id=self.vkbuddy.cfg['tproger_id'],
                            topic_id=self.vkbuddy.cfg['tproger_boardid'],
                            comment_id=message['id']
                        )

    def loop(self):
        last_digit = self.get_last_digit()
        if last_digit:
            self.post_digit(last_digit + 1)
            try:
                self.after_posting_check()
            except:
                pass
        self.timer = threading.Timer(random.randrange(60, 300), self.loop)
        self.timer.start()

    def start_loop(self, vkbuddy):
        if not vkbuddy.cfg['tproger_counter']:
            return
        self.vkbuddy = vkbuddy
        self.loop()

    def is_running(self):
        if not self.timer:
            return False
        return self.timer.is_alive()

    def stop_loop(self, vkbuddy):
        if self.timer:
            self.timer.cancel()
            self.timer = None


def toggle_counter(vkbuddy, from_id, params, att, subj, ts, msgid):
    if params and params[0] in ['?', 'помощь', 'help']:
        vkbuddy.send_message(from_id, vkbuddy.L('TPCNT_TOGGLE_HELP'))
        return
    if params:
        if params[0] in ['старт', 'включить', '+', 'вкл', 'start']:
            if counter.is_running():
                vkbuddy.send_message(from_id,
                                     vkbuddy.L('TPCNT_ALREADY_RUNNING'))
            else:
                counter.start_loop(vkbuddy)
                vkbuddy.send_message(from_id, vkbuddy.L('TPCNT_TOGGLED_RUN'))
        elif params[0] in ['стоп', 'выключить', '-', 'выкл', 'stop']:
            if counter.is_running():
                counter.stop_loop(vkbuddy)
                vkbuddy.send_message(from_id,
                                     vkbuddy.L('TPCNT_TOGGLED_NOTRUN'))
            else:
                vkbuddy.send_message(from_id,
                                     vkbuddy.L('TPCNT_ALREADY_NOTRUNNING'))
        else:
            vkbuddy.send_message(
                from_id, vkbuddy.L('WRONG_PARAMETERS', command='тпсчетчик')
            )
    else:
        if counter.is_running():
            vkbuddy.send_message(from_id, vkbuddy.L('TPCNT_RUNNING'))
        else:
            vkbuddy.send_message(from_id, vkbuddy.L('TPCNT_NOTRUNNING'))


counter = TProgerCounter()
after_auth_handlers = [counter.start_loop]
exit_handlers = [counter.stop_loop]

config_parameters = [
    {'name': 'tproger_counter',
     'required': False,
     'description': 'Count numbers in TProger community?',
     'default': False,
     'typ': bool},
    {'name': 'tproger_id',
     'required': False,
     'description': 'TProger community ID',
     'default': 30666517,
     'typ': int},
    {'name': 'tproger_boardid',
     'required': False,
     'description': 'TProger board when count numbers ID',
     'default': 25736069,
     'typ': int}
]

commands = [
    ('тпсчетчик', 20, toggle_counter)
]

__vkbuddyplugin__ = True
