# -*- coding: utf-8 -*-

# VK API Library
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


import urllib.parse
import urllib.request
import urllib.error
import http.cookiejar
import json
import hashlib
import threading

try:
    from bs4 import BeautifulSoup
except ImportError:
    BeautifulSoup = None


API_v = 5.16
USER_AGENT = ('Mozilla/5.0 (Linux; U; Android 2.1; en-us; GT-I9000 '
              'Build/ECLAIR) AppleWebKit/525.10+ (KHTML, like Gecko) '
              'Version/3.0.4 Mobile Safari/523.12.2')


class VKAPIError(Exception):
    def __init__(self, message, code, error={}):
        super(VKAPIError, self).__init__(message)
        self.message = message
        self.code = code
        self.error = error


class VKValidationError(Exception): pass


def direct_auth(client_id, client_secret, username, password, number=None,
                https=False, scope='all'):
    if not https and not scope.count('nohttps'):
        scope += ',nohttps'
    parameters = {
        'grant_type': 'password',
        'client_id': client_id,
        'client_secret': client_secret,
        'username': username,
        'password': password,
        'v': API_v,
        'scope': scope
    }
    parameters = urllib.parse.urlencode(parameters)
    try:
        response = urllib.request.urlopen(
            'https://oauth.vk.com/token?{}'.format(parameters)
        )
    except urllib.error.HTTPError as error:
        response = error.read().decode('utf-8')
    else:
        response = response.read().decode('utf-8')
    result = json.loads(response)
    if 'error' in result:
        if result['error'] == 'need_validation' and number:
            return validate_number(number, result['redirect_uri'])
        raise VKAPIError(result['error'], -1, result)
    return result


def validate_number(number, uri):
    if not BeautifulSoup:
        raise VKValidationError('BeautifulSoup module isn\'t installed')
    if number.startswith('+'):
        number = number[1:]
    cj = http.cookiejar.CookieJar()
    opener = urllib.request.build_opener(
        urllib.request.HTTPCookieProcessor(cj)
    )
    opener.addheaders = [('User-agent', USER_AGENT)]
    op = opener.open(uri)
    page = BeautifulSoup(op.read().decode('utf-8'))
    op.close()
    form = page.find('form', attrs={'method': 'post'})
    number_parts = page.find_all('span', attrs={'class': 'field_prefix'})
    if not (form and number_parts):
        raise VKValidationError('Page didn\'t have form or parts of number')
    nstart = number_parts[0].string.strip()
    if nstart.startswith('+'):
        nstart = nstart[1:]
    nend = number_parts[1].string.strip()
    if not (number.startswith(nstart) and number.endswith(nend)):
        raise VKValidationError(
            'Number must start with {} and end with {}'.format(nstart, nend)
        )
    num_part = number[len(nstart):-len(nend)]
    url = form['action']
    data = urllib.parse.urlencode({'code': num_part}).encode('utf-8')
    op = opener.open('https://m.vk.com{}'.format(url), data)
    url = op.geturl()
    op.close()
    fragment = urllib.parse.urlparse(url).fragment
    reply = urllib.parse.parse_qs(fragment)
    if 'success' in reply:
        result = {}
        if 'access_token' in reply:
            result['access_token'] = reply['access_token'][0]
        if 'secret' in reply:
            result['secret'] = reply['secret'][0]
        if 'expires_in' in reply:
            result['expires_in'] = int(reply['expires_in'][0])
        else:
            result['expires_in'] = 0
        if 'user_id' in reply:
            result['user_id'] = int(reply['user_id'][0])
            return result
    else:
        raise VKValidationError('Validation failed')


class LongPoll:
    def __init__(self, api, handler, wait=25, mode=2):
        self.api = api
        self.handler = handler
        self.wait = wait
        self.mode = mode
        self.alive = False

    def get_server(self):
        return self.api.messages.getLongPollServer()

    def connect(self, server, ts, key):
        parameters = {
            'act': 'a_check',
            'key': key,
            'ts': ts,
            'wait': self.wait,
            'mode': self.mode
        }
        parameters = urllib.parse.urlencode(parameters)
        try:
            response = urllib.request.urlopen(
                'http://{}?{}'.format(server, parameters)
            )
        except urllib.error.HTTPError as error:
            response = error.read().decode('utf-8')
        else:
            response = response.read().decode('utf-8')
        result = json.loads(response)
        return result

    def start(self):
        self.alive = True
        server = self.get_server()
        while self.alive:
            try:
                reply = self.connect(server['server'], server['ts'],
                                     server['key'])
            except:
                continue
            if 'failed' in reply:
                server = self.get_server()
            else:
                server['ts'] = reply['ts']
            if 'updates' in reply:
                for update in reply['updates']:
                    threading.Thread(target=self.handler, 
                                     args=(self.api, update)).start()

    def stop(self):
        self.alive = False


class VKAPIMethod:
    def __init__(self, name, parent):
        self.name = name
        self.parent = parent

    def __getattr__(self, name):
        return VKAPIMethod(name, self)

    def __call__(self, **parameters):
        parent = self.parent
        method = self.name
        while isinstance(parent, VKAPIMethod):
            method = '{}.{}'.format(parent.name, method)
            parent = parent.parent
        return parent.call(method, **parameters)
        

class API:
    def __init__(self, access_token, secret='', number=None, use_https=False):
        if not use_https and not secret:
            raise Exception()
        self.access_token = access_token
        self.use_https = use_https
        self.secret = secret
        self.number = number

    def __getattr__(self, name):
        return VKAPIMethod(name, self)

    def get_sig(self, request):
        raw = (request + self.secret).encode('utf-8')
        return hashlib.md5(raw).hexdigest()

    def call(self, method, **parameters):
        if not 'v' in parameters:
            parameters['v'] = API_v
        parameters['access_token'] = self.access_token
        parameters = urllib.parse.urlencode(parameters)
        request = '/method/%s?%s' % (method, parameters)
        if not self.use_https:
            url = 'http'
        else:
            url = 'https'
        url += '://api.vk.com' + request
        if self.secret:
            sig_param = urllib.parse.urlencode({'sig': self.get_sig(request)})
            url += '&{}'.format(sig_param)
        try:
            response = urllib.request.urlopen(url)
        except urllib.error.HTTPError as error:
            response = error.read().decode('utf-8')
        else:
            response = response.read().decode('utf-8')
        result = json.loads(response)
        if 'response' in result:
            return result['response']
        elif 'error' in result:
            if result['error']['error_code'] == 17:
                if self.number:
                    validate_number(
                        self.number, result['error']['redirect_uri']
                    )
                    return self.call(method, **parameters)
                print(
                    'Redirect URI: {}'.format(result['error']['redirect_uri'])
                )
            raise VKAPIError(
                result['error']['error_msg'], result['error']['error_code'],
                result['error']
            )
        else:
            raise Exception()
