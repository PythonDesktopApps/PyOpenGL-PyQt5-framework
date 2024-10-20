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
from geometry.rectangle import RectangleGeometry
from extras.text_texture2 import TextTexture
from material.texture import TextureMaterial


class GLWidget(qgl.QGLWidget):

    def __init__(self, main_window=None, *__args):
        # commennt for now, focus first on refactoring the actual code
        # fmt = qgl.QGLFormat()
        # fmt.setVersion(3, 3)
        # fmt.setProfile(qgl.QGLFormat.CoreProfile)
        # fmt.setSampleBuffers(True)
        # super().__init__(fmt, main_window, *__args)
        super().__init__(main_window, *__args)

        self.parent = main_window
        # self.setMinimumSize(800, 800)
        self.setMouseTracking(True)

        self.lastTime = time.time()

    def initializeGL(self):
        # print gl info
        Utils.print_system_info()

        self.gl_settings()

        self.renderer = Renderer(self)
        self.scene = Scene()
        self.camera = Camera(aspect_ratio=800/600)
        self.camera.set_position([0, 0, 1.5])
        geometry = RectangleGeometry()
        message = TextTexture(text="Python Graphics",
                              font_name="arial",
                              font_size=32,
                              text_color=[0, 0, 200],
                              width=256,
                              height=256,
                              h_align="center",
                              v_align="middle",
                              )
        
        material = TextureMaterial(message)
        self.mesh = Mesh(geometry, material)
        self.scene.add(self.mesh)

    def paintGL(self):
        self.clear()
        
        # Time update
        # now = time.time()
        # dt = now - self.lastTime
        # self.lastTime = now

        # self.distort_material.uniform_dict["time"].data += dt
        self.mesh.rotate_y(0.0114)
        self.mesh.rotate_x(0.0237)
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
        timer.setInterval(17)  # period, in milliseconds
        timer.timeout.connect(self.glWidget.update)
        timer.start()

    def setupUi(self):
        pass

    # Qt can access keyboard events only if any of its top level window has keyboard focus.
    # If the window is minimized or another window takes focus, you will not receive keyboard events.
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
