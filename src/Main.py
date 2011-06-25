#File browser(multiselect)

from PyQt4 import QtCore, QtGui
from gui import  Ui_MainWindow
import os, sys
import struct
import base64
import zlib

import logging.handlers

LOG_FILENAME = 'pysubd.log'

my_logger = logging.getLogger('MyLoggerSend')
my_logger.setLevel(logging.DEBUG)
# Add the log message handler to the logger
handler = logging.handlers.RotatingFileHandler(
              LOG_FILENAME, maxBytes=100000, backupCount=2)

my_logger.addHandler(handler)

if sys.version_info[0] == 3:
    from xmlrpc.client import ServerProxy, Error
else:
    from xmlrpclib import ServerProxy, Error

class pysubd(QtGui.QMainWindow):
    def __init__(self, parent=None):
        QtGui.QWidget.__init__(self, parent)
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.ui.cancelButton.setDisabled(True)
        self.ui.downloadButton.setDisabled(True)

#        self.ui.progressUpdate.append("------------PySubD Subtitle Downloader----------".center(1200))

        # Create thread object and connect its signals to methods on this object
        self.subd = SubtitleDownload()
        self.connect(self.subd, QtCore.SIGNAL("updategui(PyQt_PyObject)"), self.appendUpdates)
        self.connect(self.subd, QtCore.SIGNAL("updateFound()"), self.updateFound)
        self.connect(self.subd, QtCore.SIGNAL("updateAvailable()"), self.updateAvailable)
        self.connect(self.subd, QtCore.SIGNAL("updateDownloaded()"), self.updateDownloaded)

        QtCore.QObject.connect(self.ui.cancelButton, QtCore.SIGNAL("clicked()"), self.cancelDownload)
        self.ui.cancelButton.setDisabled(True)

    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls:
            event.accept()
        else:
            event.ignore()

    def dropEvent(self, event):
        if event.mimeData().hasUrls:
            event.setDropAction(QtCore.Qt.CopyAction)
            event.accept()
            links = []
            for url in event.mimeData().urls():
                links.append(str(url.toLocalFile()))
            self.ui.cancelButton.setEnabled(True)
            self.subd.init(links)

        else:
            event.ignore()

    def cancelDownload(self):
        self.subd.stopTask()
        self.ui.cancelButton.setDisabled(True)

        # Method called asynchronously by other thread when progress should be updated
    def appendUpdates(self, update):
        my_logger.debug(update)
        self.ui.progressUpdate.append(str(update))
        self.ui.scrollArea.verticalScrollBar().setValue(self.ui.scrollArea.verticalScrollBar().maximum())

    def updateFound(self):
        self.ui.foundlcdNumber.display(int(self.ui.foundlcdNumber.value() + 1))

    def updateAvailable(self):
        self.ui.availablelcdNumber.display(int(self.ui.availablelcdNumber.value() + 1))

    def updateDownloaded(self):
        self.ui.downloadedlcdNumber.display(int(self.ui.downloadedlcdNumber.value() + 1))

#    def startDownload(self, list):
#        self.ponderous.stopTask()
#        self.ui.downloadButton.setEnabled(True)
#        self.ui.cancelButton.setDisabled(True)
#        self.ui.startDate.setEnabled(True)
#        self.ui.endDate.setEnabled(True)
#        #Re-enable checkbox checkability once the download has been cancelled
#        self.checkBoxDisability(False)

