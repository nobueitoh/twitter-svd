
import PyQt5.QtCore as QtCore
import PyQt5.QtGui as QtGui
import PyQt5.QtWidgets as QtWidgets
from kappa_ui import Ui_MainWindow
from pyqtgraph.opengl import GLScatterPlotItem, GLGridItem

import sys, twitter, configparser
import numpy as np
import scipy.sparse as sparse
from sklearn.decomposition import TruncatedSVD
from sklearn.feature_extraction.text import HashingVectorizer
from nltk.tokenize import TweetTokenizer
from nltk.corpus import stopwords

def preprocess(text):
    tok = TweetTokenizer(reduce_len=True)
    return [i for i in tok.tokenize(text) if i not in stopwords.words()]

class TweetStream(QtCore.QThread):
    svd_signal = QtCore.pyqtSignal('PyQt_PyObject')
    twt_signal = QtCore.pyqtSignal('PyQt_PyObject')
    def __init__(self, parent=None):
        QtCore.QThread.__init__(self, parent)
        self.svd = TruncatedSVD(n_components=3)
        self.hash = HashingVectorizer(tokenizer=preprocess,
                ngram_range=(1,1))
        self.data = None

    def run(self):
        config = configparser.ConfigParser()
        config.read('cfg.ini')
        config = config['DEFAULT']
        api = twitter.Api(consumer_key=config['consumer_key'],
                consumer_secret=config['consumer_secret'],
                access_token_key=config['access_token_key'],
                access_token_secret=config['access_token_secret'])

        for n, line in enumerate(api.GetStreamFilter(
                track=['pokemon','dark souls','darksouls','sonic','hedgehog'],
                languages=['en'])):
            if self.isInterruptionRequested():
                print('saving data...')
                np.save('tweets.npy', self.data)
                return
            try:
                v = self.hash.transform((line['text'],))
                self.twt_signal.emit(line['text'])
                if self.data == None:
                    self.data = sparse.csr_matrix(v)
                elif self.data.shape[0] % 100 != 0:
                    self.data = sparse.vstack((self.data,v))
                else:
                    self.data = sparse.vstack((self.data, v))
                    trans = self.svd.fit_transform(self.data)
                    self.svd_signal.emit(trans)
            except KeyError:
                pass

class App(QtWidgets.QMainWindow, Ui_MainWindow):
    def __init__(self, parent=None):
        QtWidgets.QMainWindow.__init__(self, parent)
        Ui_MainWindow.__init__(self)
        self.setupUi(self)
        
        xgrid, ygrid, zgrid = (GLGridItem() for i in range(3))
        xgrid.rotate(90,0,1,0)
        ygrid.rotate(90,1,0,0)
        self.plot = GLScatterPlotItem(pos=np.asarray([0,0,0]))
        self.graphicsView.addItem(self.plot)
        self.graphicsView.addItem(xgrid)
        self.graphicsView.addItem(ygrid)
        self.graphicsView.addItem(zgrid)
        self.graphicsView.setBackgroundColor((111,111,111))
        
        self.tweets = TweetStream(self)
        self.tweets.svd_signal.connect(self.processSVD)
        self.tweets.twt_signal.connect(self.processTweet)

        self.started = False
        self.pushButton.clicked.connect(self.processStartStop)

        self.show()

    def processSVD(self, data):
        self.plot.setData(pos=data*5, color=(1.0,0.0,0.0,1.0))

    def processTweet(self, text):
        self.plainTextEdit.appendPlainText(text)

    def processStartStop(self):
        if not self.started:
            self.tweets.start()
            self.started = True
        else:
            self.tweets.quit()
            self.started = False

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    ex = App()
    sys.exit(app.exec_())
