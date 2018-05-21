#import sys, time
#from PyQt4.QtCore import Qt, QTimer
from PyQt4.QtGui import *
    
class MovieSplashScreen(QSplashScreen):
    
    def __init__(self, movie, parent = None):
     
        movie.jumpToFrame(0)
        pixmap = QPixmap(movie.frameRect().size())
        
        QSplashScreen.__init__(self, pixmap)
        self.movie = movie
        self.movie.frameChanged.connect(self.repaint)
    
    def showEvent(self, event):
        self.movie.start()
    
    def hideEvent(self, event):
        self.movie.stop()
    
    def paintEvent(self, event):
    
        painter = QPainter(self)
        pixmap = self.movie.currentPixmap()
        self.setMask(pixmap.mask())
        painter.drawPixmap(0, 0, pixmap)
    
    def sizeHint(self):
    
        return self.movie.scaledSize()

'''
if __name__ == "__main__":
   
    app = QApplication(sys.argv)
#    movie = QMovie("animation.gif")
    movie = QMovie("ogn-logo-ani.gif")

    splash = MovieSplashScreen(movie)
    splash.show()
    
    start = time.time()
    
    while movie.state() == QMovie.Running and time.time() < start + 10:
        app.processEvents()
    
    window = QWidget()
    window.show()
    splash.finish(window)
    
    sys.exit(app.exec_())
'''