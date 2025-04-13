import numpy as np

################################################################################
# Vector/Matrix Library

# This provides a convenient wrapper around NumPy for vectors and matrices
# It is also designed to be similar to GLM (a library used for OpenGL math)
# Hopefully, this will be useful if you ever decide to learn about OpenGL

# Note: A lot of this won't make sense until we learn about OOP and even then,
#       it uses a lot of advanced features, so feel free to ask me if you have
#       any questions.
################################################################################

class Vec2(np.ndarray):

    def __new__(cls, *args):
        if len(args) == 0:
            vec = np.zeros(2)
        elif len(args) == 1 and isinstance(args[0], (int, float)):
            vec = np.array(args * 2)
        elif len(args) == 2 and all(isinstance(x, (int, float)) for x in args):
            vec = np.array(args)
        return vec.view(cls)
    
    @property
    def x(self):
        return self[0]

    @x.setter
    def x(self, value):
        self[0] = value

    @property
    def y(self):
        return self[1]

    @y.setter
    def y(self, value):
        self[1] = value

    def norm_squared(self):
        return self.x**2 + self.y**2
    
    def norm(self):
        return np.sqrt(self.norm_squared())
    
    def normalize(self):
        n = self.norm()
        self.x /= n
        self.y /= n

    def unit(self):
        n = self.norm()
        return self / n
    
    @staticmethod
    def dot(v1, v2):
        if not isinstance(v1, Vec2) or not isinstance(v2, Vec2): return 0
        return np.dot(v1, v2)

    @staticmethod
    def cross(v1, v2):
        if not isinstance(v1, Vec2) or not isinstance(v2, Vec2): return 0
        return (v1.x * v2.y) - (v1.y * v2.x)

class Vec3(np.ndarray):

    def __new__(cls, *args):
        if len(args) == 0:
            vec = np.zeros(3)
        elif len(args) == 1 and isinstance(args[0], (int, float)):
            vec = np.array(args * 3)
        elif len(args) == 3 and all(isinstance(x, (int, float)) for x in args):
            vec = np.array(args)
        return vec.view(cls)

    @property
    def x(self):
        return self[0]

    @x.setter
    def x(self, value):
        self[0] = value

    @property
    def y(self):
        return self[1]

    @y.setter
    def y(self, value):
        self[1] = value

    @property
    def z(self):
        return self[2]

    @z.setter
    def z(self, value):
        self[2] = value

    def norm_squared(self):
        return self.x**2 + self.y**2 + self.z**2
    
    def norm(self):
        return np.sqrt(self.norm_squared())
    
    def normalize(self):
        n = self.norm()
        self.x /= n
        self.y /= n
        self.z /= n

    def unit(self):
        n = self.norm()
        return self / n
    
    def xy(self):
        return Vec2(self.x, self.y)
    
    @staticmethod
    def dot(v1, v2):
        if not isinstance(v1, Vec3) or not isinstance(v2, Vec3): return 0
        return np.dot(v1, v2)
    
    @staticmethod
    def cross(v1, v2):
        if not isinstance(v1, Vec3) or not isinstance(v2, Vec3): return Vec3()
        vec = np.cross(v1, v2)
        return vec.view(Vec3)

class Vec4(np.ndarray):

    def __new__(cls, *args):
        if len(args) == 0:
            vec = np.zeros(4)
        elif len(args) == 1:
            if isinstance(args[0], (int, float)):
                vec = np.array(args * 4)
            elif isinstance(args[0], Vec3):
                x = args[0]
                vec = np.array([x[0], x[1], x[2], 1.0])
        elif (len(args) == 2 and isinstance(args[0], Vec3)
              and isinstance(args[1], (int, float))):
            x = args[0]
            vec = np.array([x[0], x[1], x[2], args[1]])
        elif len(args) == 3 and all(isinstance(x, (int, float)) for x in args):
            vec = np.array([args[0], args[1], args[2], 1.0])
        elif len(args) == 4 and all(isinstance(x, (int, float)) for x in args):
            vec = np.array(args)
        return vec.view(cls)
    
    @property
    def x(self):
        return self[0]

    @x.setter
    def x(self, value):
        self[0] = value

    @property
    def y(self):
        return self[1]

    @y.setter
    def y(self, value):
        self[1] = value

    @property
    def z(self):
        return self[2]

    @z.setter
    def z(self, value):
        self[2] = value

    @property
    def w(self):
        return self[3]

    @w.setter
    def w(self, value):
        self[3] = value
    
    def norm_squared(self):
        return self.x**2 + self.y**2 + self.z**2 + self.w**2
    
    def norm(self):
        return np.sqrt(self.norm_squared())
    
    def normalize(self):
        n = self.norm()
        self.x /= n
        self.y /= n
        self.z /= n
        self.w /= n

    def unit(self):
        n = self.norm()
        return self / n
    
    def xyz(self):
        return Vec3(self.x, self.y, self.z)
    
    def xy(self):
        return Vec2(self.x, self.y)
    
    # Performs perspective division
    def project(self):
        return self.xyz() / self.w
    
    @staticmethod
    def dot(v1, v2):
        if not isinstance(v1, Vec3) or not isinstance(v2, Vec3): return 0
        return np.dot(v1, v2)

