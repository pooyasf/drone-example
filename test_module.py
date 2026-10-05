"""Tests for module.py.

Run with: python test_module.py     (uses a tiny inline runner)
Or:       pytest test_module.py     (if pytest is available)

The file is intentionally a single module so future teachers can read it
top-to-bottom alongside module.py. Each test focuses on one invariant.
"""
import inspect
import sys
import numpy as np

sys.path.insert(0, '/Users/claude/projects/dropship')
import module
from module import (
    Drone, PIDController, accel_to_phi_F,
    name_to_int, bits_to_float, state_to_array,
)


# Tolerance used in most numeric comparisons.
TOL = 1e-9


# ---------------------------------------------------------------------------
# Drone physics
# ---------------------------------------------------------------------------

def test_hover_thrust_equals_mg():
    """At V = M*g/2 / amp per motor, total thrust equals M*g and torque is zero."""
    d = Drone(test=True, wind=False)
    V_hover = (d.M * d.g / 2) / d.V_left_amp
    d.set_V(V_hover, V_hover)
    assert abs(d.F - d.M * d.g) < TOL, f"F={d.F}, expected {d.M * d.g}"
    assert abs(d.tau) < TOL


def test_test_mode_has_zero_per_student_variation():
    d = Drone(test=True)
    assert d.V_left_offset == 0
    assert d.V_right_offset == 0
    assert d.V_left_clip_p == 1.0
    assert d.V_right_clip_p == 1.0


def test_named_drone_has_nonzero_variation():
    d = Drone(name='Andreas', wind=False)
    assert d.V_left_offset != 0 or d.V_right_offset != 0


def test_named_drone_is_deterministic():
    d1 = Drone(name='Andreas', wind=False)
    d2 = Drone(name='Andreas', wind=False)
    assert d1.V_left_offset == d2.V_left_offset
    assert d1.V_right_offset == d2.V_right_offset
    assert d1.V_left_clip_p == d2.V_left_clip_p


def test_free_fall_dz_is_minus_g_per_dt():
    """With V = 0, drag = 0, no wind: after one step dz ~= -g * dt."""
    d = Drone(test=True, wind=False, drag_t=0, drag_r=0)
    d.set_V(0, 0)
    state = d.update()
    expected = -d.g * d.deltaT
    assert abs(state.dz - expected) < 1e-3, f"dz={state.dz}, expected {expected}"


def test_no_negative_motor_thrust_at_zero_throttle():
    """At V_left = V_right = 0, every named drone should have F_left, F_right >= 0.

    Pre-fix the per-student offsets can leave a small negative residual
    thrust, which is unphysical for single-direction motors. Post-fix
    the motor model clamps F_motor to >= 0.
    """
    for name in ['Andreas', 'Bob', 'Sander', 'Conor', 'Eve', 'Dana', 'Mira']:
        d = Drone(name=name, wind=False)
        d.set_V(0, 0)
        assert d.F_left  >= 0, f"{name}: F_left = {d.F_left}"
        assert d.F_right >= 0, f"{name}: F_right = {d.F_right}"


def test_pos_and_vel_are_stable_views():
    """drone.pos and drone.vel must keep pointing at the same memory across update().

    Pre-fix solve_state is reassigned in update() and pos/vel become stale.
    Post-fix solve_state is written in-place and the views stay valid.
    """
    d = Drone(test=True, wind=False)
    pos_ref = d.pos
    vel_ref = d.vel
    d.set_V(0.5, 0.5)
    d.update()
    assert pos_ref is d.pos, "drone.pos was reassigned across update()"
    assert vel_ref is d.vel, "drone.vel was reassigned across update()"


def test_boundary_clipping_works_for_offset_range():
    """flight_range that does not straddle zero should still keep the drone inside.

    Pre-fix the boundary clip uses ``0.999 * range[edge]`` which only points
    inward when range straddles zero. Post-fix the clip is a small
    fraction of the range width, so it works for any range.
    """
    d = Drone(test=True, wind=False, flight_range=(1, 1, 5, 5))

    # Push past lower y bound.
    d.solve_state[0] = 0.5
    d.solve_state[1] = 3.0
    d.set_state()
    assert 1.0 <= d.solve_state[0] <= 5.0, f"y after clip = {d.solve_state[0]}"

    # Push past upper y bound.
    d.solve_state[0] = 10.0
    d.set_state()
    assert 1.0 <= d.solve_state[0] <= 5.0, f"y after clip = {d.solve_state[0]}"


