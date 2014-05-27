# -*- coding: utf-8 -*-

# Access plug-in locale
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


locales = {
    'ru': {
        'GET_SELF_ACCESS': ['Ваш уровень доступа: {access}'],
        'GET_USER_ACCESS': ['Уровень доступа {fname} {lname}: {access}'],
        'GET_ACCESS_HELP': ['Отображает уровень доступа пользователя. По умолчанию - Ваш уровень доступа\nСинтаксис: доступ [пользователь]'],
        'GIVE_ACCESS_HELP': ['Устанавливает уровень доступа пользователя\nСинтаксис: доступ <пользователь> <доступ>'],
        'GIVE_ACCESS_WRONGACCESS': ['Неправильно указан доступ'],
        'GIVE_ACCESS_ADMIN': ['Невозможно изменить доступ администратора'],
        'GIVE_ACCESS_LARGER': ['Невозможно установить доступ выше вашего'],
        'GIVE_ACCESS_SUCCESS': ['Для {fname} {lname} установлен доступ {access}']
    }
}


__vkbuddylocale__ = True