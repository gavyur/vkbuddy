#!/usr/bin/env python
# -*- coding: utf-8 -*-

# VKBuddy core
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
import sys
import time
import codecs
import random
import sqlite3
import logging
import threading
import traceback
import urllib.parse
import vk
import config
import plugins
import localpath


bare = config.BareConfig()
bare.add_parameter(
    'access_token', False, 'Access token', ''
)
bare.add_parameter(
    'secret', False, 'Secret (from nohttps auth)', ''
)
bare.add_parameter(
    'number', False, 'Phone number', ''
)
bare.add_parameter(
    'login', False, 'VK login', ''
)
bare.add_parameter(
    'password', False, 'VK password', ''
)
bare.add_parameter(
    'client_id', False, 'Your VK App ID', 0x386bcf, int
)
bare.add_parameter(
    'client_secret', False, 'Your VK App secret', 
    codecs.decode('NyIKMSZHdleaNOc8aphH', 'rot_13')
)
bare.add_parameter(
    'https', False, 'Use HTTPS?', True, bool
)
bare.add_parameter(
    'logfile', False, 'Log file path', 'vkbuddy.log'
)
bare.add_parameter(
    'dbfile', False, 'SQLite database file path', 'vkbuddy.db'
)
bare.add_parameter(
    'debug', False, 'DEBUG mode', False, bool
)


class ConfigFileNotFound(Exception): pass
class VKBuddyNotAuthorised(Exception): pass


class VKBuddy:
    def __init__(self, cfgfile):
        self.import_plugins()
        cfgfile = localpath.join(cfgfile)
        if not os.path.isfile(cfgfile):
            raise ConfigFileNotFound(
                'Couldn\'t find config file: "{}"'.format(cfgfile)
            )
        self.cfg = config.Config(cfgfile, bare)
        self.install_logger()
        logger = logging.getLogger('main')
        logger.info('Starting VKBuddy...')
        if plugins.plugins:
            logger.info(
                'Imported {} plugins: {}'.format(len(plugins.plugins),
                                                 ', '.join(plugins.plugins))
            )
        else:
            logger.info('No plugins imported')
        self.db_init()
        for obj in self.shared_classes:
            setattr(self, obj[0], obj[1](self))
        for handler in self.before_auth_handlers:
            threading.Thread(target=handler, args=(self,)).start()
        self.api = None
        self.myid = 0
        self.longpoll = None

    def db_init(self):
        types = {
            None: 'NULL',
            int: 'INTEGER',
            float: 'REAL',
            str: 'TEXT',
            bytes: 'BLOB'
        }
        self.db = DataBase(localpath.join(self.cfg['dbfile']))
        for table in self.sql_tables:
            columns = []
            for column in table['structure']:
                columns.append('{} {}'.format(column[0], types[column[1]]))
            self.db.execute(
                'CREATE TABLE IF NOT EXISTS {} ({})'.format(
                    table['name'], ', '.join(columns)
                ), 'commit'
            )

    def send_message(self, user_id, text, attachments=[], delay=True):
        self.api.messages.setActivity(user_id=user_id, type='typing')
        if delay:
            time.sleep(random.randrange(5, 10))
        self.api.messages.send(user_id=user_id, message=text)

    def auth(self):
        logger = logging.getLogger('main')
        if self.cfg['access_token']:
            logger.info('Authenticating using given access token')
            self.api = vk.API(
                self.cfg['access_token'], self.cfg['secret'],
                self.cfg['number'], self.cfg['https']
            )
        elif self.cfg['login'] and self.cfg['password']:
            logger.info('Authenticating using login and password')
            auth = vk.direct_auth(
                self.cfg['client_id'], self.cfg['client_secret'],
                self.cfg['login'], self.cfg['password'], self.cfg['number'],
                self.cfg['https']
            )
            secret = auth.get('secret', '')
            if secret:
                logger.info('Got access token: "{}" and secret: "{}". Now you'
                            ' can change login and password by access token '
                            'and secret'.format(auth['access_token'], secret))
            else:
                logger.info('Got access token: "{}". Now you can change login'
                            ' and password by access '
                            'token'.format(auth['access_token'], secret))
            self.api = vk.API(
                auth['access_token'], secret, self.cfg['number'],
                self.cfg['https']
            )
        else:
            raise config.IncorrectConfig(
                'There is no login and password or access token in config'
            )
        self.myid = self.api.users.get(fields='')[0]['id']
        logger.info('Authentication success')
        logger.info('User ID: {}'.format(self.myid))
        for handler in self.after_auth_handlers:
            threading.Thread(target=handler, args=(self,)).start()

    def get_user_info(self, user, fields=[], ncase='nom'):
        parsed_url = urllib.parse.urlparse(user)
        if ((parsed_url.scheme in ('http', 'https')) and
            (parsed_url.netloc == 'vk.com')):
            user = parsed_url.path[1:]
        try:
            guser = self.api.users.get(user_ids=user, fields=','.join(fields),
                                       name_case=ncase)
        except vk.VKAPIError:
            return
        else:
            if guser:
                return guser[0]

    def import_plugins(self):
        self.sql_tables = []
        self.shared_classes = []
        self.before_auth_handlers = []
        self.after_auth_handlers = []
        self.exit_handlers = []
        self.longpoll_handlers = {None: []}
        for plug_in in plugins.plugins:
            plugin = plugins.plugins[plug_in]
            for table in getattr(plugin, 'sql_tables', []):
                self.sql_tables.append(table)
            for obj in getattr(plugin, 'shared_classes', []):
                self.shared_classes.append(obj)
            for config_param in getattr(plugin, 'config_parameters', []):
                bare.add_parameter(**config_param)
            for handler in getattr(plugin, 'before_auth_handlers', []):
                self.before_auth_handlers.append(handler)
            for handler in getattr(plugin, 'after_auth_handlers', []):
                self.after_auth_handlers.append(handler)
            for handler in getattr(plugin, 'exit_handlers', []):
                self.exit_handlers.append(handler)
            for handler in getattr(plugin, 'longpoll_handlers', []):
                if isinstance(handler[0], int) or handler[0] == None:
                    codes = (handler[0],)
                else:
                    codes = handler[0]
                for code in codes:
                    self.longpoll_handlers.setdefault(code, [])
                    self.longpoll_handlers[code].append(handler[1])


    def install_logger(self):
        logger = logging.getLogger('main')
        if self.cfg['debug']:
            logger.setLevel(logging.DEBUG)
        else:
            logger.setLevel(logging.INFO)
        formatter = logging.Formatter(
            '{asctime} [{levelname}]: {message}', '%d.%m.%Y %H:%M:%S', '{'
        )
        fhnd = logging.FileHandler(
            localpath.join(self.cfg['logfile']), encoding='utf-8'
        )
        fhnd.setFormatter(formatter)
        logger.addHandler(fhnd)
        install_exceptions_logging('main')

    def longpoll_handler(self, api, update):
        for handler in self.longpoll_handlers[None]:
            threading.Thread(target=handler,
                             args=[self] + update).start()
        if update[0] in self.longpoll_handlers:
            for handler in self.longpoll_handlers[update[0]]:
                threading.Thread(target=handler,
                                 args=[self] + update).start()

    def start_longpoll(self, block=True):
        if not self.api:
            raise VKBuddyNotAuthorised('VKBuddy isn\'t authorised')
        self.longpoll = vk.LongPoll(self.api, self.longpoll_handler, 25, 74)
        lpthread = threading.Thread(target=self.longpoll.start)
        lpthread.daemon = True
        lpthread.start()
        self.alive = True
        if block:
            while self.alive:
                time.sleep(100)

    def stop(self):
        for handler in self.exit_handlers:
            threading.Thread(target=handler, args=(self,)).start()
        self.alive = False
        if self.longpoll:
            self.longpoll.stop()


