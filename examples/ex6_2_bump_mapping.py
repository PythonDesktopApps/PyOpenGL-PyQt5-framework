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
from core_ext.texture import Texture
from geometry.rectangle import RectangleGeometry
from extras.point_light import PointLightHelper
from light.ambient import AmbientLight
from light.point import PointLight
from material.lambert import LambertMaterial


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
        self.time_elapsed = 0
        self.dt = 0

    def initializeGL(self):
        # print gl info
        Utils.print_system_info()

        self.gl_settings()

        self.renderer = Renderer(self)
        self.scene = Scene()
        self.camera = Camera(aspect_ratio=800/600)
        self.camera.set_position([0, 0, 2])

        ambient_light = AmbientLight(color=[0.3, 0.3, 0.3])
        self.scene.add(ambient_light)
        self.point_light = PointLight(color=[1, 1, 1], position=[1, 0, 1])
        self.scene.add(self.point_light)
        # texture of a brick wall
        color_texture = Texture("images/brick-wall.jpg")
        # texture of normals of the brick wall
        bump_texture = Texture("images/brick-wall-normal-map.jpg")

        rectangle_geometry = RectangleGeometry(width=2, height=2)

        color_material = LambertMaterial(
            texture=color_texture,
            number_of_light_sources=2
        )

        bump_material = LambertMaterial(
            texture=color_texture,
            bump_texture=bump_texture,
            property_dict={"bumpStrength": 1},
            number_of_light_sources=2
        )

        # Replace color_material and bump_material
        # in Mesh to see a difference
        mesh = Mesh(rectangle_geometry, bump_material)
        self.scene.add(mesh)

        point_light_helper = PointLightHelper(self.point_light)
        self.point_light.add(point_light_helper)

    def paintGL(self):
        self.clear()
        
        # time update
        now = time.time()
        self.dt = now - self.lastTime
        self.time_elapsed += self.dt
        self.lastTime = now

        self.point_light.set_position([math.cos(0.5 * self.time_elapsed) / 2, math.sin(0.5 * self.time_elapsed) / 2, 1])
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
        
        # in this example, glWidget is updated by timer as well as the keyboard
        timer = qtc.QTimer(self)
        # timer.setInterval(1000/60)  # period, in milliseconds
        timer.setInterval(17)  # on Mac, it accepts only int
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
