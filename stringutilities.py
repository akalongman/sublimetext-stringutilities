# @author          Avtandil Kikabidze
# @copyright       Copyright (c) 2008-2016, Avtandil Kikabidze aka LONGMAN (akalongman@gmail.com)
# @link            http://longman.me
# @license         The MIT License (MIT)

import sublime
import sublime_plugin
import string
import re
import sys
import time
import base64
import html.entities as htmlentitydefs
from cgi import escape
from hashlib import md5,sha1
from datetime import datetime
from random import sample, choice, randrange
import os, socket, urllib
import binascii
import json
import pprint

if sys.hexversion >= 0x3000000:
    def unichr(c):
        return chr(c)


class ConvertTabsToSpacesCommand(sublime_plugin.TextCommand):
    #Convert Tabs To Spaces
    def run(self, edit):
        sublime.status_message('Convert tabs to spaces.')
        tab_size = int(self.view.settings().get('tab_size', 4))

        for region in self.view.sel():
            if not region.empty():
                self.view.replace(edit, region, self.view.substr(region).expandtabs(tab_size))
        else:
            self.view.run_command('select_all')
            self.view.replace(edit, self.view.sel()[0], self.view.substr(self.view.sel()[0]).expandtabs(tab_size))
            self.view.sel().clear()


class ConvertSpacesToTabsCommand(sublime_plugin.TextCommand):
    #Convert Spaces To Tabs
    def run(self, edit):
        sublime.status_message('Convert spaces to tabs.')
        tab_size = str(self.view.settings().get('tab_size', 4))

        for region in self.view.sel():
            if not region.empty():
                self.view.replace(edit, region, re.sub(r' {' + tab_size + r'}', r'\t', self.view.substr(region)))
        else:
            self.view.run_command('select_all')
            self.view.replace(edit, self.view.sel()[0], re.sub(r' {' + tab_size + r'}', r'\t', self.view.substr(self.view.sel()[0])))
            self.view.sel().clear()


class ConvertCharsToHtmlCommand(sublime_plugin.TextCommand):
    #Convert Chars into XML/HTML Entities
    def run(self, edit):
        for region in self.view.sel():
            if not region.empty():
                self.view.replace(edit, region, escape(self.view.substr(region), True))


class ConvertHtmlToCharsCommand(sublime_plugin.TextCommand):
    #Convert XML/HTML Entities into Chars
    def run(self, edit):
        for region in self.view.sel():
            if not region.empty():
                text = re.sub('&(%s);' % '|'.join(htmlentitydefs.name2codepoint),
                    lambda m: unichr(htmlentitydefs.name2codepoint[m.group(1)]), self.view.substr(region))
                self.view.replace(edit, region, text)


class ConvertCamelUnderscoresCommand(sublime_plugin.TextCommand):
    #Convert camelCase to under_scores and vice versa
    def run(self, edit):
        for region in self.view.sel():
            if not region.empty():
                text = self.view.substr(region)
                text = self.toCamelCase(text) if '_' in text and text[0].islower() else self.toUnderscores(text)
                self.view.replace(edit, region, text)

    def toUnderscores(self, name):
        s1 = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', name)
        return re.sub('([a-z0-9])([A-Z])', r'\1_\2', s1).lower()

    def toCamelCase(self, name):
        return ''.join(ch.capitalize() if i % 2 else ch for i, ch in enumerate(name.split('_')))


class ConvertPascalUnderscoresCommand(sublime_plugin.TextCommand):
    #Convert PascalCase to under_scores and vice versa
    def run(self, edit):
        for region in self.view.sel():
            if not region.empty():
                text = self.view.substr(region)
                text = self.toPascalCase(text) if '_' in text and text[0].isupper() else self.toUnderscores(text)
                self.view.replace(edit, region, text)

    def toUnderscores(self, name):
        s1 = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', name)
        return re.sub('([a-z0-9])([A-Z])', r'\1_\2', s1).lower()

    def toPascalCase(self, name):
        return ''.join(map(lambda x: x.capitalize(), name.split('_')))


