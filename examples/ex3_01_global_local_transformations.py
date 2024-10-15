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
from core.attribute import Attribute
from core.uniform import Uniform
from core.matrix import Matrix

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

        ### Initialize program ###
        vs_code = """
            in vec3 position;
            uniform mat4 projectionMatrix;
            uniform mat4 modelMatrix;
            void main()
            {
                gl_Position = projectionMatrix * modelMatrix * vec4(position, 1.0);
            }
        """
        fs_code = """
            out vec4 fragColor;
            void main()
            {
                fragColor = vec4(1.0, 1.0, 0.0, 1.0);
            }
        """
        self.program_ref = Utils.initialize_program(vs_code, fs_code)
        ### Render settings ###
        GL.glClearColor(0.0, 0.0, 0.0, 1.0)
        GL.glEnable(GL.GL_DEPTH_TEST)
        ### Set up vertex array object ###
        vao_ref = GL.glGenVertexArrays(1)
        GL.glBindVertexArray(vao_ref)
        ### Set up vertex attribute: three points of triangle ###
        position_data = [[0.0,   0.2,  0.0], [0.1,  -0.2,  0.0], [-0.1, -0.2,  0.0]]
        self.vertex_count = len(position_data)
        position_attribute = Attribute('vec3', position_data)
        position_attribute.associate_variable(self.program_ref, 'position')
        ### Set up uniforms ###
        m_matrix = Matrix.make_translation(0, 0, -1)
        self.model_matrix = Uniform('mat4', m_matrix)
        self.model_matrix.locate_variable(self.program_ref, 'modelMatrix')
        p_matrix = Matrix.make_perspective()
        self.projection_matrix = Uniform('mat4', p_matrix)
        self.projection_matrix.locate_variable(self.program_ref, 'projectionMatrix')
        # movement speed, units per second
        self.move_speed = 0.5
        # rotation speed, radians per second
        self.turn_speed = 90 * (math.pi / 180)

    def paintGL(self):
        self.clear()
        
        ### Render scene ###
        GL.glClear(GL.GL_COLOR_BUFFER_BIT | GL.GL_DEPTH_BUFFER_BIT)
        GL.glUseProgram(self.program_ref)
        self.projection_matrix.upload_data()
        self.model_matrix.upload_data()
        GL.glDrawArrays(GL.GL_TRIANGLES, 0, self.vertex_count)

    # def resizeGL(self, w, h):
    #     pass

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

        # timer = qtc.QTimer(self)
        # timer.setInterval(20)  # period, in milliseconds
        # timer.timeout.connect(self.glWidget.updateGL)
        # timer.start()

    def setupUi(self):
        pass
        # get opengl window size - not really needed
        # self.x_range = [10, 500]
        # self.y_range = [10, 500]

        # note that the widgets are made attribute to be reused again
        # ---Design
        # self.btn_open_close_joint = self.findChild(qtw.QPushButton, "btn_open_close_joint")

    
    def keyPressEvent(self, e):
        
        # move_speed and turn_speed are glWidget property hence they remain there
        # however keyPress are recognized only on the mainWindow hence used here

        dt = 0.05
        move_amount = self.glWidget.move_speed * dt
        turn_amount = self.glWidget.turn_speed * dt

        key_pressed = e.text()
        # @ acts as matrix multiplication when applied to matrices
        # but acts as dot product when applied to vectors
        # global translation
        if key_pressed == 'w':
            print(key_pressed)
            m = Matrix.make_translation(0, move_amount, 0)
            self.glWidget.model_matrix.data = m @ self.glWidget.model_matrix.data
        # why s is not working?
        if key_pressed == 's':
            print(key_pressed)
            m = Matrix.make_translation(0, -move_amount, 0)
            self.glWidget.model_matrix.data = m @ self.glWidget.model_matrix.data
        if key_pressed == 'a':
            m = Matrix.make_translation(-move_amount, 0, 0)
            self.glWidget.model_matrix.data = m @ self.glWidget.model_matrix.data
        if key_pressed == 'd':
            m = Matrix.make_translation(move_amount, 0, 0)
            self.glWidget.model_matrix.data = m @ self.glWidget.model_matrix.data
        if key_pressed == 'z':
            m = Matrix.make_translation(0, 0, move_amount)
            self.glWidget.model_matrix.data = m @ self.glWidget.model_matrix.data
        if key_pressed == 'x':
            m = Matrix.make_translation(0, 0, -move_amount)
            self.glWidget.model_matrix.data = m @ self.glWidget.model_matrix.data
        
        # global rotation (around the origin)
        if key_pressed == 'q':
            m = Matrix.make_rotation_z(turn_amount)
            self.glWidget.model_matrix.data = m @ self.glWidget.model_matrix.data
        if key_pressed == 'e':
            m = Matrix.make_rotation_z(-turn_amount)
            self.glWidget.model_matrix.data = m @ self.glWidget.model_matrix.data
        # local translation
        if key_pressed == 'i':
            m = Matrix.make_translation(0, move_amount, 0)
            self.glWidget.model_matrix.data = self.glWidget.model_matrix.data @ m
        if key_pressed == 'k':
            m = Matrix.make_translation(0, -move_amount, 0)
            self.glWidget.model_matrix.data = self.glWidget.model_matrix.data @ m
        if key_pressed == 'j':
            m = Matrix.make_translation(-move_amount, 0, 0)
            self.glWidget.model_matrix.data = self.glWidget.model_matrix.data @ m
        if key_pressed == 'l':
            m = Matrix.make_translation(move_amount, 0, 0)
            self.glWidget.model_matrix.data = self.glWidget.model_matrix.data @ m
        # local rotation (around object center)
        if key_pressed == 'u':
            m = Matrix.make_rotation_z(turn_amount)
            self.glWidget.model_matrix.data = self.glWidget.model_matrix.data @ m
        if key_pressed == 'o':
            m = Matrix.make_rotation_z(-turn_amount)
            self.glWidget.model_matrix.data = self.glWidget.model_matrix.data @ m

        # use update() when using QOpenGLWidget
        self.glWidget.update()
    
# deal with dpi
qtw.QApplication.setAttribute(qtc.Qt.AA_EnableHighDpiScaling, True)     # enable high dpi scaling
qtw.QApplication.setAttribute(qtc.Qt.AA_UseHighDpiPixmaps, True)        # use high dpi icons

app = qtw.QApplication(sys.argv)

window = MainWindow()
window.show()
sys.exit(app.exec_())
