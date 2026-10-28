shader_type spatial;
render_mode cull_disabled, diffuse_burley, specular_schlick_ggx;

// ==============================================================================
// STARFIELD // ORIGAMI WASHI PAPERCRAFT SHADER (GODOT 4.3)
// Translucent Washi Paper Subsurface Scattering & Gold Crease Highlights
// ==============================================================================

uniform vec4 paper_color : source_color = vec4(0.95, 0.94, 0.92, 1.0);
uniform vec4 crease_color : source_color = vec4(1.0, 0.85, 0.45, 1.0);
uniform float translucency : hint_range(0.0, 1.0) = 0.45;
uniform float roughness_val : hint_range(0.0, 1.0) = 0.75;
uniform float crease_fresnel_power : hint_range(1.0, 6.0) = 2.8;
uniform float flap_speed : hint_range(0.5, 8.0) = 2.4;
uniform float flap_amplitude : hint_range(0.0, 1.5) = 0.45;

void vertex() {
	// Harmonic wing flapping: wing displacement increases with lateral distance abs(VERTEX.x)
	float wing_dist = abs(VERTEX.x);
	if (wing_dist > 0.05) {
		float flap_cycle = sin(TIME * flap_speed * 6.2831853);
		float weight = clamp((wing_dist - 0.05) / 1.75, 0.0, 1.0);
		VERTEX.y += flap_cycle * flap_amplitude * weight;

		// Dynamically rotate normal with wing slope to maintain realistic highlights
		float slope = flap_cycle * flap_amplitude * (1.0 / 1.75) * sign(VERTEX.x);
		NORMAL = normalize(NORMAL + vec3(0.0, 0.0, -slope * 0.3));
	}
}

void fragment() {
	// Double-sided safety: ensure normal faces camera regardless of polygon winding
	vec3 corrected_normal = FRONT_FACING ? NORMAL : -NORMAL;

	// Base washi paper tone
	ALBEDO = paper_color.rgb;
	ROUGHNESS = roughness_val;
	METALLIC = 0.02;

	// View dependent edge crease fresnel highlight with backface protection
	float rim = pow(1.0 - max(0.0, dot(corrected_normal, VIEW)), crease_fresnel_power);
	EMISSION = crease_color.rgb * rim * 0.9;

	// Backlight translucency (Subsurface Scattering simulation)
	BACKLIGHT = paper_color.rgb * translucency;
}
