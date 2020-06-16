import configparser, twitter, logging, json, sys, time
import PyQt5.QtCore as QtCore
import PyQt5.QtGui as QtGui
import PyQt5.QtWidgets as QtWidgets
from mw import Ui_MainWindow

class StreamThread(QtCore.QThread):
    signal = QtCore.pyqtSignal('PyQt_PyObject')
    def __init__(self, topics, parent=None):
        QtCore.QThread.__init__(self, parent)
        self.topics = topics

    def run(self):
        config = configparser.ConfigParser()
        config.read('cfg.ini')
        api = twitter.Api(consumer_key=config['DEFAULT']['consumer_key'],
                consumer_secret=config['DEFAULT']['consumer_secret'],
                access_token_key=config['DEFAULT']['access_token_key'],
                access_token_secret=config['DEFAULT']['access_token_secret'])
        for line in api.GetStreamFilter(
                track=self.topics.split(','),
                languages=['en']):
            try:
                self.signal.emit(
                        "@{}: {}".format(
                            line['user']['screen_name'],line['text']
                            )
                        )
            except KeyError:
                pass

class App(QtWidgets.QMainWindow, Ui_MainWindow):
    def __init__(self, parent=None):
        QtWidgets.QMainWindow.__init__(self, parent)
        Ui_MainWindow.__init__(self)
        self.setupUi(self)
        self.thread = None
        self.pushButton.setText('Start')
        self.pushButton.clicked.connect(self.handleStartClicked)

        #set up connections

        self.show()

    def handleStartClicked(self):
        self.thread = StreamThread(self.lineEdit.text(), self)
        self.thread.signal.connect(self.textEdit.append)
        self.pushButton.setText('Stop')
        self.pushButton.clicked.disconnect()
        self.pushButton.clicked.connect(self.handleStopClicked)
        self.thread.setTerminationEnabled(True)
        self.thread.start()

    def handleStopClicked(self):
        self.thread.terminate()
        self.thread.wait()
        self.thread = None
        self.pushButton.setText('Start')
        self.pushButton.clicked.disconnect()
        self.pushButton.clicked.connect(self.handleStartClicked)

    def handleThread(self, s):
        self.textEdit.append(s)

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    ex = App()
    sys.exit(app.exec_())
