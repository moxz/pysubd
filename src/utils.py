#!/usr/bin/python
# -*- coding: utf-8 -*-

import os
import logging
import logging.handlers
import re
import struct
import requests
from PyQt4.QtCore import QObject, pyqtSignal
from operator import itemgetter
import socket
from requests import exceptions


class NoInternetConnectionFound(Exception):
    pass


class IncorrectResponseRecieved(Exception):
    pass


class DailyDownloadLimitExceeded(Exception):
    pass


class Communicator(QObject):

    all_download_complete = pyqtSignal(object)  # to pysubd from SubD
    found_video_file = pyqtSignal(object)  # to pysubd from SubD
    downloaded_sub = pyqtSignal()  # to pysubd from others
    updategui = pyqtSignal(object, object)  # to pysubd from SubD addic and opensubs
    no_sub_found = pyqtSignal(object)  # to SUbD from others
    reprocess = pyqtSignal(object) #from opensubs to SubtitleDownload


communicator = Communicator()

request_headers = {
    'Host': 'www.addic7ed.com',
    'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux i686; rv:14.0) Gecko/20100101 Firefox/14.0.1',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    'Accept-Language': 'en-us,en;q=0.5',
    'Accept-Encoding': 'gzip, deflate',
    'Connection': 'keep-alive',
    }

tv_show_regex = \
    re.compile(r"(?:[^\\]\\)*(?P<SeriesName>.*) S?(?P<SeasonNumber>[0-9]+)(?:[ .XE]+(?P<EpisodeNumber>[0-9]+))(?P<Teams>.*)"
               , re.IGNORECASE)
movie_regex = \
    re.compile('(?P<movie>.*)[\.|\[|\(| ]{1}(?P<year>(?:(?:19|20)[0-9]{2}))(?P<teams>.*)'
               , re.IGNORECASE)


def get_logger():
    ''' Returns a valid logger object'''

    LOG_FILENAME = 'PySubD.log'
    logger = logging.getLogger('PySubDLogger')
    logging.basicConfig(level=logging.DEBUG,
                        format='%(asctime)s %(funcName)s %(levelname)-8s %(message)s',
                        filename=LOG_FILENAME, filemode='a')
    handler = logging.handlers.RotatingFileHandler(LOG_FILENAME,
            maxBytes=50000)
    logger.addHandler(handler)
    return logger


def check_tvshow(filename):
    ''' Checks if the given file name is a valid tv show episode or not.'''

    fname = unicode(filename.lower())
    guessed_file_data = guess_file_data(fname)
    return guessed_file_data['type'] == 'tvshow'


def is_video_file(filename):
    ''' Checks if the given file name is a valid video file or not, based on its extension.'''

    video_extns = [
        '.avi',
        '.divx',
        '.mkv',
        '.mp4',
        '.ogg',
        '.rm',
        '.rmvb',
        '.vob',
        '.x264',
        '.xvid',
        '.wmv',
        '.mov',
        '.mpeg',
        ]
    if os.path.splitext(filename)[1].lower() in video_extns:
        return True


def clean_name(name):
    ''' Cleans the file name of non alpha numeric characters and extra spaces.'''

    # pattern = re.compile('[\W_]+')
    name = re.sub('[\W_]+', ' ', unicode(name.lower()))
    name = re.sub(r"\s+", ' ', name)
    return name


def guess_file_data(filename):
    filename = clean_name(filename)
    matches_tvshow = tv_show_regex.match(filename)
    matches_movie = movie_regex.match(filename)

    if matches_tvshow and not matches_movie :
        (tvshow, season, episode, teams) = matches_tvshow.groups()
        teams = teams.split()
        data = {
                'type': 'tvshow',
                'name': tvshow.strip(),
                'season': int(season),
                'episode': int(episode),
                'teams': teams,
                }
    elif matches_movie:
        (movie, year, teams) = matches_movie.groups()
        teams = teams.split()
        part = None
        if 'cd1' in teams:
            teams.remove('cd1')
            part = 1
        if 'cd2' in teams:
            teams.remove('cd2')
            part = 2
        data = {
            'type': 'movie',
            'name': movie.strip(),
            'year': year,
            'teams': teams,
            'part': part,
            }
    else:
            data = {'type': 'unknown', 'name': filename, 'teams': []}
    logger.debug('Guessed data %s'%data)
    return data


def calc_file_hash(filepath):
    ''' Calculates the hash value of a movie.
        Edited from from OpenSubtitles's own examples:
        http://trac.opensubtitles.org/projects/opensubtitles/wiki/HashSourceCodes
        '''

    try:
        longlongformat = 'q'  # long long
        bytesize = struct.calcsize(longlongformat)

        f = open(filepath, 'rb')

        filesize = os.path.getsize(filepath)
        filehash = filesize

        if filesize < 65536 * 2:
            raise Exception('SizeError: Minimum file size must be 120Kb'
                            )

        for x in range(65536 // bytesize):
            buffer = f.read(bytesize)
            (l_value, ) = struct.unpack(longlongformat, buffer)
            filehash += l_value
            filehash = filehash & 0xFFFFFFFFFFFFFFFF  # to remain as 64bit number

        f.seek(max(0, filesize - 65536), 0)
        for x in range(65536 // bytesize):
            buffer = f.read(bytesize)
            (l_value, ) = struct.unpack(longlongformat, buffer)
            filehash += l_value
            filehash = filehash & 0xFFFFFFFFFFFFFFFF

        f.close()
        filehash = '%016x' % filehash
        return filehash
    except IOError:
        raise

def download_url_content(url, referer=None, timeout=10):
    ''' Downloads and returns the contents of the given url.'''

    logger.debug('Downloading contents of %s' % url)
    if referer:
        request_headers['Referer'] = referer
    else:
        request_headers['Referer'] = url

    try:
        x = requests.get(url, headers=request_headers, timeout=timeout)
    except (requests.exceptions.Timeout, exceptions.ConnectionError, socket.timeout):
        raise NoInternetConnectionFound

    if x.status_code != 200:
        raise IncorrectResponseRecieved

    if x.content.find('Daily Download count exceeded') != -1:
        raise DailyDownloadLimitExceeded
    else:
        return x.content


def save_subs(content, full_path, other_details=None):
    ''' Saves the content to the specified full path '''

    open(full_path, 'wb').write(content)
    logger.debug('Saved subtitles %s. Details : %s' % (full_path,
                 other_details))


def multikeysort(items, columns):
    '''Sorts a list a of dictionary based on multiple keys.
       A column can be reverse sorted by specifying - in front of the field name.'''

    comparers = [((itemgetter(col[1:].strip()),
                 -1) if col.startswith('-'
                 ) else (itemgetter(col.strip()), 1)) for col in
                 columns]

    def comparer(left, right):
        for (fn, mult) in comparers:
            result = cmp(fn(left), fn(right))
            if result:
                return mult * result
        else:
            return 0

    return sorted(items, cmp=comparer)


logger = get_logger()
