import sublime
import sublime_plugin
import string
import re
import sys
import time
import base64
import htmlentitydefs
from cgi import escape
from hashlib import md5,sha1
from datetime import datetime
from dateutil.parser import parse
from random import sample, choice, randrange

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
    #Convert CamelCase to under_scores and vice versa
    def run(self, edit):
        for region in self.view.sel():
            if not region.empty():
                text = self.view.substr(region)
                text = self.toCamelCase(text) if '_' in text else self.toUnderscores(text)
                self.view.replace(edit, region, text)

    def toUnderscores(self, name):
        s1 = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', name)
        return re.sub('([a-z0-9])([A-Z])', r'\1_\2', s1).lower()

    def toCamelCase(self, name):
        return ''.join(map(lambda x: x.capitalize(), name.split('_')))


class ConvertToUnicodeNotationCommand(sublime_plugin.TextCommand):
    #Convert string to Unicode notation
    def run(self, edit):
        pattern = re.compile(r'\s+')

        for region in self.view.sel():
            if not region.empty():
                text = ''
                for c in self.view.substr(region):
                    if not re.match(pattern, c) and (c < 0x20 or c > 0x7e):
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
                self.view.replace(edit, region, base64.b64encode(text))

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
                try:
                    text = base64.b64decode(self.view.substr(region).encode(self.enc()))
                    self.view.replace(edit, region, text.decode('utf-8'))
                except:
                    sublime.status_message('Convert error.')

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
                self.view.replace(edit, region, text.encode("hex"))

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
                self.view.replace(edit, region, text.decode("hex"))

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
                text = self.view.substr(region).encode(self.enc())
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
            rgb = tuple(str(int(value[i:i+lv/3], 16)) for i in range(0, lv, lv/3))
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
                text = self.view.substr(region).encode(self.enc())
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
                result = self.from_unix(text) if re.match(ur'^([0-9]+)$', text) else self.to_unix(text)

                if result:
                    self.view.replace(edit, region, result)
                else:
                    sublime.status_message('Convert error.')

    def from_unix(self, timestamp):
        sublime.status_message('Convert from epoch to human readable date.')
        return datetime.fromtimestamp(int(timestamp)).strftime("%Y-%m-%d %H:%M")

    def to_unix(self, timestr):
        sublime.status_message('Convert from human readable date to epoch.')
        try:
            return '%d' % (time.mktime(parse(timestr).timetuple()))
        except:
            return False


class InsertTimestampCommand(sublime_plugin.TextCommand):
    #This will allow you to insert timestamp to current position
    def run(self, edit):
        for region in self.view.sel():
            self.view.insert(edit, region.begin(), datetime.now().strftime("%Y-%m-%d %H:%M"))


class PasswordCommand(sublime_plugin.TextCommand):
    chars = "23456789abcdefghijkmnpqrstuvwxyzABCDEFGHKMNPQRSTUVWXYZ"

    def run(self, edit):
        self.view.insert(edit, self.view.sel()[0].begin(), ''.join(sample(self.chars, self.length())))

    def length(self):
        return randrange(6, 31)

class GenerateShortPasswordCommand(PasswordCommand):
    def length(self):
        return randrange(6, 9)

class GenerateMediumPasswordCommand(PasswordCommand):
    def length(self):
        return randrange(9, 14)

class GenerateLongPasswordCommand(PasswordCommand):
    def length(self):
        return randrange(14, 20)

class GenerateSecurePasswordCommand(PasswordCommand):
    chars = string.letters + string.digits
    def length(self):
        return randrange(20, 31)
