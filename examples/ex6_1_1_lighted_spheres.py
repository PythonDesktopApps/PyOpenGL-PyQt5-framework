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
from extras.movement_rig import MovementRig
from geometry.sphere import SphereGeometry
from light.ambient import AmbientLight
from light.directional import DirectionalLight
from light.point import PointLight
from material.flat import FlatMaterial
from material.lambert import LambertMaterial
from material.phong import PhongMaterial


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
        self.rig = MovementRig()
        self.rig.add(self.camera)
        self.rig.set_position([0, 0, 6])
        self.scene.add(self.rig)

        # four light sources
        ambient_light = AmbientLight(color=[0.1, 0.1, 0.1])
        self.scene.add(ambient_light)
        directional_light = DirectionalLight(color=[0.8, 0.8, 0.8], direction=[-1, -1, -2])
        self.scene.add(directional_light)
        point_light1 = PointLight(color=[0.9, 0, 0], position=[4, 0, 0])
        self.scene.add(point_light1)
        point_light2 = PointLight(color=[0, 0.9, 0], position=[-4, 0, 0])
        self.scene.add(point_light2)

        # lighted materials with a color
        flat_material = FlatMaterial(
            property_dict={"baseColor": [0.2, 0.5, 0.5]},
            number_of_light_sources=4
        )
        lambert_material = LambertMaterial(
            property_dict={"baseColor": [0.2, 0.5, 0.5]},
            number_of_light_sources=4
        )
        phong_material = PhongMaterial(
            property_dict={"baseColor": [0.2, 0.5, 0.5]},
            number_of_light_sources=4
        )

        # lighted spheres with a color
        sphere_geometry = SphereGeometry()
        sphere_left_top = Mesh(sphere_geometry, flat_material)
        sphere_left_top.set_position([-2.5, 1.5, 0])
        self.scene.add(sphere_left_top)
        sphere_center_top = Mesh(sphere_geometry, lambert_material)
        sphere_center_top.set_position([0, 1.5, 0])
        self.scene.add(sphere_center_top)
        sphere_right_top = Mesh(sphere_geometry, phong_material)
        sphere_right_top.set_position([2.5, 1.5, 0])
        self.scene.add(sphere_right_top)

        # lighted materials with a texture
        textured_flat_material = FlatMaterial(
            texture=Texture("images/grid.jpg"),
            number_of_light_sources=4
        )
        textured_lambert_material = LambertMaterial(
            texture=Texture("images/grid.jpg"),
            number_of_light_sources=4
        )
        textured_phong_material = PhongMaterial(
            texture=Texture("images/grid.jpg"),
            number_of_light_sources=4
        )

        # lighted spheres with a texture
        sphere_left_bottom = Mesh(sphere_geometry, textured_flat_material)
        sphere_left_bottom.set_position([-2.5, -1.5, 0])
        self.scene.add(sphere_left_bottom)
        sphere_center_bottom = Mesh(sphere_geometry, textured_lambert_material)
        sphere_center_bottom.set_position([0, -1.5, 0])
        self.scene.add(sphere_center_bottom)
        sphere_right_bottom = Mesh(sphere_geometry, textured_phong_material)
        sphere_right_bottom.set_position([2.5, -1.5, 0])
        self.scene.add(sphere_right_bottom)

    def paintGL(self):
        # time update
        now = time.time()
        self.dt = now - self.lastTime
        self.time_elapsed += self.dt

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
        move_amount = self.units_per_second * self.glWidget.dt
        rotate_amount = self.degrees_per_second * (math.pi / 180) * self.glWidget.dt

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
