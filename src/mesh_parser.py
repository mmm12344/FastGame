

class MeshParser:
    def __init__(self, filename=None):
        self.vertices = []
        self.texture_coords = []
        self.normals = []
        self.faces = []
        if filename:
            self.load(filename)
    
    def load(self, filename):
        with open(filename, 'r') as file:
            for line in file:
                parts = line.strip().split()
                if not parts:
                    continue
                prefix = parts[0]
                if prefix == 'v':
                    vertex = tuple(map(float, parts[1:4]))
                    self.vertices.append(vertex)
                elif prefix == 'vt':
                    tex_coord = tuple(map(float, parts[1:3]))
                    self.texture_coords.append(tex_coord)
                elif prefix == 'vn':
                    normal = tuple(map(float, parts[1:4]))
                    self.normals.append(normal)
                elif prefix == 'f':
                    face = []
                    for v in parts[1:]:
                        indices = v.split('/')
                        vertex_index = int(indices[0]) - 1 if indices[0] else None
                        tex_index = int(indices[1]) - 1 if len(indices) >= 2 and indices[1] != '' else None
                        norm_index = int(indices[2]) - 1 if len(indices) == 3 and indices[2] != '' else None
                        face.append((vertex_index, tex_index, norm_index))
                    self.faces.append(face)
    
    
