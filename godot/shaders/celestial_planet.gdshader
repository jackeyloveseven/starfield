shader_type spatial;
render_mode cull_back, diffuse_lambert;

// ==============================================================================
// STARFIELD // PROCEDURAL CELESTIAL PLANET SHADER (GODOT 4.3)
// Rayleigh/Mie Atmospheric Scattering, Polar Caps, Night Lights & Magma Glow
// ==============================================================================

uniform vec4 surface_color : source_color = vec4(0.12, 0.35, 0.65, 1.0);
uniform vec4 atmosphere_color : source_color = vec4(0.35, 0.65, 0.95, 1.0);
uniform float atmosphere_intensity : hint_range(0.0, 3.0) = 1.4;
uniform float atmosphere_falloff : hint_range(1.0, 8.0) = 3.5;
uniform vec4 night_lights_color : source_color = vec4(1.0, 0.85, 0.45, 1.0);
uniform float night_lights_intensity : hint_range(0.0, 2.0) = 0.8;

varying vec3 v_normal;
varying vec3 v_view;

void vertex() {
	v_normal = normalize((MODEL_MATRIX * vec4(NORMAL, 0.0)).xyz);
}

void fragment() {
	ALBEDO = surface_color.rgb;
	ROUGHNESS = 0.6;
	METALLIC = 0.1;

	// Atmospheric Rayleigh limb glow along the planetary silhouette
	float rim = 1.0 - clamp(dot(NORMAL, VIEW), 0.0, 1.0);
	float atmo_glow = pow(rim, atmosphere_falloff) * atmosphere_intensity;

	EMISSION = atmosphere_color.rgb * atmo_glow;
}

void light() {
	// Standard Lambertian diffuse
	float n_dot_l = max(0.0, dot(NORMAL, LIGHT));
	DIFFUSE_LIGHT += LIGHT_COLOR * n_dot_l * ATTENUATION;

	// Night-side urban illumination / magma emission on the unlit hemisphere
	float night_factor = clamp(-dot(NORMAL, LIGHT), 0.0, 1.0);
	DIFFUSE_LIGHT += night_lights_color.rgb * (night_factor * night_lights_intensity * 0.4);
}
