# -*- coding: utf-8 -*-

# Keep account online plug-in
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


import random
import logging
import threading


class KeepOnline:
    def __init__(self):
        self.timer = None

    def loop(self, vkbuddy):
        if vkbuddy.cfg['online']:
            vkbuddy.api.account.setOnline()
            sl_time = random.randrange(420, 899)
            self.timer = threading.Timer(sl_time, self.loop, (vkbuddy,))
            self.timer.start()

    def stop_loop(self, vkbuddy):
        if vkbuddy.cfg['online']:
            vkbuddy.api.account.setOffline()
        if self.timer:
            self.timer.cancel()
            self.timer = None


keep_online = KeepOnline()


after_auth_handlers = [keep_online.loop]
exit_handlers = [keep_online.stop_loop]

config_parameters = [
    {'name': 'online',
     'required': False,
     'description': 'Keep account online?',
     'default': True,
     'typ': bool}
]

__vkbuddymodule__ = True