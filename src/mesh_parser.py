import numpy as np

class MeshParser:
    def __init__(self, filename=None):
        self.vertex_positions = np.array([], dtype=np.float32)
        self.texture_coords = np.array([], dtype=np.float32)
        self.normals = np.array([], dtype=np.float32)
        
        self.indices = np.array([], dtype=np.int32)
        self.vertices = np.array([], dtype=np.float32)
        
        if filename:
            self.load(filename)
    
    def load(self, filename):
        
        vertex_map = {}
        with open(filename, 'r') as file:
            for line in file:
                if not line or line.startswith('#'):
                    continue
                parts = line.strip().split()
                if not parts:
                    continue
                prefix = parts[0]
                if prefix == 'v':
                    vertex = tuple(map(float, parts[1:4]))
                    self.vertex_positions.append(vertex)
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
                        key = (vertex_index, tex_index, norm_index)
                        face.append(key)
                        
                        if key not in vertex_map:
                        
                            combined = self.vertex_positions[vertex_index]
                            if tex_index is not None:
                                combined += self.texture_coords[tex_index]
                            else:
                                combined += [0.0, 0.0]
                            
                            if norm_index is not None:
                                combined += self.normals[norm_index]
                            else:
                                combined += [0.0, 0.0, 0.0]
                           
                            vertex_map[key] = len(self.vertices)
                            self.vertices.append(combined)
                        face.append(vertex_map[key])
                        
                if len(face) > 3:
                    for i in range(1, len(face) - 1):
                        self.indices.extend([face[0], face[i], face[i+1]])
                else:
                    self.indices.extend(face)
                    
    
    