def test_dx_returns_ndarray():
    """The state-derivative function should return a numpy array, not a list."""
    d = Drone(test=True, wind=False)
    out = d.dx(0.0, np.zeros(6), F=0.0, tau=0.0)
    assert isinstance(out, np.ndarray), f"dx returned a {type(out).__name__}"


# ---------------------------------------------------------------------------
# Target detection
# ---------------------------------------------------------------------------

def test_target_at_centre_is_hit():
    d = Drone(test=True, wind=False)
    d.set_targets(np.array([[0.5, 0.5, 0.1]]))
    d.solve_state[0] = 0.5
    d.solve_state[1] = 0.5
    d.set_state()
    assert d.target_idx == 1


def test_target_far_outside_is_missed():
    d = Drone(test=True, wind=False)
    d.set_targets(np.array([[0.0, 0.0, 0.1]]))
    d.solve_state[0] = 0.3
    d.solve_state[1] = 0.0
    d.set_state()
    assert d.target_idx == 0


def test_target_corner_of_square_does_not_register():
    """Drone at (0.99 r, 0.99 r) sits inside the old square detection box but
    OUTSIDE a Euclidean circle of radius r. Post-fix it should not register
    a hit, so the visible red disc and the actual detection agree."""
    d = Drone(test=True, wind=False)
    r = 0.1
    d.set_targets(np.array([[0.0, 0.0, r]]))
    d.solve_state[0] = 0.99 * r
    d.solve_state[1] = 0.99 * r
    d.set_state()
    # Euclidean distance is r * sqrt(2) ~= 1.4 r, well outside the circle.
    assert d.target_idx == 0, "corner of old square box should not count anymore"


def test_target_just_inside_circle_registers():
    """Drone at (0.7 r, 0) sits well inside the circle; should register."""
    d = Drone(test=True, wind=False)
    r = 0.1
    d.set_targets(np.array([[0.0, 0.0, r]]))
    d.solve_state[0] = 0.7 * r
    d.solve_state[1] = 0.0
    d.set_state()
    assert d.target_idx == 1


def test_set_targets_raises_value_error():
    """set_targets should raise ValueError (not AssertionError) on bad input
    so the check survives ``python -O``."""
    d = Drone(test=True)
    try:
        d.set_targets(42)
    except ValueError:
        pass
    except Exception as e:
        raise AssertionError(f"set_targets(42) raised {type(e).__name__}, expected ValueError")
    else:
        raise AssertionError("set_targets(42) did not raise")

    try:
        d.set_targets(np.array([1.0, 2.0, 3.0]))  # 1D, not (N, 3)
    except ValueError:
        pass
    except Exception as e:
        raise AssertionError(f"set_targets(1D) raised {type(e).__name__}, expected ValueError")
    else:
        raise AssertionError("set_targets(1D) did not raise")


# ---------------------------------------------------------------------------
# PIDController
# ---------------------------------------------------------------------------

def test_pid_proportional_only():
    c = PIDController(Kp=2.0, Ki=0, Kd=0)
    out = c(value=3.0, value_dot=0.0, setpoint=1.0)  # err = 2
    assert abs(out - 4.0) < TOL


def test_pid_derivative_only():
    c = PIDController(Kp=0, Ki=0, Kd=3.0)
    out = c(value=0.0, value_dot=2.0, setpoint=0.0)
    assert abs(out - 6.0) < TOL


def test_pid_setpoint_dot_cancels_matched_velocity():
    """If value_dot equals setpoint_dot, the Kd contribution is zero."""
    c = PIDController(Kp=0, Ki=0, Kd=10.0)
    out = c(value=0.0, value_dot=5.0, setpoint=0.0, setpoint_dot=5.0)
    assert abs(out) < TOL


def test_pid_integrator_accumulates_and_clamps():
    c = PIDController(Kp=0, Ki=1.0, Kd=0, deltaT=1.0, int_clamp=10)
    for _ in range(100):
        c(value=1.0, value_dot=0.0, setpoint=0.0)
    assert c.integral == 10.0


def test_pid_reset_zeroes_integral():
    c = PIDController(Kp=0, Ki=1.0, Kd=0)
    for _ in range(60):
        c(value=1.0, value_dot=0.0, setpoint=0.0)
    assert c.integral != 0
    c.reset()
    assert c.integral == 0


