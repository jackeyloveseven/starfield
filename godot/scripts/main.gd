class_name MainScene
extends Node3D

# ==============================================================================
# STARFIELD // MAIN SCENE ORCHESTRATOR (GODOT 4.3)
# Reactive signal wiring, exponential camera follow, dynamic warp FOV surge
# ==============================================================================

@onready var player: FlightController = $OrigamiPlayer
@onready var camera: Camera3D = $Camera3D
@onready var time_dilation: GravitationalTimeDilation = $TimeDilationManager
@onready var hud: FocusHUD = $UI/HUD
@onready var black_hole: MeshInstance3D = $BlackHole
@onready var music_manager: MusicManager = $MusicManager

var _current_region: UniverseRoute.CosmicRegion = UniverseRoute.CosmicRegion.PAPER

func _ready() -> void:
	print("[Starfield] Native Godot 4.3 Engine Initialized!")
	
	if black_hole and player:
		var bh_z = player.travel_z + 2400.0
		var bh_x = UniverseRoute.get_route_x(bh_z)
		var bh_y = UniverseRoute.get_route_y(bh_z)
		black_hole.position = Vector3(bh_x, bh_y, bh_z)

	if camera and player:
		# Behind player tail (+Z local) looking forward towards beak (-Z local / +Z world)
		camera.position = player.position + player.transform.basis.z * 18.0 + Vector3.UP * 4.5
		camera.look_at_from_position(camera.position, player.position - player.transform.basis.z * 10.0, Vector3.UP)

	if time_dilation and hud:
		time_dilation.dilation_changed.connect(hud.update_dilation_display)
		time_dilation.second_ticked.connect(hud.update_timer_display)
		if player:
			time_dilation.player_node = player

	if music_manager and hud:
		music_manager.track_changed.connect(func(_idx, title): hud.update_track_display(title))
		if music_manager.loaded_streams.size() > 0:
			hud.update_track_display(MusicManager.TRACK_TITLES[0])

	if player and hud:
		player.speed_multiplier_changed.connect(hud.update_speed_display)
		player.region_crossed.connect(_on_region_crossed)

	if hud:
		hud.update_region_display(UniverseRoute.get_region_name(_current_region))

func _process(delta: float) -> void:
	if not is_instance_valid(player) or not is_instance_valid(camera):
		return

	# 1. Design-to-Motion: Exponential decay smooth camera follow behind origami crane
	var target_cam_pos = player.global_position + player.transform.basis.z * 18.0 + Vector3.UP * 4.5
	var t_cam = 1.0 - exp(-6.0 * delta)
	camera.global_position = camera.global_position.lerp(target_cam_pos, t_cam)

	var look_target = player.global_position - player.transform.basis.z * 10.0
	if not camera.global_position.is_equal_approx(look_target):
		camera.look_at(look_target, Vector3.UP)

	# 2. Dynamic Warp FOV expansion (65deg cruise -> 78deg 15x warp surge)
	var target_fov = 65.0 + (player.current_multiplier - 1.0) * 0.92
	camera.fov = lerp(camera.fov, target_fov, 1.0 - exp(-5.0 * delta))

	# 3. Dynamic Black Hole on the Horizon (Surges closer under 15x Warp Boost)
	if is_instance_valid(black_hole):
		var boost_surge = (player.current_multiplier - 1.0) * 55.0
		var bh_z = player.travel_z + 2400.0 - boost_surge
		var bh_x = UniverseRoute.get_route_x(bh_z)
		var bh_y = UniverseRoute.get_route_y(bh_z)
		black_hole.global_position = Vector3(bh_x, bh_y, bh_z)

func _on_region_crossed(new_region: UniverseRoute.CosmicRegion) -> void:
	_current_region = new_region
	if hud:
		hud.update_region_display(UniverseRoute.get_region_name(_current_region))
	if music_manager:
		music_manager.switch_to_region(_current_region)
