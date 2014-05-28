# -*- coding: utf-8 -*-

# Config file handling module
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


import yaml


class IncorrectConfig(Exception): pass


class BareConfig:
    def __init__(self):
        self.config = {}
        self.required_list = []

    def add_parameter(self, name, required=False, description='',
                      default=None, typ=str):
        if required:
            self.required_list.append(name)
        self.config[name] = {
            'description': description,
            'default': default,
            'type': typ
        }


class Config:
    def __init__(self, filename, bare):
        cfile = open(filename, 'r')
        self.__config = yaml.load(cfile)
        cfile.close()
        self.bare = bare
        if not self.__config:
            self.__config = {}
        for param in bare.required_list:
            if not param in self.__config:
                raise IncorrectConfig(
                    'Required parameter \'{}\' not found'.format(param)
                )

    def __getitem__(self, item):
        if item in self.__config:
            if item in self.bare.config:
                return self.bare.config[item]['type'](self.__config[item])
            else:
                return self.__config[item]
        elif item in self.bare.config:
            return self.bare.config[item]['default']
        else:
            raise KeyError(item)
