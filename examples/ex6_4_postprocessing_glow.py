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
from core_ext.render_target import RenderTarget
from geometry.rectangle import RectangleGeometry
from geometry.sphere import SphereGeometry
from material.texture import TextureMaterial
from material.surface import SurfaceMaterial
from extras.movement_rig import MovementRig
from extras.postprocessor import Postprocessor
from effects.horizontal_blur import HorizontalBlurEffect
from effects.vertical_blur import VerticalBlurEffect
from effects.additive_blend import AdditiveBlendEffect


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

        self.renderer = Renderer(self, clear_color=[0, 0, 0])
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

        self.postprocessor = Postprocessor(self.renderer, self.scene, self.camera)

        # glow scene
        self.glow_scene = Scene()
        red_material = SurfaceMaterial(property_dict={"baseColor": [1, 0, 0]})
        glow_sphere = Mesh(sphere_geometry, red_material)
        glow_sphere.local_matrix = self.sphere.local_matrix
        self.glow_scene.add(glow_sphere)

        # glow postprocessing
        glow_target = RenderTarget(resolution=[800, 600])
        self.glow_pass = Postprocessor(self.renderer, self.glow_scene, self.camera, glow_target)
        self.glow_pass.add_effect(HorizontalBlurEffect(texture_size=[800, 600], blur_radius=50))
        self.glow_pass.add_effect(VerticalBlurEffect(texture_size=[800, 600], blur_radius=50))

        # combining results of glow effect with main scene
        self.combo_pass = Postprocessor(self.renderer, self.scene, self.camera)
        self.combo_pass.add_effect(
            AdditiveBlendEffect(
                blend_texture=glow_target.texture,
                original_strength=1,
                blend_strength=3
            )
        )

    def paintGL(self):
        self.clear()
        
        # time update
        now = time.time()
        self.dt = now - self.lastTime
        self.time_elapsed += self.dt
        self.lastTime = now

        self.sphere.rotate_y(0.01337)
        self.glow_pass.render()
        self.combo_pass.render()

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
