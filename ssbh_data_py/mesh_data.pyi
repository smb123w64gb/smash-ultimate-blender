from typing import List, Tuple, Any


def read_mesh(path: str) -> MeshData: ...


class MeshData:
    major_version: int
    minor_version: int
    objects: list[MeshObjectData]

    def __init__(
        self,
        major_version: int = ...,
        minor_version: int = ...,
    ) -> None: ...

    def save(self, path: str) -> None: ...


class MeshObjectData:
    name: str
    sub_index: int
    parent_bone_name: str
    vertex_indices: list[int]
    positions: list[AttributeData]
    normals: list[AttributeData]
    binormals: list[AttributeData]
    tangents: list[AttributeData]
    texture_coordinates: list[AttributeData]
    color_sets: list[AttributeData]
    bone_influences: list[BoneInfluence]

    def __init__(
        self,
        name: str,
        sub_index: int,
    ) -> None: ...


class AttributeData:
    name: str
    data: list[list[float]]

    def __init__(
        self,
        name: str,
    ) -> None: ...


class BoneInfluence:
    bone_name: str
    vertex_weights: list[VertexWeight]

    def __init__(
        self,
        bone_name: str,
        vertex_weights: list[VertexWeight],
    ) -> None: ...


class VertexWeight:
    vertex_index: int
    vertex_weight: float

    def __init__(
        self,
        vertex_index: int,
        vertex_weight: float,
    ) -> None: ...
