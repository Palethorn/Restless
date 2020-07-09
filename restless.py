import sys
from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QPushButton, QMainWindow, QLineEdit, QGridLayout, QComboBox, QPlainTextEdit, QHBoxLayout
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import pyqtSlot
import requests
import yaml
import json

class RemoveHeaderButton(QPushButton):
    def __init__(self, grid, widget, slot, header_slots):
        super().__init__()
        self.grid = grid
        self.widget = widget
        self.slot = slot
        self.header_slots = header_slots
        self.clicked.connect(self.handle)


    def handle(self):
        self.grid.removeWidget(self.widget)
        del self.header_slots[self.slot]


class MainWindow(QMainWindow):

    def __init__(self):
        super().__init__()
        self.root = QWidget()
        self.setCentralWidget(self.root)

        self.header_slots = {}

        self.headersWidget = QWidget()
        self.headersGrid = QGridLayout()
        self.headersWidget.setLayout(self.headersGrid)

        grid = QGridLayout()

        self.methods = QComboBox()
        self.methods.addItem("GET", "GET")
        self.methods.addItem("POST", "POST")
        self.methods.addItem("PUT", "PUT")
        self.methods.addItem("DELETE", "DELETE")
        self.methods.addItem("PATCH", "PATCH")
        self.methods.addItem("HEAD", "HEAD")

        self.urlField = QLineEdit()

        addHeader = QPushButton()
        addHeader.setText('Add Header')
        addHeader.clicked.connect(self.add_header)

        go = QPushButton()
        go.setText("Go")
        go.clicked.connect(self.go_clicked)

        self.requestBody = QPlainTextEdit()
        self.responseText = QPlainTextEdit()
        self.responseText.setReadOnly(True)

        grid.addWidget(self.methods, 0, 0)
        grid.addWidget(self.urlField, 0, 1)
        grid.addWidget(self.headersWidget, 1, 0, 1, 2)
        grid.addWidget(addHeader, 2, 0)
        grid.addWidget(self.requestBody, 3, 0)
        grid.addWidget(self.responseText, 3, 1)
        grid.addWidget(go, 4, 0)
        
        self.root.setLayout(grid)
        self.setWindowTitle("Restless")
        self.setMinimumSize(500, 500)
        self.read_snapshot()
        self.show()


    def read_snapshot(self):
        if len(sys.argv) > 1:
            with open(sys.argv[1], 'r') as file:
                snapshot = yaml.load(file)
                file.close()
                self.urlField.setText(snapshot['url'])
                self.requestBody.insertPlainText(snapshot['data'])
                index = self.methods.findData(snapshot['method'])
                print(index, snapshot['method'])
                self.methods.setCurrentIndex(index)

                for header in snapshot['headers']:
                    self.add_header(header, snapshot['headers'][header])


    def go_clicked(self):
        self.responseText.clear()
        method = self.methods.currentText()
        headers = {}
        responseHeaders = ''

        for key in self.header_slots:
            widget = self.header_slots[key]
            headers[widget.layout().itemAt(0).widget().text()] = widget.layout().itemAt(1).widget().text()
        
        print(headers)

        if method == 'GET':
            response = requests.get(self.urlField.text(), headers=headers)
    
        if method == 'POST':
            requestBody = self.requestBody.toPlainText()
            response = requests.post(self.urlField.text(), headers=headers, data=requestBody)

        if method == 'PUT':
            requestBody = self.requestBody.toPlainText()
            response = requests.put(self.urlField.text(), headers=headers, data=requestBody)

        if method == 'DELETE':
            response = requests.delete(self.urlField.text(), headers=headers)

        if method == 'PATCH':
            requestBody = self.requestBody.toPlainText()
            response = requests.patch(self.urlField.text(), headers=headers, data=requestBody)

        if method == 'HEAD':
            response = requests.head(self.urlField.text(), headers=headers)

        for header in response.headers:
            responseHeaders = responseHeaders + header + ': ' + response.headers[header] + "\r\n"

        response_text = response.text

        if response.headers['Content-Type'] == 'application/json':
            json_object = json.loads(response.text)
            response_text = json.dumps(json_object, indent=4, sort_keys=True)

        self.responseText.insertPlainText(responseHeaders + "\r\n" + response_text)


    def add_header(self, vname = '', vvalue = ''):
        widget = QWidget()
        layout = QHBoxLayout()
        widget.setLayout(layout)
        header_slot = len(self.header_slots)

        name = QLineEdit()

        if(vname):
            name.setText(vname)

        value = QLineEdit()

        if vvalue:
            value.setText(vvalue)

        remove = RemoveHeaderButton(self.headersGrid, widget, header_slot, self.header_slots)
        remove.setText('Remove')

        layout.addWidget(name)
        layout.addWidget(value)
        layout.addWidget(remove)

        self.headersGrid.addWidget(widget)
        self.header_slots[header_slot] = widget
        self.headersWidget.adjustSize()
        self.root.adjustSize()
        

if __name__ == '__main__':
    app = QApplication(sys.argv)
    win = MainWindow()
    sys.exit(app.exec_())
