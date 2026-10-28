class_name CelestialDeck
extends RefCounted

# ==============================================================================
# STARFIELD // 280-CARD CELESTIAL DECK & ENCOUNTER ENGINE (GODOT 4.3)
# 4 Shapes x 7 Kinds x 10 Expressions = 280 Distinct Combinatorial Planets
# ==============================================================================

enum Shape { SPHERE = 0, RINGED = 1, OBLATE = 2, FRACTURED = 3 }
enum Kind  { OCEAN = 0, LAVA = 1, FOREST = 2, CITY = 3, ICE = 4, SAND = 5, GAS = 6 }
enum Expr  { STANDARD = 0, SKIM_WATER = 1, MOTHERSHIP = 2, PSIONIC = 3, ZERG = 4, EARTH = 5, CYBER = 6, DUNE = 7, CATACLYSM = 8, SUPERSTORM = 9 }

class CelestialCard:
	var id: String
	var name: String
	var shape: Shape
	var kind: Kind
	var expression: Expr
	var base_radius: float
	var surface_color: Color
	var atmosphere_color: Color
	var axial_tilt: float
	var rotation_speed: float
	var has_rings: bool

var _draw_pile: Array[CelestialCard] = []
var _discard_pile: Array[CelestialCard] = []
var _rng: RandomNumberGenerator = RandomNumberGenerator.new()

func _init(seed_val: int = 0x1A2B) -> void:
	_rng.seed = seed_val
	build_deck()
	shuffle()

func build_deck() -> void:
	_draw_pile.clear()
	var id_counter = 1
	var kind_names = ["海", "熔火", "林", "城", "冰", "沙", "气"]
	var shape_prefix = ["环球", "带环", "扁极", "碎核"]

	for s in range(4):
		for k in range(7):
			for e in range(10):
				var card = CelestialCard.new()
				card.id = "celestial_%03d" % id_counter
				card.name = "%s · %s之星 #%d" % [shape_prefix[s], kind_names[k], id_counter]
				card.shape = s as Shape
				card.kind = k as Kind
				card.expression = e as Expr
				card.base_radius = _rng.randf_range(180.0, 650.0)
				card.axial_tilt = _rng.randf_range(-28.0, 28.0)
				card.rotation_speed = _rng.randf_range(4.0, 18.0)
				card.has_rings = (s == 1 or _rng.randf() < 0.25)

				match card.kind:
					Kind.OCEAN:
						card.surface_color = Color(0.08, 0.28, 0.55)
						card.atmosphere_color = Color(0.35, 0.65, 0.95)
					Kind.LAVA:
						card.surface_color = Color(0.65, 0.18, 0.08)
						card.atmosphere_color = Color(0.95, 0.45, 0.15)
					Kind.FOREST:
						card.surface_color = Color(0.12, 0.45, 0.22)
						card.atmosphere_color = Color(0.45, 0.85, 0.45)
					Kind.CITY:
						card.surface_color = Color(0.20, 0.22, 0.32)
						card.atmosphere_color = Color(0.95, 0.85, 0.45)
					Kind.ICE:
						card.surface_color = Color(0.75, 0.88, 0.95)
						card.atmosphere_color = Color(0.85, 0.95, 1.00)
					Kind.SAND:
						card.surface_color = Color(0.72, 0.55, 0.28)
						card.atmosphere_color = Color(0.95, 0.75, 0.40)
					Kind.GAS:
						card.surface_color = Color(0.55, 0.35, 0.65)
						card.atmosphere_color = Color(0.75, 0.55, 0.95)

				if e == Expr.EARTH:
					card.name = "蔚蓝原乡 · 地球 (Terra)"
					card.surface_color = Color(0.15, 0.38, 0.68)
					card.atmosphere_color = Color(0.45, 0.75, 1.0)

				_draw_pile.append(card)
				id_counter += 1

func shuffle() -> void:
	var n = _draw_pile.size()
	while n > 1:
		n -= 1
		var k = _rng.randi_range(0, n)
		var tmp = _draw_pile[k]
		_draw_pile[k] = _draw_pile[n]
		_draw_pile[n] = tmp

func draw_card() -> CelestialCard:
	if _draw_pile.is_empty():
		_draw_pile.append_array(_discard_pile)
		_discard_pile.clear()
		shuffle()
	var card = _draw_pile.pop_front()
	_discard_pile.append(card)
	return card
