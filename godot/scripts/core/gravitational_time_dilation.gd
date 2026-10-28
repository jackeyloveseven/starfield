class_name GravitationalTimeDilation
extends Node

# ==============================================================================
# STARFIELD // GRAVITATIONAL TIME DILATION & FOCUS ENGINE (GODOT 4.3)
# Exact Schwarzschild metric dilation: d = sqrt(1 - rs / r)
# ==============================================================================

signal dilation_changed(dilation: float)
signal horizon_proximity_warning(is_active: bool)
signal second_ticked(formatted_time: String)

@export var black_hole_node: Node3D
@export var player_node: Node3D
@export var schwarzschild_radius: float = 800.0
@export var pomodoro_total_seconds: float = 1500.0 # 25 minutes Pomodoro
@export var is_focus_active: bool = true

var current_dilation: float = 1.0
var wall_clock_seconds: float = 0.0
var dilated_focus_seconds: float = 0.0

var _is_warning_active: bool = false
var _last_reported_sec: int = -1
var _last_emitted_dilation: float = -1.0

func _ready() -> void:
	DisplayServer.screen_set_keep_on(true)

func _exit_tree() -> void:
	DisplayServer.screen_set_keep_on(false)

func _process(delta: float) -> void:
	if not is_focus_active:
		return

	wall_clock_seconds += delta

	var target_measuring_node: Node3D = player_node
	if target_measuring_node == null:
		target_measuring_node = get_parent() as Node3D

	if black_hole_node != null and is_instance_valid(black_hole_node) and target_measuring_node != null:
		var r = target_measuring_node.global_position.distance_to(black_hole_node.global_position)
		current_dilation = compute_dilation(schwarzschild_radius, r)

		# Edge-triggered warning: emits only on state change to prevent signal storm
		if current_dilation < 0.85:
			if not _is_warning_active:
				_is_warning_active = true
				horizon_proximity_warning.emit(true)
		else:
			if _is_warning_active:
				_is_warning_active = false
				horizon_proximity_warning.emit(false)
	else:
		current_dilation = 1.0

	# Dilated focus timer advances at dilated rate: dt * d
	dilated_focus_seconds += delta * current_dilation

	if abs(current_dilation - _last_emitted_dilation) > 0.002:
		_last_emitted_dilation = current_dilation
		dilation_changed.emit(current_dilation)

	var current_sec = int(ceil(pomodoro_total_seconds - dilated_focus_seconds))
	if current_sec != _last_reported_sec:
		_last_reported_sec = current_sec
		second_ticked.emit(get_formatted_focus_time())

static func compute_dilation(rs: float, r: float) -> float:
	if rs <= 0.0 or r <= rs or r <= 0.001:
		return 0.05
	var ratio = clampf(rs / r, 0.0, 0.9975)
	return sqrt(1.0 - ratio)

func get_formatted_focus_time() -> String:
	var remaining_sec = max(0, int(ceil(pomodoro_total_seconds - dilated_focus_seconds)))
	var mins = remaining_sec / 60
	var secs = remaining_sec % 60
	return "%02d:%02d" % [mins, secs]
