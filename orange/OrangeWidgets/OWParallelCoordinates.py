"""
<name>Parallel coordinates</name>
<description>Shows data using parallel coordianates visualization method</description>
<category>Classification</category>
<icon>icons/ParallelCoordinates.png</icon>
<priority>3110</priority>
"""
# ParallelCoordinates.py
#
# Show data using parallel coordinates visualization method
# 

from OWWidget import *
from OWParallelCoordinatesOptions import *
from random import betavariate 
from OWParallelGraph import *
from OData import *
import OWVisAttrSelection 

    

###########################################################################################
##### WIDGET : Parallel coordinates visualization
###########################################################################################
class OWParallelCoordinates(OWWidget):
    settingsList = ["attrContOrder", "attrDiscOrder", "jitteringType", "GraphCanvasColor", "jitterSize", "showDistributions", "showAttrValues", "hidePureExamples", "showCorrelations", "globalValueScaling", "linesDistance"]
    spreadType=["none","uniform","triangle","beta"]
    attributeContOrder = ["None","RelieF","Correlation"]
    attributeDiscOrder = ["None","RelieF","GainRatio","Gini", "Oblivious decision graphs"]
    jitterSizeList = ['2','5','10', '15', '20', '30']
    jitterSizeNums = [2,  5,  10, 15, 20, 30]
    linesDistanceList = ['20', '30', '40', '50', '60', '70', '80', '100']
    linesDistanceNums = [20, 30, 40, 50, 60, 70, 80, 100]
    
    def __init__(self,parent=None):
        
        
        OWWidget.__init__(self, parent, "Parallel Coordinates", "Show data using parallel coordinates visualization method", TRUE, TRUE)

        #set default settings
        self.attrDiscOrder = "RelieF"
        self.attrContOrder = "RelieF"
        
        self.jitteringType = "uniform"
        self.GraphCanvasColor = str(Qt.white.name())
        self.showDistributions = 1
        self.showAttrValues = 1
        self.hidePureExamples = 1
        self.showCorrelations = 1
        self.GraphGridColor = str(Qt.black.name())
        self.data = None
        self.jitterSize = 10
        self.linesDistance = 40
        self.ShowVerticalGridlines = TRUE
        self.ShowHorizontalGridlines = TRUE
        self.globalValueScaling = 0

        #load settings
        self.loadSettings()

        # add a settings dialog and initialize its values
        self.options = OWParallelCoordinatesOptions()        

        #GUI
        #add a graph widget
        self.box = QVBoxLayout(self.mainArea)
        self.graph = OWParallelGraph(self.mainArea)
        self.slider = QSlider(QSlider.Horizontal, self.mainArea)
        self.sliderRange = 0
        self.slider.setRange(0, 0)
        self.slider.setTickmarks(QSlider.Below)
        self.isResizing = 0 
        self.box.addWidget(self.graph)
        self.box.addWidget(self.slider)
        self.connect(self.graphButton, SIGNAL("clicked()"), self.graph.saveToFile)

        # graph main tmp variables
        self.addInput("cdata")
        self.addInput("selection")

        #connect settingsbutton to show options
        self.connect(self.settingsButton, SIGNAL("clicked()"), self.options.show)
        self.connect(self.options.spreadButtons, SIGNAL("clicked(int)"), self.setSpreadType)

        self.connect(self.options.showDistributions, SIGNAL("toggled(bool)"), self.setDistributions)
        self.connect(self.options.showAttrValues, SIGNAL("toggled(bool)"), self.setAttrValues)
        self.connect(self.options.hidePureExamples, SIGNAL("toggled(bool)"), self.setHidePureExamples)
        self.connect(self.options.showCorrelations, SIGNAL("toggled(bool)"), self.setShowCorrelations)
        self.connect(self.options.globalValueScaling, SIGNAL("toggled(bool)"), self.setGlobalValueScaling)
        self.connect(self.options.jitterSize, SIGNAL("activated(int)"), self.setJitteringSize)
        self.connect(self.options.linesDistance, SIGNAL("activated(int)"), self.setLinesDistance)
        self.connect(self.options.attrContButtons, SIGNAL("clicked(int)"), self.setAttrContOrderType)
        self.connect(self.options.attrDiscButtons, SIGNAL("clicked(int)"), self.setAttrDiscOrderType)
        self.connect(self.options, PYSIGNAL("canvasColorChange(QColor &)"), self.setCanvasColor)

        #add controls to self.controlArea widget
        self.selClass = QVGroupBox(self.controlArea)
        self.shownAttribsGroup = QVGroupBox(self.space)
        self.addRemoveGroup = QHButtonGroup(self.space)
        self.hiddenAttribsGroup = QVGroupBox(self.space)
        self.selClass.setTitle("Class attribute")
        self.shownAttribsGroup.setTitle("Shown attributes")
        self.hiddenAttribsGroup.setTitle("Hidden attributes")

        self.classCombo = QComboBox(self.selClass)
        self.showContinuousCB = QCheckBox('show continuous', self.selClass)
        self.connect(self.showContinuousCB, SIGNAL("clicked()"), self.setClassCombo)

        self.shownAttribsLB = QListBox(self.shownAttribsGroup)
        self.shownAttribsLB.setSelectionMode(QListBox.Extended)

        self.hiddenAttribsLB = QListBox(self.hiddenAttribsGroup)
        self.hiddenAttribsLB.setSelectionMode(QListBox.Extended)
        
        self.attrButtonGroup = QHButtonGroup(self.shownAttribsGroup)
        #self.attrButtonGroup.setFrameStyle(QFrame.NoFrame)
        #self.attrButtonGroup.setMargin(0)
        self.buttonUPAttr = QPushButton("Attr UP", self.attrButtonGroup)
        self.buttonDOWNAttr = QPushButton("Attr DOWN", self.attrButtonGroup)

        self.attrAddButton = QPushButton("Add attr.", self.addRemoveGroup)
        self.attrRemoveButton = QPushButton("Remove attr.", self.addRemoveGroup)

        #connect controls to appropriate functions
        self.connect(self.classCombo, SIGNAL('activated ( const QString & )'), self.updateGraph)

        self.connect(self.buttonUPAttr, SIGNAL("clicked()"), self.moveAttrUP)
        self.connect(self.buttonDOWNAttr, SIGNAL("clicked()"), self.moveAttrDOWN)

        self.connect(self.attrAddButton, SIGNAL("clicked()"), self.addAttribute)
        self.connect(self.attrRemoveButton, SIGNAL("clicked()"), self.removeAttribute)

        self.connect(self.slider, SIGNAL("valueChanged(int)"), self.sliderValueChanged)

        # add a settings dialog and initialize its values
        self.activateLoadedSettings()

        #self.repaint()

    def resizeEvent(self, e):
        self.isResizing = 1
        self.updateGraph()

    def sliderValueChanged(self, val):
        self.updateGraph()

    # #########################
    # OPTIONS
    # #########################
    def activateLoadedSettings(self):
        self.options.spreadButtons.setButton(self.spreadType.index(self.jitteringType))
        self.options.attrContButtons.setButton(self.attributeContOrder.index(self.attrContOrder))
        self.options.attrDiscButtons.setButton(self.attributeDiscOrder.index(self.attrDiscOrder))
        self.options.gSetCanvasColor.setNamedColor(str(self.GraphCanvasColor))
        self.options.showDistributions.setChecked(self.showDistributions)
        self.options.showAttrValues.setChecked(self.showAttrValues)
        self.options.hidePureExamples.setChecked(self.hidePureExamples)
        self.options.showCorrelations.setChecked(self.showCorrelations)
        self.options.globalValueScaling.setChecked(self.globalValueScaling)
        for i in range(len(self.jitterSizeList)):
            self.options.jitterSize.insertItem(self.jitterSizeList[i])
        self.options.jitterSize.setCurrentItem(self.jitterSizeNums.index(self.jitterSize))
        for i in range(len(self.linesDistanceList)):
            self.options.linesDistance.insertItem(self.linesDistanceList[i])
        self.options.linesDistance.setCurrentItem(self.linesDistanceNums.index(self.linesDistance))
        
        self.graph.setJitteringOption(self.jitteringType)
        self.graph.setShowDistributions(self.showDistributions)
        self.graph.setShowAttrValues(self.showAttrValues)
        self.graph.setCanvasColor(self.options.gSetCanvasColor)
        self.graph.setGlobalValueScaling(self.globalValueScaling)
        self.graph.setJitterSize(self.jitterSize)

    # jittering options
    def setSpreadType(self, n):
        self.jitteringType = self.spreadType[n]
        self.graph.setJitteringOption(self.spreadType[n])
        self.graph.setData(self.data)
        self.updateGraph()

    # minimum lines distance
    def setLinesDistance(self, n):
        self.linesDistance = self.linesDistanceNums[n]
        self.updateGraph()

    # jittering options
    def setJitteringSize(self, n):
        self.jitterSize = self.jitterSizeNums[n]
        self.graph.setJitterSize(self.jitterSize)
        self.graph.setData(self.data)
        self.updateGraph()

    def setDistributions(self, b):
        self.showDistributions = b
        self.graph.setShowDistributions(b)
        self.updateGraph()

    def setAttrValues(self, b):
        self.showAttrValues = b
        self.graph.setShowAttrValues(b)
        self.updateGraph()

    def setHidePureExamples(self, b):
        self.hidePureExamples = b
        self.graph.setHidePureExamples(b)
        self.updateGraph()
        
    def setShowCorrelations(self, b):
        self.showCorrelations = b
        self.graph.setShowCorrelations(b)
        self.updateGraph()

    def setGlobalValueScaling(self):
        self.globalValueScaling = self.options.globalValueScaling.isChecked()
        self.graph.setGlobalValueScaling(self.globalValueScaling)
        self.graph.setData(self.data)
        if self.globalValueScaling == 1:
            self.graph.rescaleAttributesGlobaly(self.data, self.getShownAttributeList())
        self.updateGraph()

    # continuous attribute ordering
    def setAttrContOrderType(self, n):
        self.attrContOrder = self.attributeContOrder[n]
        if self.data != None:
            self.setShownAttributeList(self.data)
        self.updateGraph()

    # discrete attribute ordering
    def setAttrDiscOrderType(self, n):
        self.attrDiscOrder = self.attributeDiscOrder[n]
        if self.data != None:
            self.setShownAttributeList(self.data)
        self.updateGraph()

        
    def setCanvasColor(self, c):
        self.GraphCanvasColor = c
        self.graph.setCanvasColor(c)
        
    # ####################
    # LIST BOX FUNCTIONS
    # ####################

    # move selected attribute in "Attribute Order" list one place up
    def moveAttrUP(self):
        for i in range(self.shownAttribsLB.count()):
            if self.shownAttribsLB.isSelected(i) and i != 0:
                text = self.shownAttribsLB.text(i)
                self.shownAttribsLB.removeItem(i)
                self.shownAttribsLB.insertItem(text, i-1)
                self.shownAttribsLB.setSelected(i-1, TRUE)
        self.updateGraph()

    # move selected attribute in "Attribute Order" list one place down  
    def moveAttrDOWN(self):
        count = self.shownAttribsLB.count()
        for i in range(count-2,-1,-1):
            if self.shownAttribsLB.isSelected(i):
                text = self.shownAttribsLB.text(i)
                self.shownAttribsLB.removeItem(i)
                self.shownAttribsLB.insertItem(text, i+1)
                self.shownAttribsLB.setSelected(i+1, TRUE)
        self.updateGraph()

    def addAttribute(self):
        count = self.hiddenAttribsLB.count()
        pos   = self.shownAttribsLB.count()
        for i in range(count-1, -1, -1):
            if self.hiddenAttribsLB.isSelected(i):
                text = self.hiddenAttribsLB.text(i)
                self.hiddenAttribsLB.removeItem(i)
                self.shownAttribsLB.insertItem(text, pos)
        if self.globalValueScaling == 1:
            self.graph.rescaleAttributesGlobaly(self.data, self.getShownAttributeList())
        self.updateGraph()
        self.graph.replot()

    def removeAttribute(self):
        count = self.shownAttribsLB.count()
        pos   = self.hiddenAttribsLB.count()
        for i in range(count-1, -1, -1):
            if self.shownAttribsLB.isSelected(i):
                text = self.shownAttribsLB.text(i)
                self.shownAttribsLB.removeItem(i)
                self.hiddenAttribsLB.insertItem(text, pos)
        if self.globalValueScaling == 1:
            self.graph.rescaleAttributesGlobaly(self.data, self.getShownAttributeList())
        self.updateGraph()
        self.graph.replot()

    # #####################

    def updateGraph(self):
        graphWidth = self.width()-230
        attrs = self.getShownAttributeList()
        maxAttrs = graphWidth / self.linesDistance
        if len(attrs) > maxAttrs:
            rest = len(attrs) - maxAttrs
            if self.sliderRange != rest:
                #print rest
                self.slider.setRange(0, rest)
                self.sliderRange = rest
            elif self.isResizing:
                self.isResizing = 0
                return  # if we resized widget and it doesn't change the number of attributes that are shown then we return
        else:
            #print "returned"
            self.slider.setRange(0,0)
            self.sliderRange = 0
            maxAttrs = len(attrs)

        start = min(self.slider.value(), len(attrs)-maxAttrs)
        self.graph.updateData(attrs[start:start+maxAttrs], str(self.classCombo.currentText()))
        self.slider.repaint()
        self.graph.update()
        self.repaint()

    # set combo box values with attributes that can be used for coloring the data
    def setClassCombo(self):
        exText = str(self.classCombo.currentText())
        self.classCombo.clear()
        if self.data == None:
            return

        # add possible class attributes
        self.classCombo.insertItem('(One color)')
        for i in range(len(self.data.domain)):
            attr = self.data.domain[i]
            if attr.varType == orange.VarTypes.Discrete or self.showContinuousCB.isOn() == 1:
                self.classCombo.insertItem(attr.name)

        for i in range(self.classCombo.count()):
            if str(self.classCombo.text(i)) == exText:
                self.classCombo.setCurrentItem(i)
                return

        for i in range(self.classCombo.count()):
            if str(self.classCombo.text(i)) == self.data.domain.classVar.name:
                self.classCombo.setCurrentItem(i)
                return


    # ###### SHOWN ATTRIBUTE LIST ##############
    # set attribute list
    def setShownAttributeList(self, data):
        self.shownAttribsLB.clear()
        self.hiddenAttribsLB.clear()

        if data == None: return
        
        shown, hidden = OWVisAttrSelection.selectAttributes(data, self.attrContOrder, self.attrDiscOrder)
        if data.domain.classVar.name not in shown and data.domain.classVar.name not in hidden:
            self.shownAttribsLB.insertItem(data.domain.classVar.name)
        for attr in shown:
            self.shownAttribsLB.insertItem(attr)
        for attr in hidden:
            self.hiddenAttribsLB.insertItem(attr)
        
        
    def getShownAttributeList (self):
        list = []
        for i in range(self.shownAttribsLB.count()):
            list.append(str(self.shownAttribsLB.text(i)))
        return list
    ##############################################
    
    
    ####### CDATA ################################
    # receive new data and update all fields
    def cdata(self, data):
        #self.data = orange.Preprocessor_dropMissing(data.data)
        self.data = data.data
        self.graph.setData(self.data)
        self.shownAttribsLB.clear()
        self.hiddenAttribsLB.clear()
        self.setClassCombo()

        if self.data == None:
            self.repaint()
            return
        
        self.setShownAttributeList(self.data)
        self.updateGraph()
    #################################################

    
    ####### SELECTION ################################
    # receive a list of attributes we wish to show
    def selection(self, list):
        self.shownAttribsLB.clear()
        self.hiddenAttribsLB.clear()

        if self.data == None: return

        if self.data.domain.classVar.name not in list:
            self.shownAttribsLB.insertItem(self.data.domain.classVar.name)

        for attr in list:
            self.shownAttribsLB.insertItem(attr)

        for attr in self.data.domain:
            if attr.name not in list and attr.name != self.data.domain.classVar.name:
                self.hiddenAttribsLB.insertItem(attr.name)
            
        self.updateGraph()
    #################################################
       

#test widget appearance
if __name__=="__main__":
    a=QApplication(sys.argv)
    ow=OWParallelCoordinates()
    a.setMainWidget(ow)
    ow.show()
    a.exec_loop()

    #save settings 
    ow.saveSettings()
