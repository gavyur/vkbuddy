# -*- coding: utf-8 -*-

# Working with local paths module
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

import inspect
import os

cdir = os.path.dirname(
    os.path.realpath(inspect.getfile(inspect.currentframe()))
)

def join(*args):
    if args and os.path.isabs(args[0]):
        return os.path.join(*args)
    return os.path.join(cdir, *args)
