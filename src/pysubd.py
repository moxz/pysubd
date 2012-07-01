#TODO:case of no internet connection or  a midway disconnection

from PyQt4 import QtCore, QtGui
from gui.mainwindow_ui import  Ui_MainWindow
import os
import sys
import struct
import base64
import zlib
from socket import gaierror as noInternetConnection

import logging.handlers

LOG_FILENAME = 'pysubd.log'

my_logger = logging.getLogger('pysubdLogger')
my_logger.setLevel(logging.DEBUG)
handler = logging.handlers.RotatingFileHandler(
              LOG_FILENAME, maxBytes=150000)

my_logger.addHandler(handler)

import platform
if platform.system()=='Windows' and platform.release()=='7':
        import ctypes
        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID('pysubd')

if sys.version_info[0] == 3:
    from xmlrpc.client import ServerProxy, Error
else:
    from xmlrpclib import ServerProxy, Error


class FileDialog(QtGui.QFileDialog):
    def __init__(self, *args):
        QtGui.QFileDialog.__init__(self, *args)
        self.setOption(self.DontUseNativeDialog, True)
        self.setFileMode(self.ExistingFiles)
        btns = self.findChildren(QtGui.QPushButton)
        self.openBtn = [x for x in btns if 'open' in str(x.text()).lower()][0]
        self.openBtn.clicked.disconnect()
        self.openBtn.clicked.connect(self.openClicked)
        self.tree = self.findChild(QtGui.QTreeView)
        self.selectedFiles = []

    def openClicked(self):
        inds = self.tree.selectionModel().selectedIndexes()
        files = []
        for i in inds:
            if i.column() == 0:
                pth = str(self.directory().absoluteFilePath(i.data().toString()))
                if os.path.isdir(pth):
                    pth = pth + '/'
                files.append(pth)
        self.selectedFiles = files
        self.hide()

    def filesSelected(self):
        return self.selectedFiles


