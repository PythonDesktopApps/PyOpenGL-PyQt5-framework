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

        # Initialize program #
        vs_code = """
            in vec3 position;
            void main()
            {
                gl_Position = vec4(position.x, position.y, position.z, 1.0);
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
        # Render settings (optional) #
        # on Mac, only 1px line is allowed
        GL.glLineWidth(1)
        # Set up vertex array object #
        vao_ref = GL.glGenVertexArrays(1)
        GL.glBindVertexArray(vao_ref)
        # Set up vertex attribute #
        position_data = [[ 0.8,  0.0,  0.0],
                         [ 0.4,  0.6,  0.0],
                         [-0.4,  0.6,  0.0],
                         [-0.8,  0.0,  0.0],
                         [-0.4, -0.6,  0.0],
                         [ 0.4, -0.6,  0.0]]
        self.vertex_count = len(position_data)
        position_attribute = Attribute('vec3', position_data)
        position_attribute.associate_variable(self.program_ref, 'position')

    def paintGL(self):
        self.clear()
        GL.glUseProgram(self.program_ref)
        GL.glDrawArrays(GL.GL_TRIANGLE_FAN, 0, self.vertex_count)
        
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
    
    @pyqtSlot()
    def open_close_joint(self):
        pass
    
    def keyPressEvent(self, e):
        pass
        # if e.key() == qtc.Qt.Key_Shift:
        #     self.glWidget.joint_type.mesh.select.shift = True
    
# deal with dpi
qtw.QApplication.setAttribute(qtc.Qt.AA_EnableHighDpiScaling, True)     # enable high dpi scaling
qtw.QApplication.setAttribute(qtc.Qt.AA_UseHighDpiPixmaps, True)        # use high dpi icons

app = qtw.QApplication(sys.argv)

window = MainWindow()
window.show()
sys.exit(app.exec_())
