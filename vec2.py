from math import hypot, atan2, pi, cos, sin
class Vector2(object):
     def __init__(self, x=0.0, y=0.0):
          self.x = x
          self.y = y
     def __str__(self):
          return "(%s, %s)"%(self.x, self.y)
     def project(self, vec):
          return self.dot(vec.normalise())
     def get_magnitude(self):
          return hypot(self.x, self.y)
     def dot(self, vec):
          return self.x * vec.x + self.y * vec.y
     def angle(self):
          a = atan2(self.x, self.y)
          if a < 0:
               a += pi * 2
          return a
     def rotate(self, a):
          x = (self.x * cos(a)) - (self.y * sin(a))
          y = (self.x * sin(a)) + (self.y * cos(a))
          return Vector2(x,y)
     def leftNormal(self):
          return Vector2(-self.y, self.x)
     def rightNormal(self):
          return Vector2(self.y, -self.x)
     def normalise(self):
          magnitude = self.get_magnitude()
          x = self.x / magnitude
          y = self.y / magnitude
          return Vector2(x,y)
     def __add__(self, rhs):
          if isinstance(rhs, Vector2):
               return Vector2(self.x + rhs.x, self.y + rhs.y)
          else:
               return Vector2(self.x + rhs[0], self.y + rhs[1])
     def __sub__(self, rhs):
          if isinstance(rhs, Vector2):
               return Vector2(self.x - rhs.x, self.y - rhs.y)
          else:
               return Vector2(self.x - rhs[0], self.y - rhs[1])
     def __neg__(self):
          return Vector2(-self.x, -self.y)
     def __mul__(self, scalar):
          return Vector2(self.x * scalar, self.y * scalar)
     def __truediv__(self, scalar):
          return Vector2(self.x / scalar, self.y / scalar)
     def __floordiv__(self, scalar):
          return Vector2(self.x // scalar, self.y // scalar)
     def get_tuple(self, intMode = False):
          if intMode: return (int(self.x), int(self.y))
          return (self.x, self.y)
     @classmethod
     def from_tuple(cls, tup):
          return cls(tup[0], tup[1])
