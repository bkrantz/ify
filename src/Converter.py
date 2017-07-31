import os
import common
import re

class Converter():

    _from = ''
    _to = ''

    def __init__(self, source, target):
        self._from = source
        self._to = target
        shared = self._shared(self._from, self._to)
        if not shared:
            cwd = os.getcwd()
            self._from = self._from if common.regexpos(self._from, cwd) == 0 else "%s/%s" % (cwd, self._from, )
            self._to = self._to if common.regexpos(self._to, cwd) == 0 else "%s/%s" % (cwd, self._to, )
            real = os.path.realpath(self._from)
            self._form = real if real else self._from
            real = os.path.realpath(self._to)
            self._to = real if real else self._to
        self._from = self._dirname(self._from)
        self._to = self._dirname(self._to)
        self._from = self._normalize(self._from)
        self._to = self._normalize(self._to)

    def _normalize(self, path):
        directory_seperator_regex = '[\/\\\\]'
        up_directory_regex = "[^\/]+(?<!\.\.)\/\.\.\/"

        path = re.sub(directory_seperator_regex, "/", path)
        path = common.ltrim(path)
        path = common.rtrim(path)
        path = common.rtrim(path, "\/")
        while re.findall(up_directory_regex, path):
            path = re.sub(up_directory_regex, "", path)

        return path

    def _shared(self, path1, path2):
        path1 = path1.split("/") if path1 else []
        path2 = path2.split("/") if path2 else []
        shared = []

        for pos, chunk in enumerate(path1):
            if common.isset(path2[pos]) and path1[pos] == path2[pos]:
                shared.append(chunk)
            else:
                break

        return "/".join(shared)

    def convert(self, path):
        if self._from == self._to:
            return path
        path = self._normalize(path)

        root_regex = "^(\/)"
        if common.regexpos(path, root_regex) == 0:
            return path

        path = self._normalize("%s/%s" % (self._from, path))
        shared = self._shared(path, self._to)
        path = common.mb_substr(path, len(shared))
        to = common.mb_substr(self._to, len(shared))

        to = "../" * to.count("/")

        return "%s%s" % (to, common.ltrim(path, "\/"))

    def _dirname(self, path):
        if os.path.isfile(path):
            return os.path.dirname(path.rstrip(os.pathsep)) or '.'
        if os.path.isdir(path):
            return common.rtrim(path, "\/")
        if common.mb_substr(path, -1) == "/":
            return common.rtrim(path, "\/")
        regex = ".*\..*$"
        if re.findall(regex, os.path.basename(path)):
            return os.path.dirname(path.rstrip(os.pathsep)) or '.'
        return path