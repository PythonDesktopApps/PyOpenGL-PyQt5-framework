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
from material.material import Material


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
        self.camera = Camera(aspect_ratio=800 / 600)
        self.camera.set_position([0, 0, 1.5])
        vertex_shader_code = """
            uniform mat4 projectionMatrix;
            uniform mat4 viewMatrix;
            uniform mat4 modelMatrix;
            in vec3 vertexPosition;
            in vec2 vertexUV;
            out vec2 UV;

            void main()
            {
                vec4 pos = vec4(vertexPosition, 1.0);
                gl_Position = projectionMatrix * viewMatrix * modelMatrix * pos;
                UV = vertexUV;
            }
        """
        fragment_shader_code = """
            // Return a random value in [0, 1]
            float random(vec2 UV)
            {
                return fract(235711.0 * sin(14.337 * UV.x + 42.418 * UV.y));
            }

            float boxRandom(vec2 UV, float scale)
            {
                vec2 iScaleUV = floor(scale * UV);
                return random(iScaleUV);
            }

            float smoothRandom(vec2 UV, float scale)
            {
                vec2 iScaleUV = floor(scale * UV);
                vec2 fScaleUV = fract(scale * UV);
                float a = random(iScaleUV);
                float b = random(round(iScaleUV + vec2(1, 0)));
                float c = random(round(iScaleUV + vec2(0, 1)));
                float d = random(round(iScaleUV + vec2(1, 1)));
                return mix(mix(a, b, fScaleUV.x), mix(c, d, fScaleUV.x), fScaleUV.y);
            }

            // Add smooth random values at different scales
            // weighted (amplitudes) so that sum is approximately 1.0
            float fractalLikeRandom(vec2 UV, float scale)
            {
                float value = 0.0;
                float amplitude = 0.5;
                for (int i = 0; i < 10; i++)
                {
                    value += amplitude * smoothRandom(UV, scale);
                    scale *= 2.0;
                    amplitude *= 0.5;
                }
                return value;
            }

            in vec2 UV;
            out vec4 fragColor;
            void main()
            {
                // smoothed random color
                // float r = random(UV);
                // float r = boxRandom(UV, 10);
                // float r = smoothRandom(UV, 10);
                float r = fractalLikeRandom(UV, 10);
                fragColor = vec4(r, r, r, 1);  
            }
        """
        material = Material(vertex_shader_code, fragment_shader_code)
        material.locate_uniforms()

        geometry = RectangleGeometry()
        mesh = Mesh(geometry, material)
        self.scene.add(mesh)

    def paintGL(self):
        # Time update
        # now = time.time()
        # dt = now - self.lastTime
        # self.lastTime = now

        # self.distort_material.uniform_dict["time"].data += dt
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
        timer.timeout.connect(self.glWidget.update)
        timer.start()

    def setupUi(self):
        pass
        # get opengl window size - not really needed
        # self.x_range = [10, 500]
        # self.y_range = [10, 500]

        # note that the widgets are made attribute to be reused again
        # ---Design
        # self.btn_open_close_joint = self.findChild(qtw.QPushButton, "btn_open_close_joint")

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
