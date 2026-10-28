shader_type spatial;
render_mode blend_mix, depth_draw_never, cull_disabled, unshaded;

// ==============================================================================
// STARFIELD // SCHWARZSCHILD NULL GEODESIC BLACK HOLE SHADER (GODOT 4.3)
// 100% Mathematical Parity with the WebGL & HLSL Relativistic Raymarcher
// Accelerated with Ray-Sphere Bounding Early-Hit & Radial Feathering
// ==============================================================================

uniform float horizon_radius : hint_range(0.1, 50.0) = 2.5;
uniform float accretion_inner : hint_range(1.0, 4.0) = 2.16;
uniform float accretion_outer : hint_range(3.0, 10.0) = 5.6;
uniform vec4 disk_emission : source_color = vec4(1.0, 0.78, 0.35, 1.0);
uniform float doppler_strength : hint_range(0.0, 1.0) = 0.65;
uniform int max_steps : hint_range(32, 256) = 96;
uniform float step_scale : hint_range(0.01, 0.2) = 0.08;

varying vec3 v_world_pos;

void vertex() {
	v_world_pos = (MODEL_MATRIX * vec4(VERTEX, 1.0)).xyz;
}

// Ray-Sphere intersection for skipping 2000+ units of empty space
bool intersect_bounding_sphere(vec3 ro, vec3 rd, float radius, out float t_hit) {
	float b = dot(ro, rd);
	float c = dot(ro, ro) - radius * radius;
	float h = b * b - c;
	if (h < 0.0) return false;
	h = sqrt(h);
	t_hit = -b - h;
	return true;
}

void fragment() {
	highp vec3 cam_pos = (INV_VIEW_MATRIX * vec4(0.0, 0.0, 0.0, 1.0)).xyz;
	highp vec3 ray_dir = normalize(v_world_pos - cam_pos);
	highp vec3 bh_center = (MODEL_MATRIX * vec4(0.0, 0.0, 0.0, 1.0)).xyz;

	highp float rs = max(0.001, horizon_radius);
	highp float r_in = rs * accretion_inner;
	highp float r_out = rs * accretion_outer;
	highp float r_bound = r_out * 3.5;

	highp vec3 rel_cam = cam_pos - bh_center;
	highp float t_entry;

	// 1. Skip outer void if ray misses black hole bounding sphere
	if (!intersect_bounding_sphere(rel_cam, ray_dir, r_bound, t_entry)) {
		discard;
	}

	// Advance ray directly to outer bounding sphere surface
	highp vec3 pos = rel_cam + ray_dir * max(0.0, t_entry);
	highp vec3 vel = ray_dir;

	vec3 accum_color = vec3(0.0);
	float optical_depth = 0.0;
	float prev_y = pos.y;

	// 2. High-precision Symplectic Integrator (Velocity Verlet)
	for (int step = 0; step < max_steps; ++step) {
		highp float r = length(pos);

		// Event Horizon Singularity (absorb remaining background rays without erasing foreground disk)
		if (r <= rs * 1.02) {
			optical_depth = 1.0;
			break;
		}

		// Escaped bounding sphere safely
		if (r > r_bound && dot(pos, vel) > 0.0) {
			break;
		}

		highp float step_dt = clamp((r - rs) * step_scale, 0.02, 0.75);

		// FP16-safe Symplectic Acceleration: a = -1.5 * rs * h^2 / r^5 * pos
		highp vec3 h_vec = cross(pos, vel);
		highp float h2 = dot(h_vec, h_vec);
		highp float inv_r = 1.0 / max(0.001, r);
		highp float inv_r2 = inv_r * inv_r;
		highp float inv_r5 = inv_r2 * inv_r2 * inv_r;
		highp vec3 accel = (-1.5 * rs * h2 * inv_r5) * pos;

		vel += accel * (0.5 * step_dt);
		pos += vel * step_dt;

		highp float r_new = length(pos);
		highp vec3 h_new = cross(pos, vel);
		highp float inv_rn = 1.0 / max(0.001, r_new);
		highp float inv_rn2 = inv_rn * inv_rn;
		highp float inv_rn5 = inv_rn2 * inv_rn2 * inv_rn;
		highp vec3 accel_new = (-1.5 * rs * dot(h_new, h_new) * inv_rn5) * pos;
		vel += accel_new * (0.5 * step_dt);
		vel = normalize(vel);

		// 3. Equatorial Accretion Disk Crossing (y = 0 plane)
		if ((prev_y > 0.0 && pos.y <= 0.0) || (prev_y < 0.0 && pos.y >= 0.0)) {
			float t_interp = -prev_y / (pos.y - prev_y + 1e-6);
			vec3 cross_pos = pos - vel * (step_dt * (1.0 - t_interp));
			float cross_r = length(cross_pos.xz);

			if (cross_r >= r_in && cross_r <= r_out) {
				float u_r = (cross_r - r_in) / (r_out - r_in);
				float profile = sin(u_r * 3.1415926) * (1.0 - u_r * 0.35);

				// Keplerian orbital velocity for Doppler beaming
				vec3 v_disk = normalize(vec3(-cross_pos.z, 0.0, cross_pos.x));
				float doppler_cos = dot(v_disk, -vel);
				float doppler_factor = pow(max(0.1, 1.0 + doppler_cos * doppler_strength), 3.2);

				// Smooth procedural accretion swirl
				float angle = atan(cross_pos.z, cross_pos.x);
				float swirl = sin(angle * 3.0 + cross_r * 2.2 + TIME * 0.5) * 0.3 + 0.7;

				vec3 emission = disk_emission.rgb * (profile * swirl * doppler_factor * 3.0);
				float disk_alpha = clamp(profile * 0.85, 0.0, 1.0);

				accum_color += emission * (1.0 - optical_depth);
				optical_depth += disk_alpha * (1.0 - optical_depth);

				if (optical_depth >= 0.98) {
					break;
				}
			}
		}

		prev_y = pos.y;
	}

	// 4. Eliminate square QuadMesh border with smooth radial feathering
	float quad_radial = length(UV * 2.0 - 1.0);
	float edge_feather = smoothstep(1.0, 0.80, quad_radial);

	ALBEDO = accum_color * edge_feather;
	ALPHA = clamp(optical_depth * edge_feather, 0.0, 1.0);
}
