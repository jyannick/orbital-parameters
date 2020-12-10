const a = sma.value,
  e = eccentricity.value,
  p = a * (1 - e * e),
  omega = (aop.value * window.Math.PI) / 180,
  inc = (inclination.value * window.Math.PI) / 180,
  Gomega = (raan.value * window.Math.PI) / 180,
  mu = 3.986004418e14,
  earth_radius = 6378,
  x_shape_array = orbit_shape.data["x"],
  y_shape_array = orbit_shape.data["y"],
  x_sat_in_orbital_plane = position_in_orbital_plane.data["x"],
  y_sat_in_orbital_plane = position_in_orbital_plane.data["y"],
  x_sat = position_3d.data["x"],
  y_sat = position_3d.data["y"],
  z_sat = position_3d.data["z"],
  x_array = orbit_3d.data["x"],
  y_array = orbit_3d.data["y"],
  z_array = orbit_3d.data["z"],
  x_apsides_in_orbital_plane = apsides_in_orbital_plane.data["x"],
  y_apsides_in_orbital_plane = apsides_in_orbital_plane.data["y"];

let cos_omega = window.Math.cos(omega);
let sin_omega = window.Math.sin(omega);
let cos_Gomega = window.Math.cos(Gomega);
let sin_Gomega = window.Math.sin(Gomega);
let cos_i = window.Math.cos(inc);
let sin_i = window.Math.sin(inc);

function compute_orbit(v) {
  let cos_v = window.Math.cos(v);
  let sin_v = window.Math.sin(v);
  let r = p / (1 + e * cos_v);

  let x_shape = r * cos_omega * cos_v - r * sin_omega * sin_v;
  let y_shape = r * sin_omega * cos_v + r * cos_omega * sin_v;

  let x_incli_only = -x_shape;
  let y_incli_only = -y_shape * cos_i;
  let z_incli_only = y_shape * sin_i;

  let x = x_incli_only * cos_Gomega - y_incli_only * sin_Gomega;
  let y = x_incli_only * sin_Gomega + y_incli_only * cos_Gomega;
  let z = z_incli_only;
  return {
    x_shape,
    y_shape,
    x,
    y,
    z,
  };
}

for (let i = 0; i < N; i++) {
  let v = (i / (N - 1)) * 2 * window.Math.PI;
  let results = compute_orbit(v);
  x_shape_array[i] = results.x_shape;
  y_shape_array[i] = results.y_shape;
  x_array[i] = results.x;
  y_array[i] = results.y;
  z_array[i] = results.z;
}

x_apsides_in_orbital_plane[0] = a * (1 - e) * cos_omega;
y_apsides_in_orbital_plane[0] = a * (1 - e) * sin_omega;
x_apsides_in_orbital_plane[1] = -a * (1 + e) * cos_omega;
y_apsides_in_orbital_plane[1] = -a * (1 + e) * sin_omega;

let sat_results = compute_orbit((anomaly.value * window.Math.PI) / 180);
x_sat_in_orbital_plane[0] = sat_results.x_shape;
y_sat_in_orbital_plane[0] = sat_results.y_shape;
x_sat[0] = sat_results.x;
y_sat[0] = sat_results.y;
z_sat[0] = sat_results.z;

orbit_shape.change.emit();
orbit_3d.change.emit();
position_in_orbital_plane.change.emit();
position_3d.change.emit();
apsides_in_orbital_plane.change.emit();

let orbital_period_hours =
  (2 * window.Math.PI * window.Math.sqrt((a * 1000) ** 3 / mu)) / 3600;
let apogee_altitude = a * (1 + e) - earth_radius;
let perigee_altitude = a * (1 - e) - earth_radius;

orbit_description_div.text = `
        <h2>Orbital Data</h2>
        <ul>
            <li>Orbital period: ${orbital_period_hours.toFixed(3)} hours</li>
            <li>Apogee altitude: ${apogee_altitude.toFixed(0)} kilometers</li>
            <li>Perigee altitude: ${perigee_altitude.toFixed(0)} kilometers</li>
        </ul>`;
