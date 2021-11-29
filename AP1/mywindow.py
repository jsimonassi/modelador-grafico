from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from mycanvas import *
from mymodel import *


class MyWindow(QMainWindow):
    def __init__(self):
        super(MyWindow, self).__init__()
        self.setGeometry(100, 100, 600, 400)
        self.setWindowTitle("AP1")
        self.canvas = MyCanvas()
        self.setCentralWidget(self.canvas)
        # create a model object and pass to canvas
        self.model = MyModel()
        self.canvas.setModel(self.model)
        # create a Toolbar
        tb = self.addToolBar("File")

        fit = QAction("Fit", self)
        tb.addAction(fit)

        grid = QAction("Gerar Malha", self)
        tb.addAction(grid)

        export_json = QAction("Exportar JSON", self)
        tb.addAction(export_json)

        tb.actionTriggered[QAction].connect(self.tbpressed)

    def tbpressed(self, a):
        if a.text() == "Fit":
            self.canvas.fitWorldToViewport()
        elif a.text() == "Gerar Malha":
            self.generateGridDialog()
        elif a.text() == "Exportar JSON":
            if self.model.export_json():
                QMessageBox.about(self, "Sucesso", "O arquivo data.json foi salvo na raiz do projeto")

    def generateGridDialog(self):
        dlg = QDialog()
        dlg.setGeometry(100, 100, 200, 150)
        
        label1 = QLabel("Horizontal: ",dlg)
        label2 = QLabel("Vertical: ",dlg)
        label1.move(30,30)
        label2.move(30,70)

        inputX = QLineEdit(dlg)
        inputY = QLineEdit(dlg)
        inputX.move(110, 30)
        inputX.resize(50,20)
        inputY.move(110, 70)
        inputY.resize(50,20)
        inputX.setValidator(QIntValidator(0, 100))
        inputY.setValidator(QIntValidator(0, 100))

        b1 = QPushButton("ok",dlg)
        b1.move(75,100)
        b1.clicked.connect(lambda: self.generateGrid(inputX.text(),inputY.text(), dlg))

        dlg.setWindowTitle("Gerar Malha")
        dlg.exec_()

    def generateGrid(self,x,y, dlg):
        if(x == "" or y == ""):
            QMessageBox.about(self, "Erro", "Valores Invalidos")
            return
        dlg.close()
        self.canvas.generateGrid(int(x), int(y))