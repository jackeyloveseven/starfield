class_name MusicManager
extends Node

# ==============================================================================
# STARFIELD GODOT 4.3 // NATIVE ORIGINAL SCORE SOUNDTRACK MANAGER
# Plays 6 authentic master-recorded MP3 scores with seamless Tween cross-fading
# ==============================================================================

signal track_changed(track_index: int, track_title: String)

const TRACK_PATHS: Array[String] = [
	"res://audio/music/1-paper.mp3",
	"res://audio/music/2-inkwash.mp3",
	"res://audio/music/3-foil.mp3",
	"res://audio/music/4-core.mp3",
	"res://audio/music/5-abyss.mp3",
	"res://audio/music/6-drift.mp3",
	"res://audio/music/7-saul.mp3",
	"res://audio/music/8-shigatsu-rondo.mp3"
]

const TRACK_TITLES: Array[String] = [
	"1. 原野 · 晨曦微光 (D 大调 / A 混合利底亚 · 66s)",
	"2. 月图 · 远山水墨 (A 自然小调 · 71s)",
	"3. 暖纸 · 金箔流霞 (A 混合利底亚 · 71s)",
	"4. 暮粉 · 核心回响 (A 自然小调 · 74s)",
	"5. 夜航 · 深渊行迹 (A 自然小调 深沉 · 78s)",
	"6. 雪境 · 冰穹低语 (升F 小调 · 69s)",
	"7. 律政狂想 · Better Call Saul TV Theme (15s)",
	"8. 友人A · 四月是你的谎言 第4话《圣·桑：引子与回旋随想曲 Op.28》完整版 (9分15秒)"
]

const MIN_DB: float = -80.0
const TARGET_DB: float = -4.0
const FADE_DURATION: float = 2.0

var player_a: AudioStreamPlayer
var player_b: AudioStreamPlayer
var active_player: AudioStreamPlayer
var inactive_player: AudioStreamPlayer

var current_track_index: int = -1
var loaded_streams: Array[AudioStream] = []
var _crossfade_tween: Tween
var _gap_timer: Timer

func _init() -> void:
	# Pre-load all 6 original streams
	for path in TRACK_PATHS:
		if ResourceLoader.exists(path):
			var stream = load(path) as AudioStream
			loaded_streams.append(stream)
		else:
			push_warning("[MusicManager] Stream not found: %s" % path)
			loaded_streams.append(null)

func _ready() -> void:
	_ensure_audio_players()

	_gap_timer = Timer.new()
	_gap_timer.one_shot = true
	_gap_timer.wait_time = 2.4
	_gap_timer.timeout.connect(_on_gap_timer_timeout)
	add_child(_gap_timer)
			
	# Start playing track 0 by default
	if loaded_streams.size() > 0 and loaded_streams[0] != null:
		play_track(0, true)

func _ensure_audio_players() -> void:
	if player_a == null:
		player_a = AudioStreamPlayer.new()
		player_a.name = "AudioPlayerA"
		player_a.bus = &"Master"
		add_child(player_a)
		player_a.finished.connect(_on_player_finished.bind(player_a))
	if player_b == null:
		player_b = AudioStreamPlayer.new()
		player_b.name = "AudioPlayerB"
		player_b.bus = &"Master"
		add_child(player_b)
		player_b.finished.connect(_on_player_finished.bind(player_b))
	
	if active_player == null:
		active_player = player_a
	if inactive_player == null:
		inactive_player = player_b

func play_track(track_index: int, force_restart: bool = false) -> void:
	_ensure_audio_players()
	if track_index < 0 or track_index >= loaded_streams.size():
		return
	if track_index == current_track_index and not force_restart:
		return
		
	var stream = loaded_streams[track_index]
	if stream == null:
		return

	if _gap_timer and not _gap_timer.is_stopped():
		_gap_timer.stop()
		
	current_track_index = track_index
	track_changed.emit(track_index, TRACK_TITLES[track_index])

	# Kill previous crossfade tween to avoid pop/competition
	if _crossfade_tween and _crossfade_tween.is_valid():
		_crossfade_tween.kill()
	
	# Swap active and inactive players
	var temp = active_player
	active_player = inactive_player
	inactive_player = temp
	
	active_player.stream = stream
	active_player.volume_db = MIN_DB
	if active_player.is_inside_tree():
		active_player.play()
	
	_crossfade_tween = create_tween().set_parallel(true)
	_crossfade_tween.tween_property(active_player, "volume_db", TARGET_DB, FADE_DURATION)\
		.set_trans(Tween.TRANS_SINE).set_ease(Tween.EASE_OUT)
	_crossfade_tween.tween_property(inactive_player, "volume_db", MIN_DB, FADE_DURATION)\
		.set_trans(Tween.TRANS_SINE).set_ease(Tween.EASE_IN)
	
	_crossfade_tween.chain().tween_callback(func():
		if is_instance_valid(inactive_player):
			inactive_player.stop()
	)

func switch_to_region(region: UniverseRoute.CosmicRegion) -> void:
	match region:
		UniverseRoute.CosmicRegion.PAPER: play_track(0)
		UniverseRoute.CosmicRegion.INKWASH: play_track(1)
		UniverseRoute.CosmicRegion.FOIL: play_track(2)
		UniverseRoute.CosmicRegion.CORE: play_track(3)
		UniverseRoute.CosmicRegion.ABYSS: play_track(4)
		UniverseRoute.CosmicRegion.DRIFT: play_track(5)

func next_track() -> void:
	var next_idx = (current_track_index + 1) % loaded_streams.size()
	play_track(next_idx)

func prev_track() -> void:
	var prev_idx = (current_track_index - 1 + loaded_streams.size()) % loaded_streams.size()
	play_track(prev_idx)

func _on_player_finished(player: AudioStreamPlayer) -> void:
	if player == active_player and is_instance_valid(_gap_timer):
		_gap_timer.start()

func _on_gap_timer_timeout() -> void:
	next_track()
