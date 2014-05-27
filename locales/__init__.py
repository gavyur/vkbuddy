# -*- coding: utf-8 -*-

#Locales initial module
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


locales = {}


def __search_locales():
    for filename in os.listdir(localpath.join('locales')):
        if filename.endswith('.py') and not filename.startswith('__'):
            locale_name = filename[:-3]
            locale = importlib.import_module('.' + locale_name, 'locales')
            islocale = getattr(locale, '__vkbuddylocale__', False)
            if islocale == True:
                llocales = getattr(locale, 'locales', {})
                for llocale in llocales:
                    locales.setdefault(llocale, {})
                    for phrases in llocales[llocale]:
                        locales[llocale].setdefault(phrases, [])
                        locales[llocale][phrases].extend(
                            llocales[llocale][phrases]
                        )


__search_locales()