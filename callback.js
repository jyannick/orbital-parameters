const a = sma.value,
  e = eccentricity.value,
  p = a * (1 - e * e),
  omega = (aop.value * window.Math.PI) / 180,
  inc = (inclination.value * window.Math.PI) / 180,
  Gomega = (raan.value * window.Math.PI) / 180,
  mu = 3.986004418e14,
  earth_radius = 6378,
  anomaly_index = window.Math.round((anomaly.value / 360) * N),
  x_shape = orbit_shape.data["x"],
  y_shape = orbit_shape.data["y"],
  x_sat_in_orbital_plane = position_in_orbital_plane.data["x"],
  y_sat_in_orbital_plane = position_in_orbital_plane.data["y"],
  x_sat = position_3d.data["x"],
  y_sat = position_3d.data["y"],
  z_sat = position_3d.data["z"],
  x = orbit_3d.data["x"],
  y = orbit_3d.data["y"],
  z = orbit_3d.data["z"],
  x_apsides_in_orbital_plane = apsides_in_orbital_plane.data["x"],
  y_apsides_in_orbital_plane = apsides_in_orbital_plane.data["y"];

let cos_omega = window.Math.cos(omega);
let sin_omega = window.Math.sin(omega);
let cos_Gomega = window.Math.cos(Gomega);
let sin_Gomega = window.Math.sin(Gomega);
let cos_i = window.Math.cos(inc);
let sin_i = window.Math.sin(inc);

for (let i = 0; i < N; i++) {
  let v = (i / (N - 1)) * 2 * window.Math.PI;
  let cos_v = window.Math.cos(v);
  let sin_v = window.Math.sin(v);
  let r = p / (1 + e * cos_v);

  x_shape[i] = r * cos_omega * cos_v - r * sin_omega * sin_v;
  y_shape[i] = r * sin_omega * cos_v + r * cos_omega * sin_v;

  let x_incli_only = -x_shape[i];
  let y_incli_only = -y_shape[i] * cos_i;
  let z_incli_only = y_shape[i] * sin_i;

  x[i] = x_incli_only * cos_Gomega - y_incli_only * sin_Gomega;
  y[i] = x_incli_only * sin_Gomega + y_incli_only * cos_Gomega;
  z[i] = z_incli_only;
}

x_apsides_in_orbital_plane[0] = a * (1 - e) * cos_omega;
y_apsides_in_orbital_plane[0] = a * (1 - e) * sin_omega;
x_apsides_in_orbital_plane[1] = -a * (1 + e) * cos_omega;
y_apsides_in_orbital_plane[1] = -a * (1 + e) * sin_omega;

x_sat_in_orbital_plane[0] = x_shape[anomaly_index];
y_sat_in_orbital_plane[0] = y_shape[anomaly_index];
x_sat[0] = x[anomaly_index];
y_sat[0] = y[anomaly_index];
z_sat[0] = z[anomaly_index];

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
