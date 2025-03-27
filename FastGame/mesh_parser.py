import os
import numpy as np
import trimesh
from trimesh.exchange.obj import load_obj

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
        full_path = os.path.join(os.path.dirname(__file__), filename)
        
        mesh = trimesh.load(full_path, force='mesh', process=False)
        self.vertex_positions = mesh.vertices.astype(np.float32)
        self.indices = mesh.faces.astype(np.int32)
        self.normals = mesh.vertex_normals.astype(np.float32)
        
        
        print(mesh.visual)
        if hasattr(mesh.visual, 'uv') and mesh.visual.uv is not None and not np.allclose(mesh.visual.uv, 0):
            self.texture_coords = mesh.visual.uv.astype(np.float32)
        else:
            self.texture_coords = np.zeros((len(self.vertex_positions), 2), dtype=np.float32)
        
        vertices_list = []
        for i, pos in enumerate(mesh.vertices):
            tex = self.texture_coords[i] if i < len(self.texture_coords) else [0.0, 0.0]
            norm = self.normals[i] if i < len(self.normals) else [0.0, 0.0, 0.0]
            combined = np.concatenate((pos, tex, norm))
            vertices_list.append(combined)
        self.vertices = np.array(vertices_list, dtype=np.float32)
