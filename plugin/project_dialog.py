import os
from qgis.PyQt.QtWidgets import QWidget, QCheckBox, QComboBox, QTableWidget, QTableWidgetItem, QHBoxLayout
from qgis.PyQt import uic
from qgis.PyQt.QtCore import Qt
from qgis.core import QgsProject

class ProjectWidget(QWidget):
    def __init__(self, item, backgrounds, parent=None):
        super(ProjectWidget, self).__init__(parent)
        uic.loadUi(os.path.join(os.path.dirname(__file__), "project_dialog.ui"), self)
        self.__item = item
        if 'scales' in item:
            self.scaleLineEdit.setText(str([int(s) for s in item['scales']])[1:-1])

        currentProject = QgsProject.instance().baseName()
        currentItem = item['url'].split("/")[-1]

        defaultBackgroundIdx = None
        self.backgroundComboBox.addItem("")
        for i, layer in enumerate(backgrounds):
            self.backgroundTable.insertRow(i)
            cbWidget = QWidget()
            bgCheckBox = QCheckBox()
            printLayerText = ''
            for l in item['backgroundLayers']:
                if (l['name']==layer['name']):
                    bgCheckBox.setChecked(True)
                    printLayerText = l.get('printLayer', '')
                    if l.get('visibility', '') == 1:
                        defaultBackgroundIdx = i + 1
                    break

            cbLayout = QHBoxLayout()
            cbLayout.addWidget(bgCheckBox)
            cbLayout.setAlignment(Qt.AlignCenter)
            cbLayout.setContentsMargins(0,0,0,0)
            cbWidget.setLayout(cbLayout)
            self.backgroundTable.setCellWidget(i, 0, cbWidget)

            backgroundItem = QTableWidgetItem(layer['name'])
            backgroundItem.setTextAlignment(Qt.AlignCenter)
            backgroundItem.setFlags(Qt.ItemIsEnabled)
            self.backgroundTable.setItem(i, 1, backgroundItem)

            if currentProject == currentItem:
                printLayers = [''] + [l.name() for l in QgsProject.instance().mapLayers().values()]
                printLayersComboBox = QComboBox()
                printLayersComboBox.addItems(printLayers)
                if printLayerText != '':
                    for j in range(printLayersComboBox.count()):
                        if printLayerText == printLayersComboBox.itemText(j):
                            printLayersComboBox.setCurrentIndex(j)
                            break
                self.backgroundTable.setCellWidget(i, 2, printLayersComboBox)
            else:
                printLayerItem = QTableWidgetItem(printLayerText)
                printLayerItem.setTextAlignment(Qt.AlignCenter)
                self.backgroundTable.setItem(i, 2, printLayerItem)

            self.backgroundComboBox.addItem(layer['name'])

        if defaultBackgroundIdx is not None:
            self.backgroundComboBox.setCurrentIndex(defaultBackgroundIdx)

        if 'coordinates' in item['searchProviders']:
            self.coordinatesCheckBox.setChecked(True)
        if 'nominatim' in item['searchProviders']:
            self.nominatimCheckBox.setChecked(True)

    def item(self):
        if self.scaleLineEdit.text() != '':
            self.__item['scales'].clear()
            for s in self.scaleLineEdit.text().split(', '):
                self.__item['scales'].append(int(s))
        backgrounds = []
        for i in range(self.backgroundTable.rowCount()):
            if self.backgroundTable.cellWidget(i, 0).findChild(QCheckBox).isChecked():
                bg = {}
                bg["name"] = self.backgroundTable.item(i, 1).text()
                bg["visibility"] = self.backgroundComboBox.currentText() == bg["name"]
                if isinstance(self.backgroundTable.cellWidget(i, 2), QComboBox):
                    bg["printLayer"] = self.backgroundTable.cellWidget(i, 2).currentText()
                elif self.backgroundTable.item(i, 2) != '':
                    bg["printLayer"] = self.backgroundTable.item(i, 2).text()
                backgrounds.append(bg)

        self.__item['backgroundLayers'] = backgrounds
            
        self.__item["searchProviders"] = []
        if self.coordinatesCheckBox.isChecked() == True:
            self.__item["searchProviders"].append("coordinates")
        if self.nominatimCheckBox.isChecked() == True:
            self.__item["searchProviders"].append("nominatim")

        return self.__item