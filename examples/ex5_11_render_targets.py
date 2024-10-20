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
from core_ext.render_target import RenderTarget
from core_ext.renderer import Renderer
from core_ext.scene import Scene
from core_ext.texture import Texture
from geometry.box import BoxGeometry
from geometry.rectangle import RectangleGeometry
from geometry.sphere import SphereGeometry
from material.surface import SurfaceMaterial
from material.texture import TextureMaterial
from extras.movement_rig import MovementRig


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

    def initializeGL(self):
        # print gl info
        Utils.print_system_info()

        self.gl_settings()

        self.renderer = Renderer(self)
        self.scene = Scene()
        self.camera = Camera(aspect_ratio=800/600)
        self.rig = MovementRig()
        self.rig.add(self.camera)
        self.scene.add(self.rig)
        self.rig.set_position([0, 1, 4])
        sky_geometry = SphereGeometry(radius=50)
        sky_material = TextureMaterial(texture=Texture(file_name="images/sky.jpg"))
        sky = Mesh(sky_geometry, sky_material)
        self.scene.add(sky)

        grass_geometry = RectangleGeometry(width=100, height=100)
        grass_material = TextureMaterial(
            texture=Texture(file_name="images/grass.jpg"),
            property_dict={"repeatUV": [50, 50]}
        )
        grass = Mesh(grass_geometry, grass_material)
        grass.rotate_x(-math.pi/2)
        self.scene.add(grass)

        sphere_geometry = SphereGeometry()
        sphere_material = TextureMaterial(Texture("images/grid.jpg"))
        self.sphere = Mesh(sphere_geometry, sphere_material)
        self.sphere.set_position([0, 1, 0])
        self.scene.add(self.sphere)

        box_geometry = BoxGeometry(width=1.12, height=1.12, depth=0.2)
        box_material = SurfaceMaterial(property_dict={"baseColor": [0, 0, 0]})
        box = Mesh(box_geometry, box_material)
        box.set_position([2, 1, 0])
        self.scene.add(box)

        # Create the "television screen" on the box
        self.render_target = RenderTarget(resolution=[512, 512])
        screen_geometry = RectangleGeometry(width=1.1, height=1.1)
        screen_material = TextureMaterial(self.render_target.texture)
        screen = Mesh(screen_geometry, screen_material)
        screen.set_position([2, 1, 0.11])
        self.scene.add(screen)

        self.sky_camera = Camera(aspect_ratio=512/512)
        self.sky_camera.set_position([0, 10, 0])
        self.sky_camera.look_at([0, 0, 0])
        self.scene.add(self.sky_camera)

    def paintGL(self):
        self.clear()
        
        # though the rotate does not depend on delta_time
        # we need to trigger update at the standard fps to show that the sphere is rotating
        self.sphere.rotate_y(0.01337)
        self.renderer.render(self.scene, self.sky_camera, render_target=self.render_target)
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

        timer = qtc.QTimer(self)
        timer.setInterval(1000/60)  # period, in milliseconds
        timer.timeout.connect(self.glWidget.update)
        timer.start()

    def setupUi(self):
        pass

    # Qt can access keyboard events only if any of its top level window has keyboard focus.
    # If the window is minimized or another window takes focus, you will not receive keyboard events.
    def keyPressEvent(self, e):
        dt = 1/60
        move_amount = self.units_per_second * dt
        rotate_amount = self.degrees_per_second * (math.pi / 180) * dt

        key_pressed = e.text()
        if key_pressed == "w":
            self.glWidget.rig.translate(0, 0, -move_amount)
        if key_pressed == "s":
            self.glWidget.rig.translate(0, 0, move_amount)
        if key_pressed == "a":
            self.glWidget.rig.translate(-move_amount, 0, 0)
        if key_pressed == "d":
            self.glWidget.rig.translate(move_amount, 0, 0)
        if key_pressed == "r":
            self.glWidget.rig.translate(0, move_amount, 0)
        if key_pressed == "f":
            self.glWidget.rig.translate(0, -move_amount, 0)
        if key_pressed == "q":
            self.glWidget.rig.rotate_y(-rotate_amount)
        if key_pressed == "e":
            self.glWidget.rig.rotate_y(rotate_amount)

        # basically, we are moving the child node here
        if key_pressed == "t":
            self.glWidget.rig._look_attachment.rotate_x(rotate_amount)
        if key_pressed == "g":
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