class ConvertToUnicodeNotationCommand(sublime_plugin.TextCommand):
    #Convert string to Unicode notation
    def run(self, edit):
        pattern = re.compile(r'\s+')

        for region in self.view.sel():
            if not region.empty():
                text = ''
                for c in self.view.substr(region):
                    if not re.match(pattern, c) and (ord(c) < 0x20 or ord(c) > 0x7e):
                        text += '\\u{0:04X}'.format(ord(c))
                    else:
                        text += c

                self.view.replace(edit, region, text)


class ConvertFromUnicodeNotationCommand(sublime_plugin.TextCommand):
    #Convert string from Unicode notation
    def run(self, edit):
        pattern = re.compile(r'(\\u)([0-9a-fA-F]{2,4})')

        for region in self.view.sel():
            if not region.empty():
                text = re.sub(pattern, lambda m: unichr(int(m.group(2), 16)), self.view.substr(region))
                self.view.replace(edit, region, text)


class ConvertToBase64Command(sublime_plugin.TextCommand):
    #Encode string with base64
    def run(self, edit):
        for region in self.view.sel():
            if not region.empty():
                text = self.view.substr(region).encode(self.enc())
                t = base64.b64encode(text)
                txt = str(t, self.enc())
                self.view.replace(edit, region, txt)

    def enc(self):
        if self.view.encoding() == 'Undefined':
            return self.view.settings().get('default_encoding', 'UTF-8')
        else:
            return self.view.encoding()


class ConvertFromBase64Command(sublime_plugin.TextCommand):
    #Decode string with base64
    def run(self, edit):
        for region in self.view.sel():
            if not region.empty():
                text = self.view.substr(region).encode(self.enc())
                t = base64.b64decode(text)
                txt = str(t, self.enc())
                self.view.replace(edit, region, txt)

    def enc(self):
        if self.view.encoding() == 'Undefined':
            return self.view.settings().get('default_encoding', 'UTF-8')
        else:
            return self.view.encoding()

class ConvertToHexCommand(sublime_plugin.TextCommand):
    #Convert string to hex
    def run(self, edit):
        for region in self.view.sel():
            if not region.empty():
                text = self.view.substr(region).encode(self.enc())
                t = binascii.hexlify(text)
                txt = str(t,'ascii')
                self.view.replace(edit, region, txt)

    def enc(self):
        if self.view.encoding() == 'Undefined':
            return self.view.settings().get('default_encoding', 'UTF-8')
        else:
            return self.view.encoding()


class ConvertFromHexCommand(sublime_plugin.TextCommand):
    #Convert string from hex
    def run(self, edit):
        for region in self.view.sel():
            if not region.empty():
                text = self.view.substr(region).encode(self.enc())
                t = binascii.unhexlify(text)
                txt = str(t,'ascii')
                self.view.replace(edit, region, txt)

    def enc(self):
        if self.view.encoding() == 'Undefined':
            return self.view.settings().get('default_encoding', 'UTF-8')
        else:
            return self.view.encoding()

