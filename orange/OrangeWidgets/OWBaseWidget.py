#
# OWWidget.py
# Orange Widget
# A General Orange Widget, from which all the Orange Widgets are derived
#

import sys
import ConfigParser,os
import orange
from string import *
import cPickle
from OWTools import *
from OWAboutX import *
from orngSignalManager import *



class ExampleTable(orange.ExampleTable):
    pass

class ExampleTableWithClass(ExampleTable):
    pass

class SignalWrapper:
    def __init__(self, widget, method):
        self.widget = widget
        self.method = method

    def __call__(self, *k):
        signalManager.signalProcessingInProgress += 1
        apply(self.method, k)
        signalManager.signalProcessingInProgress -= 1
        if not signalManager.signalProcessingInProgress:
            signalManager.processNewSignals(self.widget)


class OWBaseWidget(QDialog):
    def __init__(
    self,
    parent=None,
    title="Qt Orange BaseWidget",
    description="This a base for OWWidget. It encorporates saving, loading settings and signal processing.",
    wantSettings=FALSE,
    wantGraph = FALSE, 
    wantAbout = TRUE,
    icon="OrangeWidgetsIcon.png",
    logo="OrangeWidgetsLogo.png",
    modal=FALSE
    ):
        """
        Initialization
        Parameters: 
            title - The title of the\ widget, including a "&" (for shortcut in about box)
            description - self explanatory
            wantSettings - display settings button or not
            icon - the icon file
            logo - the logo file
        """
        fullIcon = sys.prefix + "/lib/site-packages/Orange/OrangeWidgets/icons/" + icon
        logo = sys.prefix + "/lib/site-packages/Orange/OrangeWidgets/icons/" + logo
        self.widgetDir = sys.prefix + "/lib/site-packages/Orange/OrangeWidgets/"
        self.title = title.replace("&","")
        self.captionTitle=title.replace("&","")

        # if we want the widget to show the title then the title must start with "Qt"
        if self.captionTitle[:2].upper != "QT":
            self.captionTitle = "Qt " + self.captionTitle

        apply(QDialog.__init__, (self, parent, title, modal, Qt.WStyle_Customize + Qt.WStyle_NormalBorder + Qt.WStyle_Title + Qt.WStyle_SysMenu + Qt.WStyle_Minimize))

        # number of control signals, that are currently being processed
        # needed by signalWrapper to know when everything was sent
        #self.stackHeight = 0
        self.needProcessing = 0

        self.inputs = []     # signalName:(dataType, handler, onlySingleConnection)
        self.outputs = []    # signalName: dataType
        self.wrappers =[]    # stored wrappers for widget events
        self.linksIn = {}      # signalName : (dirty, widgetFrom, handler, signalData)
        self.linksOut = {}       # signalName: signalData
    
        #the map with settings
        if not hasattr(self, 'settingsList'):
            self.__class__.settingsList = []

        #the title
        self.setCaption(self.captionTitle)
        self.setIcon(QPixmap(fullIcon))

        #about box
        self.about=OWAboutX(title,description,fullIcon,logo)
        self.buttonBackground=QVBox(self)
        if wantSettings: self.settingsButton=QPushButton("&Settings",self.buttonBackground)
        if wantGraph:    self.graphButton=QPushButton("&Save Graph",self.buttonBackground)
        if wantAbout:
            self.aboutButton=QPushButton("&About",self.buttonBackground)
            self.connect(self.aboutButton,SIGNAL("clicked()"),self.about.show)

        self.mainArea=QWidget(self)
        self.controlArea=QVBox(self)
        self.space=QVBox(self)
        
    # put this widget on top of all windows
    def reshow(self):
        self.hide()
        self.show()

    def send(self, signalName, value):
        self.linksOut[signalName] = value
        signalManager.send(self, signalName, value)
       
    def setSettings(self,settings):
        """
        Set all settings
        settings - the map with the settings
        """
        self.__dict__.update(settings)

    def getSettings(self):
        """
        Get all settings
        returns map with all settings
        """
        return dict([(x, getattr(self, x, None)) for x in settingsList])
   
    def loadSettings(self, file = None):
        """
        Loads settings from the widget's .ini file
        """
        if hasattr(self, "settingsList"):
            if file==None:
                file = self.widgetDir + self.title + ".ini"
            if type(file) == str:
                if os.path.exists(file):
                    file = open(file, "r")
                    settings = cPickle.load(file)
                    file.close()
                else:
                    settings = {}
            else:
                settings = cPickle.load(file)
            
            self.__dict__.update(settings)

        
    def saveSettings(self, file = None):
        if hasattr(self, "settingsList"):
            settings = dict([(name, getattr(self, name)) for name in self.settingsList])
            if file==None:
                file = self.widgetDir + self.title + ".ini"                
            if type(file) == str:
                file = open(file, "w")
                cPickle.dump(settings, file)
                file.close()
            else:
                cPickle.dump(settings, file)

    def loadSettingsStr(self, str):
        """
        Loads settings from string str which is compatible with cPickle
        """
        if hasattr(self, "settingsList"):
            settings = cPickle.loads(str)
            self.__dict__.update(settings)

    def saveSettingsStr(self):
        """
        return settings in string format compatible with cPickle
        """
        str = ""
        if hasattr(self, "settingsList"):
            settings = dict([(name, getattr(self, name)) for name in self.settingsList])
            str = cPickle.dumps(settings)
        return str

    # this function is only intended for derived classes to send appropriate signals when all settings are loaded
    def activateLoadedSettings(self):
        pass
        
    def addInput(self,signalName, dataType, handler, onlySingleConnection=TRUE):
        self.inputs.append((signalName, dataType, handler, onlySingleConnection))
            
    def addOutput(self, signalName, dataType):
        self.outputs.append((signalName, dataType))

    def setOptions(self):
        pass

    # ########################################################################
    def connect(self, control, signal, method):
        wrapper = SignalWrapper(self, method)
        self.wrappers.append(wrapper)
        QDialog.connect(control, signal, wrapper)
        #QWidget.connect(control, signal, method)        # ordinary connection useful for dialogs and windows that don't send signals to other widgets

    def findSignalTypeFrom(self, signalName):
        for (signal, dataType) in self.outputs:
            if signal == signalName: return dataType
        return dataType 

    def findSignalTypeTo(self, signalName):
        for (signal, dataType, handler, onlySingleConnection) in self.inputs:
            if signalName == signal: return dataType
        return None

    def addInputConnection(self, widgetFrom, signalName):
        handler = None
        for (signal, dataType, h, onlySingle) in self.inputs:
            if signalName == signal: handler = h
            
        existing = []
        if self.linksIn.has_key(signalName): existing = self.linksIn[signalName]
        self.linksIn[signalName] = existing + [(0, widgetFrom, handler, None)]    # (dirty, handler, signalData)
    

    # return list of signal names, that are single and already connected to other widgets        
    def removeExistingSingleLink(self, signal):
        #(type, handler, single) = self.inputs[signal]
        #if not single: return []
        for (signalName, dataType, handler, onlySingle) in self.inputs:
            if signalName == signal and not onlySingle: return []
            
        widgets = []
        for signalName in self.linksIn.keys():
            if signalName == signal:
                widgets.append(self.linksIn[signalName][0][1])
                del self.linksIn[signalName]
                
        return widgets
        
    # signal manager calls this function when all input signals have updated the data
    def processSignals(self):
        #if self.stackHeight > 0: return  # if this widet is already processing something return
        
        # we define only a way to handle signals that have defined a handler function
        for key in self.linksIn.keys():
            for i in range(len(self.linksIn[key])):
                (dirty, widgetFrom, handler, signalData) = self.linksIn[key][i]
                if handler != None and dirty:
                    #print "processing ", self.name()," , handler = ", str(handler)[13:30]
                    self.linksIn[key][i] = (0, widgetFrom, handler, signalData) # clear the dirty flag
                    handler(signalData)

        self.needProcessing = 0

    # set new data from widget widgetFrom for a signal with name signalName
    def updateNewSignalData(self, widgetFrom, signalName, value):
        if not self.linksIn.has_key(signalName): return
        for i in range(len(self.linksIn[signalName])):
            (dirty, widget, handler, oldValue) = self.linksIn[signalName][i]
            if widget == widgetFrom:
                self.linksIn[signalName][i] = (1, widget, handler, value)
        self.needProcessing = 1

if __name__ == "__main__":  
    a=QApplication(sys.argv)
    oww=OWBaseWidget()
    a.setMainWidget(oww)
    oww.show()
    a.exec_loop()
    oww.saveSettings()
