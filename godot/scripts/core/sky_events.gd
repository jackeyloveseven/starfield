class_name SkyEvents
extends Node

# ==============================================================================
# STARFIELD // SKY ASTRONOMICAL EVENTS ENGINE (GODOT 4.3)
# 0.34s Deterministic Gamma-Ray Burst (GRB) & Planetary Occultation
# ==============================================================================

signal grb_triggered(intensity: float, afterglow: float)
signal occultation_triggered(darkness: float)

@export var grb_enabled: bool = true

var _grb_timer: float = -1.0
const GRB_BURST_DURATION: float = 0.3402
const GRB_AFTERGLOW_DURATION: float = 20.0

var current_flash_intensity: float = 0.0
var current_afterglow_intensity: float = 0.0

func _process(delta: float) -> void:
	if _grb_timer >= 0.0:
		_grb_timer += delta

		if _grb_timer <= GRB_BURST_DURATION:
			# Fast peak flash: rises to 1.0 at 0.1s then drops sharply
			var t_norm = _grb_timer / GRB_BURST_DURATION
			current_flash_intensity = sin(t_norm * PI) * 0.95 + 0.05
		else:
			current_flash_intensity = 0.0

		if _grb_timer <= GRB_AFTERGLOW_DURATION:
			# 20s Exponential decay afterglow ring
			var decay = exp(-(_grb_timer - GRB_BURST_DURATION) * 0.35)
			current_afterglow_intensity = decay * 0.45
		else:
			current_afterglow_intensity = 0.0
			_grb_timer = -1.0

		grb_triggered.emit(current_flash_intensity, current_afterglow_intensity)

func trigger_grb() -> void:
	if not grb_enabled:
		return
	_grb_timer = 0.0
