# Topical Lectures

Andreas Freise 27.05.2026

Hands-on material for a control-systems lecture. Students learn the basics of feedback control by flying a virtual 2D drone, working entirely inside Jupyter notebooks. 

This first version of this code was developed for teaching in undergraduate courses and PhD summer schools in Birmingham. An updated version of used used during the Topical Lectures at Nikhef 2021.  This is again, and updated and improved version for the preparation of the Topical Lectures in 2026.

## Syllabus

The notebooks are intended to be worked through in order. 

* `student0_example_notebook`: Jupyter primer. Skip if you have used notebooks before.
* `student1_keyboard`: first flight. Keyboard control of the raw motor voltages. The lesson is that flying a drone with no controller is hard.
* `student2_system_identification`: measure your virtual drone (motor offset, hover voltage, clipping limits).
* `student3_basic_control`: build the first feedback loops. Tilt PD, then a flat cascade for altitude and lateral position.
* `student3b_velocity_loop`: insert a velocity loop between the position controller and the attitude loop. Non-racing step-response demo showing why a cascade with an explicit speed cap is structurally better than reading the position PID's output directly as a tilt.
* `student4a_racing`: first easy race. Interactive keyboard control of the position setpoint, with the velocity cascade in charge underneath.
* `student4b_racing_noninteractive`: same race, headless. Records the trajectory and replays it as an inline video.
* `student5_model_based_control`: replace the dimensionless tilt clip with an algebraic inversion of the drone dynamics. Ask for a desired acceleration, get the unique tilt and thrust that produce it.
* `student6_trajectories`: add a smooth fly-through trajectory between waypoints. Tangent-step lookahead on the trajectory's closest-point projection so the drone tracks the planned spiral without cutting corners.

`module.py` provides the `Drone`, `Plotter`, `PIDController`, `accel_to_phi_F`, and `render_replay` building blocks the notebooks rely on. Keep it in the same directory.

## Drone model

The virtual drone is a 2D slice (y, z, phi) of a Crazyflie 2.1, with parameters matched to the high-fidelity Simulink model in Richardson and Pretorius, MATEC Web of Conferences 417, 04007 (2025). See `drone_parameters.md` for the full parameter list and where each value comes from.

For the interactive notebooks (1 and 4a) you need a Qt backend. `pip install pyqt5` or `conda install pyqt` is usually enough. Notebooks 4b, 5 and 6 produce inline HTML5 video and have no GUI dependency, so they run on Google Colab as well.
