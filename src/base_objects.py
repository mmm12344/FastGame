from components import Transform, MeshShape


class EmptyObject:
    def __init__(self):
        self.transform = Transform()
        self.children = []
        self.input_axes = {} 
        self.delta_time = 0
        self.tag = None
        
    def add_child(self, object=None):
        if type(object) != type(EmptyObject):
            raise TypeError('Object type must be or inheret from EmptyObject')
        self.children.append(object)
    
    def start(self):
        return
    
    def update(self):
        return
        
        
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
        