class ConvertHexToRgbCommand(sublime_plugin.TextCommand):
    #Convert hex to rgb color
    def run(self, edit):
        for region in self.view.sel():
            if not region.empty():
                text = self.view.substr(region)
                self.view.replace(edit, region, self.hex_to_rgb(text))

    def enc(self):
        if self.view.encoding() == 'Undefined':
            return self.view.settings().get('default_encoding', 'UTF-8')
        else:
            return self.view.encoding()

    def hex_to_rgb(self, value):
        value = value.lstrip('#')
        lv = len(value)
        if lv == 6:
            rgb = tuple(str(int(value[i:i+lv//3], 16)) for i in range(0, lv, lv//3))
        if lv == 3:
            rgb = tuple(str(int(value[i:i+1], 16)*17) for i in range(0, 3))
        if lv == 1:
            v = str(int(value, 16)*17)
            rgb = v, v, v
        return 'rgb(' + ','.join(rgb) + ')'


class ConvertRgbToHexCommand(sublime_plugin.TextCommand):
    #Convert rgb to hex color
    def run(self, edit):
        for region in self.view.sel():
            if not region.empty():
                text = self.view.substr(region)
                str_len = len(text)
                reg_rgb = '^rgb[a]?\((\s*\d+\s*),(\s*\d+\s*),(\s*\d+\s*),?(\s*(0?.?\d)+\s*)?\)$'
                rgb_match = re.match(reg_rgb, text)
                if rgb_match is not None:
                    self.view.replace(edit, region, self.rgb_to_hex(rgb_match))

    def enc(self):
        if self.view.encoding() == 'Undefined':
            return self.view.settings().get('default_encoding', 'UTF-8')
        else:
            return self.view.encoding()

    def rgb_to_hex(self, rgb_match):
        """Converts an rgb(a) value to a hex value.

        Attributes:
            self: The Regionset object.
            rgb_match: The reg exp collection of matches.

        """

        # Convert all values to 10-base integers, strip the leading characters,
        # convert to hex and fill with leading zero's.
        val_1 = hex(int(rgb_match.group(1), 10))[2:].zfill(2)
        val_2 = hex(int(rgb_match.group(2), 10))[2:].zfill(2)
        val_3 = hex(int(rgb_match.group(3), 10))[2:].zfill(2)

        # Return the proformatted string with the new values.
        return '#%s%s%s' % (val_1, val_2, val_3)


class ConvertSingleQuotesToDoubleCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        for region in self.view.sel():
            if not region.empty():
                text = self.view.substr(region)
                text = text.replace("'", "\"")
                self.view.replace(edit, region, text)

class ConvertDoubleQuotesToSingleCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        for region in self.view.sel():
            if not region.empty():
                text = self.view.substr(region)
                text = text.replace("\"", "'")
                self.view.replace(edit, region, text)

class UrlDecodeCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        for region in self.view.sel():
            if not region.empty():
                text = self.view.substr(region)
                text = urllib.parse.unquote(text)
                self.view.replace(edit, region, text)

class UrlEncodeCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        for region in self.view.sel():
            if not region.empty():
                text = self.view.substr(region)
                text = urllib.parse.quote(text)
                self.view.replace(edit, region, text)




class ConvertMd5Command(sublime_plugin.TextCommand):
    #Calculate MD5 hash
    def run(self, edit):
        for region in self.view.sel():
            if not region.empty():
                text = self.view.substr(region).encode(self.enc())
                self.view.replace(edit, region, md5(text).hexdigest())

    def enc(self):
        if self.view.encoding() == 'Undefined':
            return self.view.settings().get('default_encoding', 'UTF-8')
        else:
            return self.view.encoding()

class ConvertSha1Command(sublime_plugin.TextCommand):
    #Calculate SHA1 hash
    def run(self, edit):
        for region in self.view.sel():
            if not region.empty():
                text = self.view.substr(region).encode(self.enc())
                self.view.replace(edit, region, sha1(text).hexdigest())

    def enc(self):
        if self.view.encoding() == 'Undefined':
            return self.view.settings().get('default_encoding', 'UTF-8')
        else:
            return self.view.encoding()


class ConvertTimeFormatCommand(sublime_plugin.TextCommand):
    #This will allow you to convert epoch to human readable date
    def run(self, edit):
        for region in self.view.sel():
            if not region.empty():
                text = self.view.substr(region)

                if re.match('^([0-9]+)$', text):
                    result = self.from_unix(text)
                else:
                    result = self.to_unix(text)

                if result:
                    self.view.replace(edit, region, result)
                else:
                    sublime.status_message('Convert error.')

    def from_unix(self, timestamp):
        sublime.status_message('Convert from epoch to human readable date.')
        timestamp = float(timestamp)
        stamp = datetime.fromtimestamp(timestamp)
        return stamp.strftime("%Y-%m-%d %H:%M")

    def to_unix(self, timestr):
        sublime.status_message('Convert from human readable date to epoch.')
        try:
            datetime_to_convert = datetime.strptime(timestr, "%Y-%m-%d %H:%M")
            return '%d' % (time.mktime(datetime_to_convert.timetuple()))
        except:
            return False


class InsertTimestampCommand(sublime_plugin.TextCommand):
    #This will allow you to insert timestamp to current position
    def run(self, edit):
        for region in self.view.sel():
            self.view.insert(edit, region.begin(), datetime.now().strftime("%Y-%m-%d %H:%M"))


class GeneratePasswordCommand(sublime_plugin.TextCommand):
    chars = "23456789abcdefghijkmnpqrstuvwxyzABCDEFGHKMNPQRSTUVWXYZ"

    def run(self, edit, length=16):
        length = int(length)
        self.view.insert(edit, self.view.sel()[0].begin(), ''.join(sample(self.chars, length)))


class StringUtilitiesExtIpCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        url = "http://api.long.ge/sublimetext/ip.php"
        request = urllib.request.Request(url)
        response = urllib.request.urlopen(request)
        for region in self.view.sel():
            self.view.insert(edit, region.begin(), response.read().decode(self.enc()))

    def enc(self):
        if self.view.encoding() == 'Undefined':
            return self.view.settings().get('default_encoding', 'UTF-8')
        else:
            return self.view.encoding()

class StringUtilitiesIntIpCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(('google.com', 0))
        int_ip = s.getsockname()[0]
        s.close()
        for region in self.view.sel():
                self.view.insert(edit, region.begin(), int_ip)

    def enc(self):
        if self.view.encoding() == 'Undefined':
            return self.view.settings().get('default_encoding', 'UTF-8')
        else:
            return self.view.encoding()


class StringUtilitiesDecodeJsonCommand(sublime_plugin.TextCommand):
    output = ""
    i = 0

    def run(self, edit):
        for region in self.view.sel():
            self.output = ""
            if not region.empty():
                text = self.view.substr(region).encode(self.enc())
                text = str(text, 'utf8')
                data = json.loads(text, encoding='utf8')
                output = json.dumps(data, indent=4, sort_keys=True)

                self.view.replace(edit, region, output)


                #self.recursive_print(data)

                #print(self.output)

                #pp = pprint.PrettyPrinter(indent=4, width=1)
                #data = pp.pformat(data)
                #data = self.output
                #data = data.replace('{   ', '{')
                #data = data.replace('{', '\n   {\n')

                #self.view.replace(edit, region, self.output)

    def enc(self):
        if self.view.encoding() == 'Undefined':
            return self.view.settings().get('default_encoding', 'UTF-8')
        else:
            return self.view.encoding()

    def recursive_print(self, src, dpth = 0, key = ''):
        """ Recursively prints nested elements."""
        tabs = lambda n: '\t' * n * 1 # or 2 or 8 or...
        brace = lambda s, n: '%s%s%s' % ('['*n, s, ']'*n)

        if isinstance(src, dict):
            for key, value in src.items():
                if isinstance(value, dict) or (isinstance(value, list)):
                    self.output += tabs(dpth) + brace(key, dpth) + "\n"
                self.recursive_print(value, dpth + 1, key)
        elif (isinstance(src, list)):
            self.i = 0
            for litem in src:
                self.recursive_print(litem, dpth + 1)
        else:
            if key:
                self.output += tabs(dpth) + '[%s] => %s' % (key, src) + "\n"
            else:
                self.i = self.i + 1
                self.output += tabs(dpth) + str(self.i) + ' => %s' % src + "\n"



class StringUtilitiesTestCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        ext_ip = urllib2.urlopen('http://api.long.ge/sublimetext/ip.php').read()
        for region in self.view.sel():
            self.view.insert(edit, region.begin(), ext_ip.encode(self.enc()))

    def enc(self):
        if self.view.encoding() == 'Undefined':
            return self.view.settings().get('default_encoding', 'UTF-8')
        else:
            return self.view.encoding()