class SubtitleDownload(QtCore.QThread):
    '''Traverses a directory and all subdirectories and downloads subtitles.
    
    Relies on an undocumented OpenSubtitles feature where subtitles seems to be
    sorted by filehash and popularity.
    '''

    api_url = 'http://api.opensubtitles.org/xml-rpc'
    login_token = None
    server = None

    def __init__(self, parent=None):
        QtCore.QThread.__init__(self, parent)


    def init(self, movie_paths):
        self._movie_paths = movie_paths
        self.start()

    def stopTask(self):
        self.stopping = True

    def run(self):
        self.stopping = False
        self.moviefiles = {}

        self.emit(QtCore.SIGNAL("updategui(PyQt_PyObject)"), "Searching for video files...")
        """Check if the movie_path is a file or directory.
            Calculate the file stats if its a file, else traverse the directory tree and calculate filestats for all movie files"""
        for path in self._movie_paths:
            if os.path.isfile(path):
                self.calcfilestats(path, os.path.dirname(path))
            else:
                for root, _, files in os.walk(path):
                    for file in files:
                        if not self.stopping:
                                self.calcfilestats(file, root)
                        else:
                            return

        try:
            self.login()
            self.emit(QtCore.SIGNAL("updategui(PyQt_PyObject)"), "Searching for subtitles...")
            self.search_subtitles()
            self.emit(QtCore.SIGNAL("updategui(PyQt_PyObject)"), "Done...")
            self.logout()
        except Error as e:
            self.emit(QtCore.SIGNAL("updategui(PyQt_PyObject)"), ("XML-RPC error:", e))

        except UserWarning as uw:
            self.emit(QtCore.SIGNAL("updategui(PyQt_PyObject)"), uw)

    def calcfilestats(self, file, parentdir):
        video_extns = [ '.avi', '.divx', '.mkv', '.mp4', '.ogg', '.rm', '.rmvb', '.vob', '.x264', '.xvid']

        if os.path.splitext(file)[1].lower() in video_extns:
                    self.emit(QtCore.SIGNAL("updategui(PyQt_PyObject)"), "Found: " + file)
                    self.emit(QtCore.SIGNAL("updateFound()"))

                    filehash = self.hashFile(os.path.join(parentdir, file))
                    filesize = os.path.getsize(os.path.join(parentdir, file))
                    self.moviefiles[filehash] = {'dir': parentdir,
                                                 'file': file,
                                                 'size': filesize}

    def login(self):
        '''Log in to OpenSubtitles'''
        self.server = ServerProxy(self.api_url, verbose=False)
        self.emit(QtCore.SIGNAL("updategui(PyQt_PyObject)"), "Logging in...")
        try:
            resp = self.server.LogIn('', '', 'en', 'OS Test User Agent')
            self.check_status(resp)
            self.login_token = resp['token']
        except Error as e:
            self.emit(QtCore.SIGNAL("updategui(PyQt_PyObject)"), e)



    def logout(self):
        '''Log out from OpenSubtitles'''
        self.emit(QtCore.SIGNAL("updategui(PyQt_PyObject)"), "Logging out...")
        resp = self.server.LogOut(self.login_token)
        self.check_status(resp)

    def search_subtitles(self):
        '''Search OpenSubtitles for matching subtitles using moviehash and filebytesize'''

        search = []

        for hash in self.moviefiles.keys():
            search.append({'sublanguageid': 'eng',
                           'moviehash': hash,
                           'moviebytesize': str(self.moviefiles[hash]['size'])})
        my_logger.debug("Length of search string: " + str(len(search)))

        resp = {}
        resp['data'] = []

        while search[:500]:
            if not self.stopping:
                tempresp = self.server.SearchSubtitles(self.login_token, search[:500])
                resp['data'].extend(tempresp['data'])
                self.check_status(tempresp)
                search = search[500:]
            else:
                return

        if resp['data'] == False:
            self.emit(QtCore.SIGNAL("updategui(PyQt_PyObject)"), "Sorry, no subtitles were found!")
            return

        # A dictionary to store the subtitle id's found corresponding to every file hash 
        subtitles = {}
        for result in resp['data']:
            if int(result['SubBad']) != 1 and not subtitles.get(result['MovieHash']):
                subtitles[result['MovieHash']] = {'subid':result['IDSubtitleFile'], 'downcount':result['SubDownloadsCnt']}
                self.emit(QtCore.SIGNAL("updateAvailable()"))

            elif int(result['SubBad']) != 1 and subtitles.get(result['MovieHash']) and int(subtitles.get(result['MovieHash'])['downcount']) < int(result['SubDownloadsCnt']):
                subtitles[result['MovieHash']] = {'subid':result['IDSubtitleFile'], 'downcount':result['SubDownloadsCnt']}

        my_logger.debug("Length of final subtitle string : " + str(len(subtitles)))

        notfound = []
        for hash, filedetails in self.moviefiles.iteritems():
            if not self.stopping:
                if subtitles.get(hash):
                        subtitle = self.download_subtitles([subtitles[hash]['subid']])
                        self.emit(QtCore.SIGNAL("updategui(PyQt_PyObject)"), "Saving subtitle for: " + filedetails['file'])
                        self.emit(QtCore.SIGNAL("updateDownloaded()"))
                        filename = os.path.join(filedetails['dir'], os.path.splitext(filedetails['file'])[0] + ".srt")
                        file = open(filename, "wb")
                        file.write(subtitle)
                        file.close()
                else:
                    notfound.append(filedetails['file'])
            else:
                return

        #Report all the files for which no subtitles were found.
        notfound.sort(key=str.lower)
        for file in notfound:
                self.emit(QtCore.SIGNAL("updategui(PyQt_PyObject)"), "No subtitles found for: " + file)

    def download_subtitles(self, subparam):
        resp = self.server.DownloadSubtitles(self.login_token, subparam)
        self.check_status(resp)
        decoded = base64.standard_b64decode(resp['data'][0]['data'].encode('ascii'))
        decompressed = zlib.decompress(decoded, 15 + 32)
        return decompressed

    def check_status(self, resp):
        '''Check the return status of the request.
        
        Anything other than "200 OK" raises a UserWarning
        '''
        if resp['status'].upper() != '200 OK':
            raise UserWarning("Response error from " + self.api_url + ". Response status was: " + resp['status'])

    def hashFile(self, name):
        ''' Calculates the hash value of a movie.
            Copied from OpenSubtitles own examples:
            http://trac.opensubtitles.org/projects/opensubtitles/wiki/HashSourceCodes
        '''
        try:
            longlongformat = 'q'  # long long 
            bytesize = struct.calcsize(longlongformat)

            f = open(name, "rb")

            filesize = os.path.getsize(name)
            hash = filesize

            if filesize < 65536 * 2:
                return "SizeError: Minimum file size must be 120Kb"

            for x in range(65536 // bytesize):
                buffer = f.read(bytesize)
                (l_value,) = struct.unpack(longlongformat, buffer)
                hash += l_value
                hash = hash & 0xFFFFFFFFFFFFFFFF #to remain as 64bit number  

            f.seek(max(0, filesize - 65536), 0)
            for x in range(65536 // bytesize):
                buffer = f.read(bytesize)
                (l_value,) = struct.unpack(longlongformat, buffer)
                hash += l_value
                hash = hash & 0xFFFFFFFFFFFFFFFF

            f.close()
            returnedhash = "%016x" % hash
            return returnedhash
        except(IOError):
            return "IOError"

#Start the program
app = QtGui.QApplication(sys.argv)
window = pysubd()
window.show()
sys.exit(app.exec_())
