#!/usr/bin/python
# -*- coding: utf-8 -*-

from PyQt4 import QtCore
import os
import traceback
from opensubs import Site
import utils
from PyQt4.QtCore import pyqtSlot
import queue
import time

communicator = utils.communicator


class SubtitleDownload(QtCore.QThread):

    '''Traverses a directory and all subdirectories and downloads
        the best available subtitles.'''


    def __init__(self, parent=None):
        QtCore.QThread.__init__(self, parent)
        self.queue = queue.Queue()
        self.not_found = []
        communicator.no_sub_found.connect(self.append_to_not_found)
        communicator.reprocess.connect(self.add_to_q)
        self.sites = {'Addic7ed': Site().create('Addic7ed'),
                      'OpenSubtitles': Site().create('OpenSubtitles')}

    def init(self, videos_pathlist, lang):
        self.videos_pathlist = videos_pathlist
        self.lang = lang
        self.start()

    def stopTask(self):
        self.cancelled = True
        for (site_name, site_instance) in self.sites.iteritems():
                site_instance.stopTask()

    def run(self):
        self.cancelled = False
        self.videofiles_queue = {}
        communicator.updategui.emit('Searching for video files...', 'info'
                )
        self.check_and_add()
        try:
            self.process_queue()
        except utils.NoInternetConnectionFound:
            communicator.updategui.emit('No active Internet connection found. Kindly check and try again.',
                    'error')
        except:
            communicator.updategui.emit('An unknown exception occured:\n%s'
                 % traceback.format_exc(), 'error')
        self.print_not_found()
        communicator.updategui.emit('Done...', 'info')
        communicator.all_download_complete.emit(self.videos_pathlist)
        
    def check_and_add(self):
        for path in self.videos_pathlist:
            if os.path.isfile(path):
                if utils.is_video_file(path):
                    self.add_to_processing_queue(os.path.basename(path),
                            os.path.dirname(path))
            else:
                for (root, _, files) in os.walk(path):
                    for filename in files:
                        if not self.cancelled:
                            if utils.is_video_file(filename):
                                self.add_to_processing_queue(filename,
                                        root)
                        else:
                            return

    def add_to_processing_queue(self, filename, parentdir):
        communicator.updategui.emit('Found: %s'% filename, 'info')
        communicator.found_video_file.emit(filename)

        filehash = utils.calc_file_hash(os.path.join(parentdir,
                filename))
        filesize = os.path.getsize(os.path.join(parentdir, filename))
        save_to_path = os.path.join(parentdir,
                                    os.path.splitext(filename)[0]
                                    + '.srt')
        self.queue.put({'file_name': filename,
                        'type': 'Addic7ed' if utils.check_tvshow(filename) else 'OpenSubtitles',
                        'save_subs_to': save_to_path,
                        'moviehash':filehash,
                        'moviebytesize': str(filesize)})

    def catch_all(self, site, files, lang):
        try:
            self.sites[site].process(files, self.lang)
            self.sites[site].wait()
        except utils.IncorrectResponseRecieved:
            communicator.updategui.emit('Exception: IncorrectResponseRecieved', 'error'
                    )
        except UserWarning as uw:
            communicator.updategui.emit(uw, 'error')
        except utils.DailyDownloadLimitExceeded:
            communicator.updategui.emit('You have reached your daily download limit for Addic7ed.com', 'error')

    def process_queue(self):
        addic7ed_list = []
        opensubs_dict = {}
        
        for x in range(self.queue.qsize()):
            video = self.queue.get_nowait()
            if video['type'] == 'Addic7ed':
                addic7ed_list.append(video)
            else:
                self.queue.put_nowait(video)
        
        if addic7ed_list:
            self.catch_all('Addic7ed', addic7ed_list, self.lang)
        
        time.sleep(0.01) #To prevent race condition

        opensubs_list = [self.queue.get_nowait() for x in range(self.queue.qsize())]
        for x in opensubs_list:
            opensubs_dict[x['moviehash']] = x
        if opensubs_dict:
            self.catch_all('OpenSubtitles', opensubs_dict, self.lang)

    @pyqtSlot(object)
    def append_to_not_found(self, filename):
        self.not_found.append(filename)

    @pyqtSlot(object)
    def add_to_q(self, data):
        self.queue.put(data)

    def print_not_found(self):
        self.not_found.sort(key=str.lower)
        for file_name in self.not_found:
            communicator.updategui.emit('No subtitles found for: %s'% file_name, 'error')
        self.not_found = []