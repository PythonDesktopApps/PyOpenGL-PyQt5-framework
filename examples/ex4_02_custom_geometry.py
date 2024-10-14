import math
import time
import sys
from pathlib import Path

import numpy as np
import PyQt5.QtWidgets as qtw
import PyQt5.QtGui as qtg
import PyQt5.QtCore as qtc
import PyQt5.QtOpenGL as qgl

from PyQt5.uic import loadUi
from PyQt5.QtCore import pyqtSlot

import OpenGL.GL as GL

package_dir = str(Path(__file__).resolve().parents[1])
print("parent dir: ", package_dir)
# Add the package directory into sys.path if necessary
if package_dir not in sys.path:
    sys.path.insert(0, package_dir)

from core.utils import Utils
from core_ext.camera import Camera
from core_ext.mesh import Mesh
from core_ext.renderer import Renderer
from core_ext.scene import Scene
from geometry.geometry import Geometry
from material.surface import SurfaceMaterial

class GLWidget(qgl.QGLWidget):

    def __init__(self, main_window=None, *__args):
        # commennt for now, focus first on refactoring the actual code
        fmt = qgl.QGLFormat()
        fmt.setVersion(3, 3)
        fmt.setProfile(qgl.QGLFormat.CoreProfile)
        fmt.setSampleBuffers(True)
        super().__init__(fmt, main_window, *__args)

        self.parent = main_window
        # self.setMinimumSize(800, 800)
        self.setMouseTracking(True)

    def initializeGL(self):
        # print gl info
        Utils.print_system_info()

        self.gl_settings()

        self.renderer = Renderer(self)
        self.scene = Scene()
        self.camera = Camera(aspect_ratio=800/600)
        self.camera.set_position([0, 0, 0.5])
        geometry = Geometry()
        p0 = [-0.1, 0.1, 0.0]
        p1 = [0.0, 0.0, 0.0]
        p2 = [0.1, 0.1, 0.0]
        p3 = [-0.2, -0.2, 0.0]
        p4 = [0.2, -0.2, 0.0]
        position_data = [p0, p3, p1, p1, p3, p4, p1, p4, p2]
        geometry.add_attribute("vec3", "vertexPosition", position_data)
        R = [1, 0, 0]
        Y = [1, 1, 0]
        G = [0, 0.25, 0]
        color_data = [R, G, Y, Y, G, G, Y, G, R]
        geometry.add_attribute("vec3", "vertexColor", color_data)
        material = SurfaceMaterial(property_dict={"useVertexColors": True})
        self.mesh = Mesh(geometry, material)
        self.scene.add(self.mesh)

    def paintGL(self):
        self.renderer.render(self.scene, self.camera)

    def gl_settings(self):
        # self.qglClearColor(qtg.QColor(255, 255, 255))
        GL.glClearColor(255, 255, 255, 1)
        GL.glEnable(GL.GL_DEPTH_TEST)
        GL.glDepthFunc(GL.GL_LESS)
        # the shapes are basically behind the white background
        # if you enabled face culling, they will not show
        # GL.glEnable(GL.GL_CULL_FACE)

    def clear(self):
        # color it white for better visibility
        GL.glClearColor(255, 255, 255, 1)
        GL.glClear(GL.GL_COLOR_BUFFER_BIT | GL.GL_DEPTH_BUFFER_BIT)

class MainWindow(qtw.QMainWindow):

    def __init__(self, *args):
        super().__init__(*args)
        self.scaling = self.devicePixelRatioF()

        loadUi("examples/Tsugite.ui", self)
        self.setupUi()

        self.title = "PyOpenGL Framework"
        self.setWindowTitle(self.title)
        self.setWindowIcon(qtg.QIcon("resources/tsugite_icon.png"))

        self.glWidget = GLWidget(self)

        self.hly_gl.addWidget(self.glWidget)

        self.statusBar = qtw.QStatusBar()
        self.setStatusBar(self.statusBar)
        self.statusBar.showMessage(
            "To open and close the joint: PRESS 'Open/close joint' button or DOUBLE-CLICK anywhere inside the window.")

        # since we dont have events to trigger updateGL
        # we can use time interval to do it
        timer = qtc.QTimer(self)
        timer.setInterval(10)  # period, in milliseconds
        timer.timeout.connect(self.glWidget.updateGL)
        timer.start()

    def setupUi(self):
        pass
        # get opengl window size - not really needed
        # self.x_range = [10, 500]
        # self.y_range = [10, 500]

        # note that the widgets are made attribute to be reused again
        # ---Design
        # self.btn_open_close_joint = self.findChild(qtw.QPushButton, "btn_open_close_joint")

    
    def keyPressEvent(self, e):
        pass
    
# deal with dpi
qtw.QApplication.setAttribute(qtc.Qt.AA_EnableHighDpiScaling, True)     # enable high dpi scaling
qtw.QApplication.setAttribute(qtc.Qt.AA_UseHighDpiPixmaps, True)        # use high dpi icons

app = qtw.QApplication(sys.argv)

# basically
window = MainWindow()
window.show()

# this starts the loop
sys.exit(app.exec_())