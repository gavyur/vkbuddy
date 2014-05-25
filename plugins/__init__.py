# -*- coding: utf-8 -*-

# Plug-ins initial module
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

import os
import importlib
import localpath


plugins = {}


def __search_modules():
    for filename in os.listdir(localpath.join('plugins')):
        if filename.endswith('.py') and not filename.startswith('__'):
            plugin_name = filename[:-3]
            plugin = importlib.import_module('.' + plugin_name, 'plugins')
            ismodule = getattr(plugin, '__vkbuddymodule__', False)
            if ismodule == True:
                plugins[plugin_name] = plugin


__search_modules()