class DataBase:
    def __init__(self, filename):
        self.filename = filename

    def execute(self, sql, action, *args, **kwargs):
        connection = sqlite3.connect(self.filename)
        cursor = connection.cursor()
        cursor.execute(sql, *args, **kwargs)
        result = None
        if action == 'commit':
            connection.commit()
        elif action == 'fetchone':
            result = cursor.fetchone()
        elif action == 'fetchall':
            result = cursor.fetchall()
        cursor.close()
        connection.close()
        return result


def install_exceptions_logging(logger_name):
    def excepthook(etype, value, etraceback):
        exception = ''.join(traceback.format_exception(etype, value, etraceback)).strip()
        logging.getLogger(logger_name).error(exception)
        sys.__excepthook__(etype, value, etraceback)
    sys.excepthook = excepthook
    threading_excepthook()


def threading_excepthook():
    run_old = threading.Thread.run
    def run(*args, **kwargs):
        try:
            run_old(*args, **kwargs)
        except (KeyboardInterrupt, SystemExit):
            raise
        except:
            sys.excepthook(*sys.exc_info())
    threading.Thread.run = run


def main(argv):
    if argv:
        cfgfile = argv[0]
    else:
        cfgfile = 'config.yaml'
    vkbuddy = VKBuddy(cfgfile)
    vkbuddy.auth()
    try:
        vkbuddy.start_longpoll()
    except KeyboardInterrupt:
        print('Interrupted...')
        vkbuddy.stop()

if __name__ == '__main__':
    main(sys.argv[1:])
