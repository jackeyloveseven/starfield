class_name FocusHUD
extends Control

# ==============================================================================
# STARFIELD // FOCUS POMODORO HUD & TELEMETRY DASHBOARD (GODOT 4.3)
# Non-overlapping, responsive, frosted glass layout with 144Hz real-time updates
# Implements 'page-design' typographic hierarchy & 'design-to-motion' living UI
# ==============================================================================

@onready var timer_label: Label = %TimerLabel if has_node("%TimerLabel") else (find_child("TimerLabel", true, false) as Label)
@onready var dilation_label: Label = %DilationLabel if has_node("%DilationLabel") else (find_child("DilationLabel", true, false) as Label)
@onready var region_label: Label = %RegionLabel if has_node("%RegionLabel") else (find_child("RegionLabel", true, false) as Label)
@onready var track_label: Label = %TrackLabel if has_node("%TrackLabel") else (find_child("TrackLabel", true, false) as Label)
@onready var fps_label: Label = %FPSLabel if has_node("%FPSLabel") else (find_child("FPSLabel", true, false) as Label)
@onready var speed_label: Label = %SpeedLabel if has_node("%SpeedLabel") else (find_child("SpeedLabel", true, false) as Label)

var _fps_timer: float = 0.0

func _ready() -> void:
	# Ensure Chinese font is active
	var font = load("res://fonts/simhei.ttf")
	if font:
		var custom_theme = Theme.new()
		custom_theme.default_font = font
		theme = custom_theme

	resized.connect(_apply_responsive_layout)
	_apply_responsive_layout()

func _process(delta: float) -> void:
	_fps_timer += delta
	if _fps_timer >= 0.25:
		_fps_timer = 0.0
		var current_fps = Engine.get_frames_per_second()
		var label = get_fps_label()
		if label:
			label.text = "● %d FPS · 144Hz" % current_fps
			if current_fps >= 115:
				label.modulate = Color(0.31, 0.89, 0.76) # Starlight Mint
			else:
				label.modulate = Color(0.85, 0.88, 0.92)

func update_timer_display(time_str: String) -> void:
	var label = get_timer_label()
	if label and label.text != time_str:
		label.text = time_str
		# Living UI: subtle micro-scale punch on second tick
		var t = create_tween()
		t.tween_property(label, "scale", Vector2(1.025, 1.025), 0.08).set_trans(Tween.TRANS_SINE)
		t.tween_property(label, "scale", Vector2(1.0, 1.0), 0.15).set_trans(Tween.TRANS_SINE)

func update_dilation_display(d: float) -> void:
	var label = get_dilation_label()
	if label:
		var new_text = "d = %.3f · 相对论时间流速" % d
		if label.text != new_text:
			label.text = new_text
		if d < 0.70:
			label.modulate = Color(1.0, 0.38, 0.32) # Event horizon alert
		elif d < 0.90:
			label.modulate = Color(0.96, 0.82, 0.43) # Relativistic warp
		else:
			label.modulate = Color(0.38, 0.82, 1.0) # Calm starlight

func update_region_display(region_name: String) -> void:
	var label = get_region_label()
	if label and label.text != region_name:
		label.text = region_name

func update_track_display(track_title: String) -> void:
	var label = get_track_label()
	var formatted = "🎵 %s" % track_title
	if label and label.text != formatted:
		label.text = formatted

func update_speed_display(multiplier: float) -> void:
	var label = get_speed_label()
	if label:
		if multiplier > 1.2:
			label.text = "%.1fx 曲速爆发推进 (按住)" % multiplier
			label.modulate = Color(1.0, 0.85, 0.45)
		else:
			var normal_text = "1.0x 巡航速度 (长按加速)"
			if label.text != normal_text:
				label.text = normal_text
				label.modulate = Color(0.65, 0.72, 0.82)

func _apply_responsive_layout() -> void:
	var safe_area: Rect2i = DisplayServer.get_display_safe_area()
	var margin_top = get_node_or_null("TopBarMargin") as MarginContainer
	if margin_top:
		margin_top.add_theme_constant_override("margin_left", max(24, safe_area.position.x))
		margin_top.add_theme_constant_override("margin_right", max(24, int(get_viewport_rect().size.x - safe_area.end.x)))

# Safe getters with fallback resolution for headless test harness
func get_timer_label() -> Label:
	if timer_label == null:
		timer_label = get_node_or_null("%TimerLabel") as Label
		if timer_label == null:
			timer_label = find_child("TimerLabel", true, false) as Label
	return timer_label

func get_dilation_label() -> Label:
	if dilation_label == null:
		dilation_label = get_node_or_null("%DilationLabel") as Label
		if dilation_label == null:
			dilation_label = find_child("DilationLabel", true, false) as Label
	return dilation_label

func get_region_label() -> Label:
	if region_label == null:
		region_label = get_node_or_null("%RegionLabel") as Label
		if region_label == null:
			region_label = find_child("RegionLabel", true, false) as Label
	return region_label

func get_track_label() -> Label:
	if track_label == null:
		track_label = get_node_or_null("%TrackLabel") as Label
		if track_label == null:
			track_label = find_child("TrackLabel", true, false) as Label
	return track_label

func get_fps_label() -> Label:
	if fps_label == null:
		fps_label = get_node_or_null("%FPSLabel") as Label
		if fps_label == null:
			fps_label = find_child("FPSLabel", true, false) as Label
	return fps_label

func get_speed_label() -> Label:
	if speed_label == null:
		speed_label = get_node_or_null("%SpeedLabel") as Label
		if speed_label == null:
			speed_label = find_child("SpeedLabel", true, false) as Label
	return speed_label
