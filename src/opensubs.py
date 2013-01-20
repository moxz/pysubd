#!/usr/bin/python
# -*- coding: utf-8 -*-

#   This file is part of periscope.
#   Copyright (c) 2008-2011 Patrick Dessalle <patrick@dessalle.be>
#
#    periscope is free software; you can redistribute it and/or modify
#    it under the terms of the GNU Lesser General Public License as published by
#    the Free Software Foundation; either version 2 of the License, or
#    (at your option) any later version.
#
#    periscope is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Lesser General Public License for more details.
#
#    You should have received a copy of the GNU Lesser General Public License
#    along with periscope; if not, write to the Free Software
#    Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA

from PyQt4 import QtCore
import re
from bs4 import BeautifulSoup
import sys
import traceback
import utils
import zlib
import base64
from operator import itemgetter

# Python 3 compatibility

if sys.version_info[0] == 3:
    from xmlrpc.client import ServerProxy, Error
else:
    from xmlrpclib import ServerProxy, Error

logger = utils.logger

LANGUAGES = {
    u'English': ('1', 'eng'),
    u'French': ('8', 'fre'),
    u'Greek': ('27', 'ell'),
    u'Spanish': ('4', 'spa'),
    u'Portuguese(Br)': ('10', 'pob'),
    u'Italian': ('7', 'ita'),
    }


class Site(object):

    def __init__(self):
        self.Addic7ed = Addic7ed()
        self.OpenSubtitles = OpenSubtitles()

    def create(self, site):
        if site == 'Addic7ed':
            return self.Addic7ed
        elif site == 'OpenSubtitles':
            return self.OpenSubtitles


class Addic7ed(QtCore.QThread):

    host = 'http://www.addic7ed.com'
    logger = utils.logger

    def __init__(self, parent=None):
        QtCore.QThread.__init__(self, parent)
        self.stopping = False

    def process(self, files_list, lang='English'):
        '''Given filename and the wished language, searches and downloads the best match found from Addic7ed.com'''

        self.lang = lang
        utils.communicator.updategui.emit('Querying Addic7ed.com...', 'info')

        for details_dict in files_list[:]:
            if not self.stopping:
                filename = details_dict['file_name']
                save_to = details_dict['save_subs_to']

                (searched_url, downloadlink) = self._query(filename)
                if downloadlink:
                    try:
                        subs = self.download_subtitles(searched_url,
                                downloadlink, filename)
                    except utils.DailyDownloadLimitExceeded:
                        for details_dict in files_list:
                            utils.communicator.reprocess.emit(details_dict)
                        raise
                    utils.save_subs(subs, save_to)
                    files_list.remove(details_dict)
                    utils.communicator.downloaded_sub.emit()
                else:
                    utils.communicator.reprocess.emit(details_dict)

    def stopTask(self):
        self.stopping = True

    def _listTeams(self, subteams, separators):
        for sep in separators:
            subteams = self._splitTeam(subteams, sep)
        return set(subteams)

    def _splitTeam(self, subteams, sep):
        teams = []
        for t in subteams:
            teams += t.split(sep)
        return teams

    def _query(self, filename):
        utils.communicator.updategui.emit('Searching Addic7ed.com for %s'
                 % filename, 'info')
        guessed_file_data = utils.guess_file_data(filename)
        name = guessed_file_data.get('name')
        season = guessed_file_data.get('season')
        episode = guessed_file_data.get('episode')
        teams = guessed_file_data.get('teams')

        lang_url = LANGUAGES[self.lang][0]
        searchurl = '%s/serie/%s/%s/%s/%s' % (self.host, name, season,
                episode, lang_url)

        name = name.lower().replace(' ', '_')
        teams = set(teams)
        self.logger.debug('[Addic7ed] Searched URL for %s:  %s'
                          % (filename, searchurl))
        best_match = None

        page_html = utils.download_url_content(searchurl)
        if not page_html.strip():
            return (searchurl, None)
        soup = BeautifulSoup(page_html)
        release_pattern = \
            re.compile('Version (.+), ([0-9]+).([0-9])+ MBs')

        try:
            sub_list = soup.findAll('td', {'class': 'NewsTitle','colspan': '3'})
            result = []

            for subs in sub_list:
                subteams = \
                    release_pattern.match(subs.contents[1].strip()).groups()[0].lower()
                subteams = self._listTeams([subteams], ['.', '_', ' '])
                langs_html = subs.find_next('td', {'class': 'language'})
                statusTD = langs_html.find_next('td')
                status = statusTD.text.strip()
                links = statusTD.find_next('td').find_all('a')
                link = '%s%s' % ('http://www.addic7ed.com',
                                 links[len(links) - 1]['href'])
                self.logger.debug('[Addic7ed] Team from website: %s'
                                  % subteams)
                self.logger.debug('[Addic7ed] Team from file: %s'
                                  % teams)

                b = {}
                b['link'] = link

                if status == 'Completed':
                    b['completed'] = 1
                    sub_quality = subs.parent.parent.find_all('a',
                            {'class': 'buttonDownload'})[0].text
                    if sub_quality == u'original' or sub_quality \
                        == u'most updated':
                        b['best_match'] = 1
                    else:
                        b['best_match'] = 0
                else:
                    b['completed'] = 0

                if subteams.issubset(teams):
                    b['overlap'] = len(set.intersection(teams,
                            subteams))
                else:
                    b['overlap'] = 0
                result.append(b)
        except:
            utils.communicator.updategui.emit('Following unknown exception occured:\n%s'
                     % traceback.format_exc(), 'error')
        else:
            if result:
                # Sort the results found by completed, overlapping, best_match

                best_match = sorted(result, key=itemgetter('completed',
                                    'overlap', 'best_match'),
                                    reverse=True)[0]
                self.logger.debug('A best match subtitle for %s found at %s'
                                   % (searchurl, best_match.get('link',
                                  None)))
        return (searchurl, best_match.get('link') if best_match else None)

    def download_subtitles(
        self,
        searchurl,
        link,
        filename,
        ):

        referer = searchurl.replace('_', ' ')
        utils.communicator.updategui.emit('Saving subtitles for %s...'
                % filename, 'success')
        return utils.download_url_content(link, referer)


