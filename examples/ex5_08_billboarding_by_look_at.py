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
from core.matrix import Matrix
from core_ext.camera import Camera
from core_ext.mesh import Mesh
from core_ext.renderer import Renderer
from core_ext.scene import Scene
from core_ext.texture import Texture
from geometry.box import BoxGeometry
from geometry.rectangle import RectangleGeometry
from extras.text_texture import TextTexture
from material.texture import TextureMaterial


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

        self.lastTime = time.time()

    def initializeGL(self):
        # print gl info
        Utils.print_system_info()

        self.gl_settings()

        self.renderer = Renderer(self)
        self.scene = Scene()
        self.camera = Camera(aspect_ratio=800/600)
        # self.rig = MovementRig()
        # self.rig.add(self.camera)
        self.camera.set_position([0, 1, 5])
        self.scene.add(self.camera)

        label_texture = TextTexture(text=" This is a Crate ",
                                    system_font_name="Arial Bold",
                                    font_size=40,
                                    font_color=[0, 0, 200],
                                    image_width=256,
                                    image_height=128,
                                    align_horizontal=0.5,
                                    align_vertical=0.5,
                                    image_border_width=4,
                                    image_border_color=[255, 0, 0])
        label_material = TextureMaterial(label_texture)
        label_geometry = RectangleGeometry(width=1, height=0.5)
        label_geometry.apply_matrix(Matrix.make_rotation_y(math.pi))
        self.label = Mesh(label_geometry, label_material)
        self.label.set_position([0, 1, 0])
        self.scene.add(self.label)

        crate_geometry = BoxGeometry()
        crate_texture = Texture("images/crate.jpg")
        crate_material = TextureMaterial(crate_texture)
        crate = Mesh(crate_geometry, crate_material)
        self.scene.add(crate)

    def paintGL(self):
        self.clear()
        
        # Time update
        # now = time.time()
        # dt = now - self.lastTime
        # self.lastTime = now

        self.label.look_at(self.camera.global_position)
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

        self.units_per_second = 1
        self.degrees_per_second = 60
        
    def setupUi(self):
        pass

    # Qt can access keyboard events only if any of its top level window has keyboard focus.
    # If the window is minimized or another window takes focus, you will not receive keyboard events.
    def keyPressEvent(self, e):
        dt = 0.05
        move_amount = self.units_per_second * dt
        rotate_amount = self.degrees_per_second * (math.pi / 180) * dt

        key_pressed = e.text()
        if key_pressed == "w":
            # move_forwards
            self.glWidget.camera.translate(0, 0, -move_amount)
        if key_pressed == "s":
            # move_backwards
            self.glWidget.camera.translate(0, 0, move_amount)
        if key_pressed == "a":
            # move_left
            self.glWidget.camera.translate(-move_amount, 0, 0)
        if key_pressed == "d":
            # move_right
            self.glWidget.camera.translate(move_amount, 0, 0)
        if key_pressed == "r":
            # move_up
            self.glWidget.camera.translate(0, move_amount, 0)
        if key_pressed == "f":
            # move_down
            self.glWidget.camera.translate(0, -move_amount, 0)
        if key_pressed == "q":
            # turn left
            self.glWidget.camera.rotate_y(-rotate_amount)
        if key_pressed == "e":
            # turn right
            self.glWidget.camera.rotate_y(rotate_amount)

        # TODO: why is the old code using _look_attachment
        if key_pressed == "t":
            # look up
            self.glWidget.camera.rotate_x(rotate_amount)
        if key_pressed == "g":
            # look down
            self.glWidget.camera.rotate_x(-rotate_amount)

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