class Mat4(np.ndarray):

    def __new__(cls, *args):
        if len(args) == 0:
            mat = np.zeros((4, 4))
        elif (len(args) == 1 and isinstance(args[0], list) and (len(args[0]) == 16)
              and all(isinstance(x, (int, float)) for x in args[0])):
            mat = np.reshape(np.array(args[0]), (4, 4))
        elif len(args) == 4 and all(isinstance(x, Vec4) for x in args):
            mat = np.zeros((4, 4))
            mat[0] = args[0]
            mat[1] = args[1]
            mat[2] = args[2]
            mat[3] = args[3]
        elif len(args) == 16 and all(isinstance(x, (int, float)) for x in args):
            mat = np.reshape(np.array(args), (4, 4))
        return mat.view(cls)
    
    def __matmul__(self, other):
        if isinstance(other, Mat4):
            res = np.matmul(self, other)
            return res.view(Mat4)
        if isinstance(other, Vec4):
            res = np.matmul(self, other)
            return res.view(Vec4)
        # If we multiply a 4x4 matrix with a vector of length 3,
        # we first add a 1, multiply normally, then project down
        if isinstance(other, Vec3):
            res = np.matmul(self, Vec4(other)).view(Vec4)
            return res.project()
        
    ############################################################################
    # Transformation Matrices
    ############################################################################
    
    # Creates identity matrix
    @staticmethod
    def I(): 
        mat = np.identity(4)
        return mat.view(Mat4)

    @staticmethod
    def scale(scaleVec):
        if not isinstance(scaleVec, Vec3): return Mat4.I()
        mat = np.diag(Vec4(scaleVec))
        return mat.view(Mat4)
    
    @staticmethod
    def translate(translation):
        if not isinstance(translation, Vec3): return Mat4.I()
        mat = Mat4.I()
        mat[0:3, 3] = translation
        return mat

    @staticmethod
    def rotate(angle, rotationAxis):
        if not isinstance(rotationAxis, Vec3): return Mat4.I()
        a, r = angle, rotationAxis.unit()
        mat = Mat4.I()

        mat[0, 0] = np.cos(a) + (r.x ** 2) * (1 - np.cos(a))
        mat[0, 1] = r.x * r.y * (1 - np.cos(a)) - r.z * np.sin(a)
        mat[0, 2] = r.x * r.z * (1 - np.cos(a)) + r.y * np.sin(a)

        mat[1, 0] = r.y * r.x * (1 - np.cos(a)) + r.z * np.sin(a)
        mat[1, 1] = np.cos(a) + (r.y ** 2) * (1 - np.cos(a))
        mat[1, 2] = r.y * r.z * (1 - np.cos(a)) - r.x * np.sin(a)

        mat[2, 0] = r.z * r.x * (1 - np.cos(a)) - r.y * np.sin(a)
        mat[2, 1] = r.z * r.y * (1 - np.cos(a)) + r.x * np.sin(a)
        mat[2, 2] = np.cos(a) + (r.z ** 2) * (1 - np.cos(a))
        
        return mat
    
    ############################################################################
    # Projection Matrices
    ############################################################################
    
    # Creates matrix for orthographic projection (not used here)
    @staticmethod
    def ortho(left, right, bottom, top, near, far):
        mat = Mat4.I()
        mat[0, 0] = 2 / (right - left)
        mat[1, 1] = 2 / (top - bottom)
        mat[2, 2] = 2 / (near - far)
        mat[0, 3] = (-left - right) / (right - left)
        mat[1, 3] = (-bottom - top) / (top - bottom)
        mat[2, 3] = -near / (far - near)
        return mat
    
    # Creates matrix for perspective projection
    # fov - field of view (in radians)
    # aspectRatio - aspect ratio (width / height)
    # near - near plane location
    # far - far plane location
    @staticmethod
    def perspective(fov, aspectRatio, near, far):
        f = 1.0 / np.tan(fov / 2)
        mat = Mat4()
        mat[0, 0] = f / aspectRatio
        mat[1, 1] = f
        mat[2, 2] = (-far - near) / (far - near)
        mat[2, 3] = -2 * far * near / (far - near)
        mat[3, 2] = -1
        return mat
    
    # Creates matrix that makes the position relative to the camera
    # pos - camera position
    # at - position of camera target
    # up - camera up direction
    @staticmethod
    def lookAt(pos, at, up):
        f = (at - pos).unit()
        r = Vec3.cross(f, up).unit()
        u = Vec3.cross(r, f).unit()
        mat = Mat4()
        mat[0, 0:3] = r
        mat[1, 0:3] = u
        mat[2, 0:3] = -f
        mat[0, 3] = -Vec3.dot(r, pos)
        mat[1, 3] = -Vec3.dot(u, pos)
        mat[2, 3] = Vec3.dot(f, pos)
        mat[3, 3] = 1
        return mat
        
    # Creates matrix that converts from NDC to screen space
    @staticmethod
    def screenSpace(width, height):
        scaleVec = Vec3(width/2, height/2, 1)
        translateVec = Vec3(width/2, height/2, 0)
        return Mat4.translate(translateVec) @ Mat4.scale(scaleVec)