class OpenSubtitles(QtCore.QThread):

    api_url = 'http://api.opensubtitles.org/xml-rpc'
    login_token = None
    server = None
    logger = utils.logger

    def __init__(self, parent=None):
        QtCore.QThread.__init__(self, parent)

    def process(self, files_list, lang='English'):
        self.moviefiles = files_list
        self.imdbid_to_hash = {}
        self.lang = LANGUAGES[lang][1]
        self.start()

    def __del__(self):
        if self.login_token:
            self.logout()

    def stopTask(self):
        self.stopping = True

    def run(self):
        self.stopping = False
        utils.communicator.updategui.emit('Querying OpenSubtitles.org...', 'info'
                )

        if not self.login_token:
            self.login()
        self.search_subtitles()

    def login(self):
        '''Log in to OpenSubtitles.org'''

        self.server = ServerProxy(self.api_url, verbose=False)
        utils.communicator.updategui.emit('Logging in to OpenSubtitles.org...', 'info'
                )
        try:
            resp = self.server.LogIn('', '', 'en', 'PySubD v2.0')
            self.check_status(resp)
            self.login_token = resp['token']
        except Error, e:
            utils.communicator.updategui.emit(e, 'error')

    def logout(self):
        '''Log out from OpenSubtitles'''

        utils.communicator.updategui.emit('Logging out...', 'info')
        resp = self.server.LogOut(self.login_token)
        self.check_status(resp)

    def check_status(self, resp):
        '''Check the return status of the request.
        Anything other than "200 OK" raises a UserWarning
        '''

        if resp['status'].upper() != '200 OK':
            raise utils.IncorrectResponseRecieved('Response error from %s. Response status: %s'
                     % (self.api_url, resp['status']))

    def _query_opensubs(self, search):
        results = []
        while search[:500]:
            if not self.stopping:
                tempresp = self.server.SearchSubtitles(self.login_token, search[:500])
                if tempresp['data']:
                    results.extend(tempresp['data'])
                self.check_status(tempresp)
                search = search[500:]
            else:
                return
        return results

    def clean_results(self, results, imdb=False):
        subtitles = {}
        user_ranks = {  'administrator': 1,
                        'platinum member': 2,
                        'vip member': 3,
                        'gold member': 4,
                        'trusted': 5,
                        'silver member': 6,
                        'bronze member': 7,
                        'sub leecher': 8,
                        '': 9, }

        for result in results:
            if result['SubBad'] != '1':
                movie_hash = result.get('MovieHash')
                if not movie_hash:
                    movie_hash = self.imdbid_to_hash[int(result['IDMovieImdb'])]
                subid = result['IDSubtitleFile']
                downcount = int(result['SubDownloadsCnt'])
                rating = float(result['SubRating'])
                user_rank = user_ranks[result['UserRank']]

                if imdb:
                    cleaned_release_name = utils.clean_name(result['MovieReleaseName'])
                    file_name = self.moviefiles[movie_hash]['file_name']
                    cleaned_file_name = utils.clean_name(file_name)
                    overlap = len(set.intersection(set(cleaned_release_name), set(cleaned_file_name)))
                else:
                    overlap = 0

                subtitles.setdefault(movie_hash, []).append({
                    'subid': subid,
                    'downcount': downcount,
                    'rating': rating,
                    'user_rank': user_rank,
                    'overlap' : overlap
                    })

        return subtitles

    def search_subtitles(self):
        search = []

        for video_file_details in self.moviefiles.itervalues():
            video_file_details['sublanguageid'] = self.lang
            search.append(video_file_details)
        
        results = self._query_opensubs(search)
        subtitles = self.clean_results(results)

        for (hash, found_matches) in subtitles.iteritems():
            subtitles[hash] = utils.multikeysort(found_matches,
                    ['overlap', 'user_rank', '-rating', '-downcount'])[0]

        for (hash, filedetails) in self.moviefiles.iteritems():
            if not self.stopping:
                if subtitles.get(hash):
                    utils.communicator.updategui.emit('Saving subtitles for %s'%filedetails['file_name'], 'success')
                    subtitle = \
                        self.download_subtitles([subtitles[hash]['subid'
                            ]])
                    utils.communicator.downloaded_sub.emit()
                    utils.save_subs(subtitle, filedetails['save_subs_to'],
                                    subtitles[hash])
                else:
                    utils.communicator.no_sub_found.emit(filedetails['file_name'])
            else:
                return


    def download_subtitles(self, subparam):
        resp = self.server.DownloadSubtitles(self.login_token, subparam)
        self.check_status(resp)
        decoded = base64.standard_b64decode(resp['data'][0]['data'
                ].encode('ascii'))
        decompressed = zlib.decompress(decoded, 15 + 32)
        return decompressed
