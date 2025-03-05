from components import Transform, MeshShape


class EmptyObject:
    def __init__(self):
        self.transform = Transform()
        self._children = []
        
    def add_child(self, object=None):
        if type(object) != type(EmptyObject):
            raise TypeError('Object type must be or inheret from EmptyObject')
        self._children.append(object)
        
        
class Cuboid(EmptyObject): 
    def __init__(self, *args, **kwargs):
        super.__init__(*args, **kwargs)
        self.mesh = MeshShape('cuboid')
        
        
class Plane(EmptyObject): 
    def __init__(self, *args, **kwargs):
        super.__init__(*args, **kwargs)
        self.mesh = MeshShape('plane')
        
        
class Sphere(EmptyObject): 
    def __init__(self, *args, **kwargs):
        super.__init__(*args, **kwargs)
        self.mesh = MeshShape('sphere')
        
class Cylinder(EmptyObject): 
    def __init__(self, *args, **kwargs):
        super.__init__(*args, **kwargs)
        self.mesh = MeshShape('cylinder')
        
