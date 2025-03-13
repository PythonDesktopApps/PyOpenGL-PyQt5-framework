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
from geometry.box import BoxGeometry
from extras.axes import AxesHelper
from extras.grid import GridHelper
from material.surface import SurfaceMaterial
from extras.movement_rig import MovementRig


class GLWidget(qgl.QGLWidget):

    def __init__(self, main_window=None, *__args):
        fmt = Utils.get_gl_format()

        if fmt:
            super().__init__(fmt, main_window, *__args)
        else:
            super().__init__(main_window, *__args)

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
        self.camera.set_position([0, 1, 5])
        geometry = BoxGeometry()
        material = SurfaceMaterial(property_dict={"useVertexColors": True})
        self.mesh = Mesh(geometry, material)
        self.rig = MovementRig()
        self.rig.add(self.mesh)
        self.rig.set_position([0, 0.5, 0])
        self.scene.add(self.rig)
        axes = AxesHelper(axis_length=2)
        self.scene.add(axes)
        grid = GridHelper(
            size=20,
            grid_color=[1, 1, 1],
            center_color=[1, 1, 0]
        )
        grid.rotate_x(-math.pi / 2)
        self.scene.add(grid)

    def paintGL(self):
        self.clear()
        
        # since the update for this is not triggered by some external event (e.i mouseclick)
        # then we trigger the updateGL in the mainWindow
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

        self.units_per_second = 1
        self.degrees_per_second = 60
        
    def setupUi(self):
        pass

    # Qt can access keyboard events only if any of its top level window has keyboard focus.
    # If the window is minimized or another window takes focus, you will not receive keyboard events.
    def keyPressEvent(self, e):
        dt = 1/60
        move_amount = self.units_per_second * dt
        rotate_amount = self.degrees_per_second * (math.pi / 180) * dt

        key_pressed = e.text()
        if key_pressed == "w": # move_forwards
            self.glWidget.rig.translate(0, 0, -move_amount)
        if key_pressed == "s": # move_backwards
            self.glWidget.rig.translate(0, 0, move_amount)
        if key_pressed == "a": # move_left
            self.glWidget.rig.translate(-move_amount, 0, 0)
        if key_pressed == "d": # move_right
            self.glWidget.rig.translate(move_amount, 0, 0)
        if key_pressed == "r": # move_up
            self.glWidget.rig.translate(0, move_amount, 0)
        if key_pressed == "f": # move_down
            self.glWidget.rig.translate(0, -move_amount, 0)
        if key_pressed == "q": # turn_left
            self.glWidget.rig.rotate_y(-rotate_amount)
        if key_pressed == "e": # turn_right
            self.glWidget.rig.rotate_y(rotate_amount)

        # basically, we are moving the child node here
        if key_pressed == "t": # look_up
            self.glWidget.rig._look_attachment.rotate_x(rotate_amount)
        if key_pressed == "g": # look_down
            self.glWidget.rig._look_attachment.rotate_x(-rotate_amount)

        self.glWidget.update()
    
# deal with dpi
qtw.QApplication.setAttribute(qtc.Qt.AA_EnableHighDpiScaling, True)     # enable high dpi scaling
qtw.QApplication.setAttribute(qtc.Qt.AA_UseHighDpiPixmaps, True)        # use high dpi icons

app = qtw.QApplication(sys.argv)

# basically
window = MainWindow()
window.show()

# this starts the loop
sys.exit(app.exec_())
