class_name UniverseRoute
extends RefCounted

# ==============================================================================
# STARFIELD // UNIVERSE CORRIDOR & REGION TRANSITION ENGINE (GODOT 4.3)
# Analytical route equations, 6 full cosmic regions & smooth transition factors
# ==============================================================================

enum CosmicRegion {
	PAPER = 0,     # 素纸: 清雅灰白与深墨微蓝 (Track 1)
	INKWASH = 1,   # 墨海: 浓郁水墨晕染与深渊墨蓝 (Track 2)
	FOIL = 2,      # 箔野: 暖金箔反光与暮光金辉 (Track 3)
	CORE = 3,      # 星核: 炽热等离子体与高能日冕紫 (Track 4)
	ABYSS = 4,     # 深渊: 极暗黑洞视界与零重力虚空 (Track 5)
	DRIFT = 5      # 雪境: 冰穹低语与晶化以太流 (Track 6)
}

const REGION_LENGTH: float = 15000.0
const TRANSITION_ZONE: float = 3700.0

static func get_route_x(z: float) -> float:
	var s1 = sin(z * 0.00018) * 420.0
	var s2 = cos(z * 0.00045) * 180.0
	var s3 = sin(z * 0.00120) * 60.0
	return s1 + s2 + s3

static func get_route_y(z: float) -> float:
	return sin(z * 0.00022) * 120.0 + cos(z * 0.00065) * 45.0

# Analytical machine-precision derivative
static func get_route_heading(z: float) -> Vector3:
	var dx = 0.0756 * cos(z * 0.00018) - 0.081 * sin(z * 0.00045) + 0.072 * cos(z * 0.00120)
	var dy = 0.0264 * cos(z * 0.00022) - 0.02925 * sin(z * 0.00065)
	return Vector3(dx, dy, 1.0).normalized()

static func get_region(z: float) -> CosmicRegion:
	var idx = int(floor(posmod(z, REGION_LENGTH * 6.0) / REGION_LENGTH))
	return idx as CosmicRegion

static func get_transition_factor(z: float) -> float:
	var local_z = fposmod(z, REGION_LENGTH)
	var start_zone = REGION_LENGTH - TRANSITION_ZONE
	if local_z < start_zone:
		return 0.0
	return smoothstep(0.0, 1.0, (local_z - start_zone) / TRANSITION_ZONE)

static func get_region_name(region: CosmicRegion) -> String:
	match region:
		CosmicRegion.PAPER: return "素纸 · REGION 01"
		CosmicRegion.INKWASH: return "墨海 · REGION 02"
		CosmicRegion.FOIL: return "箔野 · REGION 03"
		CosmicRegion.CORE: return "星核 · REGION 04"
		CosmicRegion.ABYSS: return "深渊 · REGION 05"
		CosmicRegion.DRIFT: return "雪境 · REGION 06"
		_: return "深空走廊"

static func get_region_theme_color(region: CosmicRegion) -> Color:
	match region:
		CosmicRegion.PAPER: return Color(0.92, 0.94, 0.96)
		CosmicRegion.INKWASH: return Color(0.05, 0.12, 0.22)
		CosmicRegion.FOIL: return Color(0.98, 0.82, 0.35)
		CosmicRegion.CORE: return Color(0.65, 0.42, 0.95)
		CosmicRegion.ABYSS: return Color(0.02, 0.03, 0.06)
		CosmicRegion.DRIFT: return Color(0.72, 0.88, 0.98)
		_: return Color.WHITE
