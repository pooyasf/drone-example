# Drone parameters
Andreas Freise 26.05.2026

The simulator's drone is a 2D slice (y, z, phi) of a Crazyflie 2.1. Physical parameters are matched to the high-fidelity Simulink model described in:

> Richardson, L. and Pretorius, A., *Development of a high-fidelity simulation environment for a Crazyflie 2.1 quadcopter*, MATEC Web of Conferences 417, 04007 (2025). [DOI: 10.1051/matecconf/202541704007](https://doi.org/10.1051/matecconf/202541704007).

## Physical parameters used in `module.py`

* `M = 0.032` kg, drone mass.
* `Ixx = 16.57e-6` kg m², roll inertia. The 2D slice ignores pitch and yaw.
* `L_arm = 0.0325` m, perpendicular distance from the centre of gravity to each motor pair.
* `g = 9.8` m/s², gravity.
* `F_max = 0.296` N per 2D motor, equal to `2 * 0.148` N from the Crazyflie specification (a 2D motor here represents one pair of real rotors).
* `V_min = 0`, `V_max = 1`, per-motor throttle range. The motors are single-direction.
* `drag_t = 4` 1/s, linear drag coefficient. The drag force on each axis is `-drag_t * velocity`.
* `drag_r = 5` 1/s, angular drag coefficient. The drag torque is `-drag_r * omega`.

## Calibrated constants (measured by `student2`)

These are not stored anywhere in `module.py`. They are the values a student reads off the system-identification sweep in `student2`, and they depend on the per-student randomisation seeded by the student's name.

* `V_hover`, per-motor throttle that produces `M * g / 2` of thrust. About 0.5 with a per-student range about ±0.01 throttle.
* `V_left_offset`, residual left and right asymmetry, applied inside the motor mixer. This has a per-student range about ±0.01.

The Crazyflie firmware's outer-loop saturation values (±1 m/s on commanded velocity and ±20° on commanded tilt) are imported as the default `v_max_cmd` and `tilt_max` in the velocity-cascade notebooks. Section 3 of the Richardson et al. paper has the firmware block diagram to match.

## Where each parameter comes from

### Direct from the Richardson et al. paper, Table 1

* `CF_M = 0.032` kg, the published Crazyflie 2.1 mass (Table 1, ref. [8] in the paper).
* `CF_IXX = 16.57e-6` kg m², the (1,1) entry of the inertia matrix `J` in Table 1 (the paper gives 16.57171e-6; we round).
* `CF_G = 9.8` m/s², the Cape Town value the paper uses in its text after equation (11).

### Derived from the paper

* `CF_L_ARM = 0.0325` m. The paper lists "adjacent motor distance d = 0.065 m" in Table 1. In our 2D model one motor on each side stands in for a pair of real rotors, so the moment arm is `d / 2 = 0.0325` m.
* `CF_F_MAX_MOTOR = 0.296` N per 2D motor (= `2 × 0.148` N). The per-real-motor max thrust of 0.148 N comes out of the paper's thrust coefficient `k_t = 2.879933e-8` times the maximum propeller angular velocity from the PWM mapping. We double it because each of our two motors represents a pair of real rotors.

### From the Crazyflie firmware (paper Section 3, Table 2, Figure 3)

* `v_max_cmd = 1.0` m/s, outer-loop commanded-velocity saturation.
* `tilt_max = 20°`, commanded-tilt saturation produced by the position-then-velocity cascade.

### Our own choices, not from the paper

* `drag_t = 4.0` 1/s. Chosen so the terminal forward-flight velocity at full tilt is roughly 3 m/s, matching the Bitcraze datasheet for the real platform. The paper itself only models propeller drag torque, not body air drag.
* `drag_r = 5.0` 1/s. Empirical, so the roll rate at full motor differential is plausible for a small drone.
* `thrust_factor = 1.0` default. A scaling parameter added so users can crank thrust-to-weight up for a snappier sim (e.g. `thrust_factor = 2` or `3`). `1.0` matches the real Crazyflie.
* `deltaT = 1/60` s. 60 Hz simulation step, matching typical display refresh. The paper uses 100 Hz (position / velocity) and 500 Hz (attitude / rate) on the real Crazyflie.
* `flight_range = (-3, -3, 3, 3)` m. Arbitrary sized box, similar to an possible area at Nikhef.
* Throttle range `V_min = 0, V_max = 1`. Our convention. The Crazyflie firmware uses a 16-bit unsigned PWM value internally.
* Per-student variation, set in `Drone.__init__` from a hash of the student's name string:
  * motor force offset `± 0.003` N (about 2% of per-motor hover thrust),
  * upper-clip variation `± 0.05` throttle (about 5% of nominal).
  These are purely pedagogical, so each student calibrates a slightly different drone.

