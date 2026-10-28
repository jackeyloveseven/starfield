class_name FlightController
extends Node3D

# ==============================================================================
# STARFIELD // FLIGHT CONTROLLER & CORRIDOR DYNAMICS (GODOT 4.3)
# Multi-input Navigation, Banking Physics, Zero-Lag Travel & 15x Throttle Surge
# ==============================================================================

signal speed_multiplier_changed(multiplier: float)
signal region_crossed(new_region: UniverseRoute.CosmicRegion)

@export var base_speed: float = 65.0
@export var current_multiplier: float = 1.0
@export var max_boost_multiplier: float = 15.0
@export var steer_sensitivity: float = 45.0
@export var max_bank_angle: float = 35.0

var travel_z: float = 0.0
var _steer_input: Vector2 = Vector2.ZERO
var _current_bank: float = 0.0
var _current_region: UniverseRoute.CosmicRegion = UniverseRoute.CosmicRegion.PAPER

func _ready() -> void:
	var start_x = UniverseRoute.get_route_x(0.0)
	var start_y = UniverseRoute.get_route_y(0.0)
	global_position = Vector3(start_x, start_y, 0.0)

func _process(delta: float) -> void:
	handle_input(delta)
	update_flight(delta)

func handle_input(delta: float) -> void:
	var h = Input.get_axis("ui_left", "ui_right")
	var v = Input.get_axis("ui_down", "ui_up")

	# Throttle boost (Spacebar, Gamepad Trigger, or Screen Hold)
	var prev_multiplier = current_multiplier
	if Input.is_action_pressed("ui_accept") or Input.is_mouse_button_pressed(MOUSE_BUTTON_LEFT):
		current_multiplier = move_toward(current_multiplier, max_boost_multiplier, delta * 6.0)
	else:
		current_multiplier = move_toward(current_multiplier, 1.0, delta * 8.0)

	if not is_equal_approx(prev_multiplier, current_multiplier):
		speed_multiplier_changed.emit(current_multiplier)

	_steer_input = Vector2(h, v).limit_length(1.0)

func update_flight(delta: float) -> void:
	var speed = base_speed * current_multiplier
	travel_z += speed * delta

	# Analytical corridor positions
	var target_x = UniverseRoute.get_route_x(travel_z) + _steer_input.x * steer_sensitivity
	var target_y = UniverseRoute.get_route_y(travel_z) + _steer_input.y * steer_sensitivity

	# Design-to-Motion: Frame-rate independent exponential smoothing on lateral axes
	var t_lat = 1.0 - exp(-8.0 * delta)
	global_position.x = lerp(global_position.x, target_x, t_lat)
	global_position.y = lerp(global_position.y, target_y, t_lat)
	global_position.z = travel_z # Zero lag on longitudinal flight!

	# Dynamic banking roll (Exponential decay)
	var target_bank_rad = deg_to_rad(-_steer_input.x * max_bank_angle)
	var t_bank = 1.0 - exp(-6.0 * delta)
	_current_bank = lerp_angle(_current_bank, target_bank_rad, t_bank)

	# Forward alignment: aligns model -Z front with heading
	var heading = UniverseRoute.get_route_heading(travel_z)
	var forward_basis = Basis.looking_at(heading, Vector3.UP, false)
	transform.basis = forward_basis.rotated(heading, _current_bank)

	# Check region transition
	var reg = UniverseRoute.get_region(travel_z)
	if reg != _current_region:
		_current_region = reg
		region_crossed.emit(_current_region)