def test_pid_deltaT_default_matches_drone():
    """PIDController and Drone share the simulation step."""
    d = Drone(test=True)
    c = PIDController(Kp=1, Ki=1, Kd=1)
    assert c.deltaT == d.deltaT


def test_shared_delta_t_constant():
    """Both Drone and PIDController take their default step from module.DELTA_T."""
    assert hasattr(module, 'DELTA_T')
    d = Drone(test=True)
    c = PIDController(Kp=0, Ki=0, Kd=0)
    assert d.deltaT == module.DELTA_T
    assert c.deltaT == module.DELTA_T


def test_wind_attributes_named_a_wind():
    """Wind disturbance is stored as accelerations a_wind_y, a_wind_z."""
    d = Drone(test=True, wind=False)
    assert hasattr(d, 'a_wind_y')
    assert hasattr(d, 'a_wind_z')
    assert not hasattr(d, 'F_wind_y')
    assert not hasattr(d, 'F_wind_z')


def test_set_V_args_have_no_leading_underscore():
    """Drone.set_V's argument names are V_left / V_right (no underscore prefix)."""
    sig = inspect.signature(Drone.set_V)
    params = list(sig.parameters.keys())
    assert 'V_left' in params
    assert 'V_right' in params
    assert '_V_left' not in params


def test_perlin_methods_are_snake_case():
    """Perlin's public methods follow PEP 8 (snake_case)."""
    p = module.Perlin()
    for name in ('smooth', 'perlin_1d', 'sum', 'lerp'):
        assert hasattr(p, name), f"Perlin missing {name}"
    # Old CamelCase names should be gone.
    for old in ('Smooth', 'Perlin1D', 'Sum'):
        assert not hasattr(p, old), f"Perlin still has {old}"


# ---------------------------------------------------------------------------
# accel_to_phi_F
# ---------------------------------------------------------------------------

def test_accel_to_phi_F_hover():
    phi, F = accel_to_phi_F(0.0, 0.0)
    assert abs(phi) < TOL
    assert abs(F - Drone.CF_M * Drone.CF_G) < TOL


def test_accel_to_phi_F_round_trip():
    """Applying the EOM to (phi, F) should recover (a_y, a_z)."""
    M, g = Drone.CF_M, Drone.CF_G
    for a_y, a_z in [(0, 0), (1, 0), (0, 1), (-2, 3), (5, -2), (-3, -3)]:
        phi, F = accel_to_phi_F(a_y, a_z, M=M, g=g)
        a_y_back = -np.sin(phi) * F / M
        a_z_back =  np.cos(phi) * F / M - g
        assert abs(a_y_back - a_y) < 1e-9, f"(a_y={a_y}): got {a_y_back}"
        assert abs(a_z_back - a_z) < 1e-9, f"(a_z={a_z}): got {a_z_back}"


def test_accel_to_phi_F_defaults_match_crazyflie():
    sig = inspect.signature(accel_to_phi_F)
    assert sig.parameters['M'].default == Drone.CF_M
    assert sig.parameters['g'].default == Drone.CF_G


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def test_name_to_int_is_deterministic():
    assert name_to_int('Andreas') == name_to_int('Andreas')


def test_name_to_int_distinguishes_names():
    assert name_to_int('Andreas') != name_to_int('Bob')


def test_bits_to_float_within_range():
    for key in [0, 7, 15, 0xff00, 0xffffffff]:
        v = bits_to_float(key, 0, 3, 1.0)
        assert -1.0 <= v <= 1.0


def test_state_to_array_length():
    d = Drone(test=True, wind=False)
    d.set_V(0.5, 0.5)
    s = d.update()
    arr = state_to_array(s)
    assert arr.shape == (12,), f"state_to_array shape = {arr.shape}"


# ---------------------------------------------------------------------------
# Tiny test runner (so the file works without pytest installed)
# ---------------------------------------------------------------------------

def _run():
    tests = [
        (name, obj) for name, obj in globals().items()
        if name.startswith('test_') and callable(obj)
    ]
    failed = []
    for name, fn in tests:
        try:
            fn()
        except AssertionError as e:
            failed.append((name, str(e)))
            print(f"FAIL  {name}: {e}")
        except Exception as e:
            failed.append((name, f"{type(e).__name__}: {e}"))
            print(f"ERROR {name}: {type(e).__name__}: {e}")
        else:
            print(f"ok    {name}")
    print(f"\n{len(tests) - len(failed)} / {len(tests)} passed")
    return 0 if not failed else 1


if __name__ == '__main__':
    sys.exit(_run())