class pysubd(QtGui.QMainWindow):
    def __init__(self, parent=None):
        QtGui.QWidget.__init__(self, parent)
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.ui.cancelButton.setDisabled(True)
        self.tobeSearched = []
        self.ui.progressUpdate.append("--------------------------------------------PySubD Subtitle Downloader-------------------------------------------")
        self.ui.progressUpdate.append("------------------------------Drag and drop your movie files or folders here--------------------------------")
        self.subd = SubtitleDownload()
        self.connect(self.subd, QtCore.SIGNAL("updategui(PyQt_PyObject)"), self.appendUpdates)
        self.connect(self.subd, QtCore.SIGNAL("updateFound()"), self.updateFound)
        self.connect(self.subd, QtCore.SIGNAL("updateAvailable()"), self.updateAvailable)
        self.connect(self.subd, QtCore.SIGNAL("updateDownloaded()"), self.updateDownloaded)
        self.connect(self.subd, QtCore.SIGNAL("downloadComplete(PyQt_PyObject)"), self.downloadComplete)

        QtCore.QObject.connect(self.ui.cancelButton, QtCore.SIGNAL("clicked()"), self.cancelDownload)
        QtCore.QObject.connect(self.ui.browseButton, QtCore.SIGNAL("clicked()"), self.openFileDialog)

        self.cancelled = False
        self.ui.authorLabel.setOpenExternalLinks(True)
        self.ui.cancelButton.setDisabled(True)

    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls:
            event.accept()
        else:
            event.ignore()

    def dropEvent(self, event):
        self.cancelled = False
        if event.mimeData().hasUrls:
            event.setDropAction(QtCore.Qt.CopyAction)
            event.accept()
            links = []
            for url in event.mimeData().urls():
                links.append(str(url.toLocalFile()))

            self.ui.cancelButton.setEnabled(True)
            if self.tobeSearched:
                self.tobeSearched.extend(links)
            else:
                self.tobeSearched.extend(links)
                self.subd.init(links)
        else:
            event.ignore()

    def openFileDialog(self):
        self.cancelled = False
        d = FileDialog()
        d.exec_()
        x = d.filesSelected()

        if x:
            self.ui.cancelButton.setEnabled(True)
            self.ui.browseButton.setDisabled(True)
            self.tobeSearched.extend(x)
            self.subd.init(x)

    def cancelDownload(self):
        self.cancelled = True
        self.subd.stopTask()
        self.ui.cancelButton.setDisabled(True)
        self.ui.browseButton.setEnabled(True)

    def downloadComplete(self, donepaths):
        for path in donepaths:
            self.tobeSearched.remove(str(path))
        if self.tobeSearched and not self.cancelled:
            self.ui.browseButton.setDisabled(True)
            self.ui.cancelButton.setEnabled(True)
            self.subd.init(self.tobeSearched)
        else:
            self.ui.cancelButton.setDisabled(True)
            self.ui.browseButton.setEnabled(True)

    def appendUpdates(self, update):
        self.ui.progressUpdate.append(str(update))
        self.ui.scrollArea.verticalScrollBar().setValue(self.ui.scrollArea.verticalScrollBar().maximum())

    def updateFound(self):
        self.ui.foundlcdNumber.display(int(self.ui.foundlcdNumber.value() + 1))

    def updateAvailable(self):
        self.ui.availablelcdNumber.display(int(self.ui.availablelcdNumber.value() + 1))

    def updateDownloaded(self):
        self.ui.downloadedlcdNumber.display(int(self.ui.downloadedlcdNumber.value() + 1))


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

    def __del__(self):
        if self.login_token:
            self.logout()

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
            if self.moviefiles:
                if not self.login_token:
                    try:
                        self.login()
                    except (noInternetConnection):
                        self.emit(QtCore.SIGNAL("updategui(PyQt_PyObject)"), "Sorry, No active Internet connection found. Re-Check and try again.")
                        my_logger.debug("Sorry, No active Internet connection found. Re-Check and try again.")
                        self.emit(QtCore.SIGNAL("downloadComplete(PyQt_PyObject)"), self._movie_paths)
                        return

                self.emit(QtCore.SIGNAL("updategui(PyQt_PyObject)"), "Searching for subtitles...")
                self.search_subtitles()
                self.emit(QtCore.SIGNAL("updategui(PyQt_PyObject)"), "Done...")
                my_logger.debug("Done...")
            else:
                self.emit(QtCore.SIGNAL("updategui(PyQt_PyObject)"), "Sorry, no video files were found!")
            self.emit(QtCore.SIGNAL("downloadComplete(PyQt_PyObject)"), self._movie_paths)

        except Error as e:
            self.emit(QtCore.SIGNAL("updategui(PyQt_PyObject)"), ("XML-RPC error:", e))

        except UserWarning as uw:
            self.emit(QtCore.SIGNAL("updategui(PyQt_PyObject)"), uw)

    def calcfilestats(self, file, parentdir):
        ''' Calculates and adds the hash of a movie file to the moviefiles dictionary.
            Also emits a signal to update the LCD counter showing the found files.'''
        video_extns = ['.avi', '.divx', '.mkv', '.mp4', '.ogg', '.rm', '.rmvb', '.vob', '.x264', '.xvid']
        if os.path.splitext(file)[1].lower() in video_extns:
                    self.emit(QtCore.SIGNAL("updategui(PyQt_PyObject)"), "Found: " + file)
                    my_logger.debug("Found: " + file)
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
        my_logger.debug("Logging in...")
        try:
            resp = self.server.LogIn('', '', 'en', 'PySubD v1.0')
            self.check_status(resp)
            self.login_token = resp['token']
        except Error as e:
            self.emit(QtCore.SIGNAL("updategui(PyQt_PyObject)"), e)
            my_logger.debug(str(e))

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
                        if tempresp['data'] != False:
                                resp['data'].extend(tempresp['data'])
                        self.check_status(tempresp)
                        search = search[500:]
                else:
                        return

        #Check if we actually got some matching subtitles to download, else return
        if not resp['data']:
            self.emit(QtCore.SIGNAL("updategui(PyQt_PyObject)"), "Sorry, no subtitles were found!")
            my_logger.debug("Sorry, no subtitles were found!")
            return

        #User Ranks on OpenSubtitles.org.These are decided based upon the number of subtitles uploaded by the member.
        #A better rank is often an indication of a better subtitle quality.
        user_ranks = {'administrator': 1, 'platinum member': 2, 'vip member': 3, 'gold member': 4, 'trusted': 5, 'silver member': 6,
                         'bronze member': 7, 'sub leecher': 8, '': 9}
        # A dictionary to store the subtitle id's found corresponding to every file hash
        subtitles = {}
        for result in resp['data']:
            #The subtitle must not be rated bad
            if int(result['SubBad']) != 1:
                hash = result['MovieHash']
                subid = result['IDSubtitleFile']
                downcount = result['SubDownloadsCnt']
                rating = result['SubRating']
                user_rank = user_ranks[result['UserRank']]

                #First good matching subtitle found
                if not subtitles.get(hash):
                    subtitles[hash] = {'subid': subid, 'downcount': downcount, 'rating': rating, 'user_rank': user_rank}
                    self.emit(QtCore.SIGNAL("updateAvailable()"))

                #Another good quality subtitle found uploaded by a more reputed user
                elif subtitles[hash]['user_rank'] > user_rank:
                    subtitles[hash] = {'subid': subid, 'downcount': downcount, 'rating': rating, 'user_rank': user_rank}

                #Another good quality subtitle found with a perfect rating, uploaded by a more or equally reputed user
                elif float(rating) == 10.0 and subtitles[hash]['user_rank'] >= user_rank:
                    subtitles[hash] = {'subid': subid, 'downcount': downcount, 'rating': rating, 'user_rank': user_rank}

                #Another good quality subtitle found with the better rating, higher download count and uploaded by a more or equally trusted user
                elif float(subtitles[hash]['rating']) >= float(rating) \
                and int(subtitles[hash]['downcount']) < int(downcount) and subtitles[hash]['user_rank'] >= user_rank:
                    subtitles[hash] = {'subid': subid, 'downcount': downcount, 'rating': rating, 'user_rank': user_rank}

        my_logger.debug("Total number of subtitles found: " + str(len(subtitles)))

        notfound = []
        for hash, filedetails in self.moviefiles.iteritems():
            if not self.stopping:
                if subtitles.get(hash):
                    try:
                        subtitle = self.download_subtitles([subtitles[hash]['subid']])
                        self.emit(QtCore.SIGNAL("updategui(PyQt_PyObject)"), "Saving subtitle for: " + filedetails['file'])
                        my_logger.debug("Saving subtitle for: " + filedetails['file'] + "  Hash : " + hash + " Rating: " +
                                        subtitles[hash]['rating'] + " DwnCnt: " + subtitles[hash]['downcount'] + " UpldrRnk:" + \
                                        str(subtitles[hash]['user_rank']))
                        self.emit(QtCore.SIGNAL("updateDownloaded()"))
                        filename = os.path.join(filedetails['dir'], os.path.splitext(filedetails['file'])[0] + ".srt")
                        file = open(filename, "wb")
                        file.write(subtitle)
                        file.close()
                    except IOError:
                        self.emit(QtCore.SIGNAL("updategui(PyQt_PyObject)"), "IO Error in saving subs for  " + filedetails['file'])

                else:
                    notfound.append(filedetails['file'])
            else:
                return

        #Report all the files for which no subtitles were found in an alphabetically sorted order.
        notfound.sort(key=str.lower)
        for file in notfound:
                self.emit(QtCore.SIGNAL("updategui(PyQt_PyObject)"), "No subtitles found for: " + file)
                my_logger.debug("No subtitles were found for: " + file)

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
                hash = hash & 0xFFFFFFFFFFFFFFFF  # to remain as 64bit number

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
