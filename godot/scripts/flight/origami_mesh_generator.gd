class_name OrigamiMeshGenerator
extends MeshInstance3D

# ==============================================================================
# STARFIELD // PROCEDURAL 3D ORIGAMI CRANE GENERATOR (GODOT 4.3)
# 0 External Model Assets: Procedural ArrayMesh with Godot -Z Standard Forward
# ==============================================================================

@export var wingspan: float = 3.6
@export var body_length: float = 2.4
@export var height_scale: float = 1.0

var _base_verts: PackedVector3Array = PackedVector3Array()
var _indices: PackedInt32Array = PackedInt32Array()
var _array_mesh: ArrayMesh

func _ready() -> void:
	build_base_mesh()

func build_base_mesh() -> void:
	# Standard Godot 3D Coordinate: -Z is Forward (Beak Tip), +Z is Back (Tail)
	_base_verts = PackedVector3Array([
		Vector3(0.0, 0.45 * height_scale, -1.2 * body_length),      # 0: Beak Tip (Forward -Z)
		Vector3(0.0, 0.20 * height_scale, -0.6 * body_length),      # 1: Neck Base
		Vector3(0.0, 0.0, 0.0),                                      # 2: Hull Center
		Vector3(0.0, 0.35 * height_scale, 1.3 * body_length),       # 3: Tail (+Z)
		Vector3(wingspan * 0.5, 0.25 * height_scale, -0.05),        # 4: Left Wing Tip
		Vector3(-wingspan * 0.5, 0.25 * height_scale, -0.05),       # 5: Right Wing Tip
		Vector3(0.0, -0.45 * height_scale, 0.0)                      # 6: Keel Bottom
	])

	# Single-sided clean 10-facet topology (Double-sided lighting handled by shader)
	_indices = PackedInt32Array([
		1, 4, 2,   # Left Wing Front Facet
		2, 4, 3,   # Left Wing Aft Facet
		1, 2, 5,   # Right Wing Front Facet
		2, 3, 5,   # Right Wing Aft Facet
		0, 1, 6,   # Crown & Beak Side
		0, 2, 1,   # Neck Ridge
		2, 6, 3,   # Tail Keel Bottom
		1, 6, 2,   # Throat Fold
		4, 6, 2,   # Left Wing Keel Fold
		5, 2, 6    # Right Wing Keel Fold
	])

	update_surface()

func update_surface() -> void:
	var arrays = []
	arrays.resize(Mesh.ARRAY_MAX)
	arrays[Mesh.ARRAY_VERTEX] = _base_verts
	arrays[Mesh.ARRAY_INDEX] = _indices

	# Generate surface normals automatically
	var surface_tool = SurfaceTool.new()
	surface_tool.create_from_arrays(arrays)
	surface_tool.generate_normals()

	_array_mesh = surface_tool.commit()
	mesh = _array_mesh
