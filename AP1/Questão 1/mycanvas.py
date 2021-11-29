from PyQt5 import QtOpenGL
from PyQt5.QtWidgets import *
from PyQt5 import QtCore
from OpenGL.GL import *
from hetool import HeController, HeModel, HeView, Tesselation
from mymodel import MyPoint

class MyCanvas(QtOpenGL.QGLWidget):
    def __init__(self):
        super(MyCanvas, self).__init__()
        self.m_model = None
        self.m_w = 0 # width: GL canvas horizontal size
        self.m_h = 0 # height: GL canvas vertical size
        self.m_L = -1000.0
        self.m_R = 1000.0
        self.m_B = -1000.0
        self.m_T = 1000.0
        self.list = None
        self.m_buttonPressed = False
        self.m_pt0 = QtCore.QPoint(0.0,0.0)
        self.m_pt1 = QtCore.QPoint(0.0,0.0)
        
        self.tol = 0.1
        self.hemodel = HeModel()
        self.heview = HeView(self.hemodel)
        self.hecontroller = HeController(self.hemodel)

    def initializeGL(self):
        glClear(GL_COLOR_BUFFER_BIT)
        glEnable(GL_LINE_SMOOTH)
        self.list = glGenLists(1)
        
    def setModel(self,_model):
        self.m_model = _model
        
    def fitWorldToViewport(self):
        print("fitWorldToViewport")
        if self.m_model == None:
            return
        self.m_L,self.m_R,self.m_B,self.m_T=self.heview.getBoundBox()
        self.scaleWorldWindow(1.10)
        self.update()
    
    def generateGrid(self, xTam, yTam):
        interval_x = self.m_w / xTam
        interval_y = self.m_h / yTam
        grid_points = []
        i = j = 0
        while i < self.m_w:
            while j < self.m_h:
                grid_points.append(self.convertPtCoordsToUniverse(QtCore.QPoint(i,j)))
                j += interval_y
            i += interval_x
            j = 0

        for point in grid_points:
            for pat in self.heview.getPatches():
                pt = MyPoint(point.x(),point.y())
                if pat.isPointInside(pt):
                    self.m_model.addPoint(point, pat)

        self.update()
        self.paintGL()
        
    
    def scaleWorldWindow(self,_scaleFac):
        # Compute canvas viewport distortion ratio.
        vpr = self.m_h / self.m_w
        
        # Get current window center.
        cx = (self.m_L + self.m_R) / 2.0
        cy = (self.m_B + self.m_T) / 2.0
        
        # Set new window sizes based on scaling factor.
        sizex = (self.m_R - self.m_L) * _scaleFac
        sizey = (self.m_T - self.m_B) * _scaleFac
        
        # Adjust window to keep the same aspect ratio of the viewport.
        if sizey > (vpr*sizex):
            sizex = sizey / vpr
        else:
            sizey = sizex * vpr
        
        self.m_L = cx - (sizex * 0.5)
        self.m_R = cx + (sizex * 0.5)
        self.m_B = cy - (sizey * 0.5)
        self.m_T = cy + (sizey * 0.5)
        
        # Establish the clipping volume by setting up an orthographic projection
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        glOrtho(self.m_L, self.m_R, self.m_B, self.m_T, -1.0, 1.0)
        
    def panWorldWindow(self, _panFacX, _panFacY):
        # Compute pan distances in horizontal and vertical directions.
        panX = (self.m_R - self.m_L) * _panFacX
        panY = (self.m_T - self.m_B) * _panFacY
        
        # Shift current window.
        self.m_L += panX
        self.m_R += panX
        self.m_B += panY
        self.m_T += panY
        
        # Establish the clipping volume by setting up an
        # orthographic projection
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        glOrtho(self.m_L, self.m_R, self.m_B, self.m_T, -1.0, 1.0)    
    
    def convertPtCoordsToUniverse(self, _pt):
        if self.m_w == 0 or self.m_h == 0:
            return

        dX = self.m_R - self.m_L
        dY = self.m_T - self.m_B
        mX = _pt.x() * dX / self.m_w
        mY = (self.m_h - _pt.y()) * dY / self.m_h
        x = self.m_L + mX
        y = self.m_B + mY
        return QtCore.QPointF(x,y)

    def resizeGL(self, _width, _height):
        self.m_w = _width
        self.m_h = _height
        glViewport(0, 0, self.m_w, self.m_h)
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        glOrtho(self.m_L,self.m_R,self.m_B,self.m_T,-1.0,1.0)
        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()
    
    def mousePressEvent(self, event):
        self.m_buttonPressed = True
        self.m_pt0 = event.pos()
    
    def mouseMoveEvent(self, event):
        if self.m_buttonPressed:
            self.m_pt1 = event.pos()
            self.update()
    
    def mouseReleaseEvent(self, event):
        pt0_U = self.convertPtCoordsToUniverse(self.m_pt0)
        pt1_U = self.convertPtCoordsToUniverse(self.m_pt1)

        snapped, x1, y1 = self.heview.snapToSegment(pt0_U.x(),pt0_U.y(), 1)
        snapped2, x2, y2 = self.heview.snapToSegment(pt1_U.x(),pt1_U.y(), 1)
        print(snapped, snapped2) #Dúvida: Sempre retorna False

        self.hecontroller.insertSegment([x1, y1, x2, y2], self.tol)
        self.m_buttonPressed = False
        self.m_pt0.setX(0.0)
        self.m_pt0.setY(0.0)
        self.m_pt1.setX(0.0)
        self.m_pt1.setY(0.0)
        self.update()
        self.paintGL()
    
    def paintGL(self):
        glClear(GL_COLOR_BUFFER_BIT)
        glCallList(self.list)
        glDeleteLists(self.list, 1)
        self.list = glGenLists(1)
        glNewList(self.list, GL_COMPILE)
        
        # desenho dos pontos coletados
        pt0_U = self.convertPtCoordsToUniverse(self.m_pt0)
        pt1_U = self.convertPtCoordsToUniverse(self.m_pt1)
        if(pt0_U and pt1_U):
            glColor3f(1.0, 0.0, 0.0)
            glBegin(GL_LINE_STRIP)
            glVertex2f(pt0_U.x(), pt0_U.y())
            glVertex2f(pt1_U.x(), pt1_U.y())
            glEnd()
            
        if not(self.heview.isEmpty()):
            patches = self.heview.getPatches() # retalhos, regioes construídas automaticamente
            glColor3f(3.0, 0.0, 1.0)
            for pat in patches:
                triangs = Tesselation.tessellate(pat.getPoints())
                for triang in triangs:
                    glBegin(GL_TRIANGLES)
                    for pt in triang:
                        glVertex2d(pt.getX(), pt.getY())
                    glEnd()

            segments = self.heview.getSegments()
            glColor3f(0.0, 1.0, 1.0)
            for curv in segments:
                ptc = curv.getPointsToDraw()
                glBegin(GL_LINES)

                glVertex2f(ptc[0].getX(), ptc[0].getY())
                glVertex2f(ptc[1].getX(), ptc[1].getY())
                
                glEnd()
                
            verts = self.heview.getPoints()
            glColor3f(1.0, 0.0, 0.0)
            glPointSize(5)
            glBegin(GL_POINTS)
            for vert in verts:
                glVertex2f(vert.getX(), vert.getY())
            glEnd()


        if len(self.m_model.getPoints()) > 0:
            glColor3f(1.0, 1.0, 0.0)
            glPointSize(3)
            glBegin(GL_POINTS)
            for pt in self.m_model.getPoints():
                glVertex2f(pt['x'], pt['y'])
            glEnd()
                
        glEndList()