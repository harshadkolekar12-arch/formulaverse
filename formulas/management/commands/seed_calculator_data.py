from django.core.management.base import BaseCommand
from formulas.models import Formula, FormulaVariable, FormulaConstant

CALCULATOR_DATA = {
    # Make sure this matches your formula's exact title (or slug)
    "First Equation of Motion": {
        "variables": [
            ("v", "Final velocity", "m/s", "u + (a * t)", 1),
            ("u", "Initial velocity", "m/s", "v - (a * t)", 2),
            ("a", "Acceleration", "m/s^2", "(v - u) / t", 3),
            ("t", "Time", "s", "(v - u) / a", 4),
        ],
        "constants": [],
    },

    "Single Slit Diffraction (Minima Condition)": {
        "variables": [
            ("a", "Slit width", "m", "n * lambda / sin(theta)", 1),
            ("theta", "Diffraction angle", "rad", "asin((n * lambda) / a)", 2),
            ("n", "Order of minimum", "", "a * sin(theta) / lambda", 3),
            ("lambda", "Wavelength", "m", "a * sin(theta) / n", 4),
        ],
        "constants": [],
    },

    "Fringe width (Young's double slit)": {
        "variables": [
            ("beta", "Fringe width", "m", "lambda * D / d", 1),
            ("lambda", "Wavelength", "m", "beta * d / D", 2),
            ("D", "Screen distance", "m", "beta * d / lambda", 3),
            ("d", "Slit separation", "m", "lambda * D / beta", 4),
        ],
        "constants": [],
    },

    "Critical angle (Total internal reflection)": {
        "variables": [
            ("theta_c", "Critical angle", "rad", "asin(1 / n)", 1),
            ("n", "Refractive index", "", "1 / sin(theta_c)", 2),
        ],
        "constants": [],
    },

    "Angle of Deviation (Prism)": {
        "variables": [
            ("delta", "Angle of deviation", "rad", "i1 + i2 - A", 1),
            ("i1", "Angle of entry", "rad", "delta + A - i2", 2),
            ("i2", "Angle of emergence", "rad", "delta + A - i1", 3),
            ("A", "Prism angle", "rad", "i1 + i2 - delta", 4),
        ],
        "constants": [],
    },

    "Equation of Continuity": {
        "variables": [
            ("A1", "Area 1", "m^2", "A2 * v2 / v1", 1),
            ("v1", "Velocity 1", "m/s", "A2 * v2 / A1", 2),
            ("A2", "Area 2", "m^2", "A1 * v1 / v2", 3),
            ("v2", "Velocity 2", "m/s", "A1 * v1 / A2", 4),
        ],
        "constants": [],
    },

    "Torricelli's Law": {
        "variables": [
            ("v", "Efflux velocity", "m/s", "sqrt(2 * g * h)", 1),
            ("h", "Fluid depth", "m", "v^2 / (2 * g)", 2),
        ],
        "constants": [("g", 9.81)],
    },

    "Reynolds Number": {
        "variables": [
            ("Re", "Reynolds number", "", "rho * v * d / eta", 1),
            ("rho", "Fluid density", "kg/m^3", "Re * eta / (v * d)", 2),
            ("v", "Flow velocity", "m/s", "Re * eta / (rho * d)", 3),
            ("d", "Pipe diameter", "m", "Re * eta / (rho * v)", 4),
            ("eta", "Dynamic viscosity", "Pa*s", "rho * v * d / Re", 5),
        ],
        "constants": [],
    },

    "Velocity in SHM": {
        "variables": [
            ("v", "Velocity", "m/s", "omega * sqrt(A^2 - x^2)", 1),
            ("omega", "Angular frequency", "rad/s", "v / sqrt(A^2 - x^2)", 2),
            ("A", "Amplitude", "m", "sqrt(x^2 + (v / omega)^2)", 3),
            ("x", "Displacement", "m", "sqrt(A^2 - (v / omega)^2)", 4),
        ],
        "constants": [],
    },

    "Time Period of a Spring-Mass System": {
        "variables": [
            ("T", "Time period", "s", "2 * pi * sqrt(m / k)", 1),
            ("m", "Mass", "kg", "k * (T / (2 * pi))^2", 2),
            ("k", "Spring constant", "N/m", "m / (T / (2 * pi))^2", 3),
        ],
        "constants": [("pi", 3.14159)],
    },

    "Potential Energy in SHM": {
        "variables": [
            ("PE", "Potential energy", "J", "0.5 * m * omega^2 * x^2", 1),
            ("m", "Mass", "kg", "2 * PE / (omega^2 * x^2)", 2),
            ("omega", "Angular frequency", "rad/s", "sqrt(2 * PE / (m * x^2))", 3),
            ("x", "Displacement", "m", "sqrt(2 * PE / (m * omega^2))", 4),
        ],
        "constants": [],
    },

    "Kinetic Energy in SHM": {
        "variables": [
            ("KE", "Kinetic energy", "J", "0.5 * m * omega^2 * (A^2 - x^2)", 1),
            ("m", "Mass", "kg", "2 * KE / (omega^2 * (A^2 - x^2))", 2),
            ("omega", "Angular frequency", "rad/s", "sqrt(2 * KE / (m * (A^2 - x^2)))", 3),
            ("A", "Amplitude", "m", "sqrt(x^2 + 2 * KE / (m * omega^2))", 4),
            ("x", "Displacement", "m", "sqrt(A^2 - 2 * KE / (m * omega^2))", 5),
        ],
        "constants": [],
    },

    "Time Period of a Physical Pendulum": {
        "variables": [
            ("T", "Time period", "s", "2 * pi * sqrt(I / (m * g * d))", 1),
            ("I", "Moment of inertia", "kg*m^2", "m * g * d * (T / (2 * pi))^2", 2),
            ("m", "Mass", "kg", "I / (g * d * (T / (2 * pi))^2)", 3),
            ("d", "Distance to COM", "m", "I / (m * g * (T / (2 * pi))^2)", 4),
        ],
        "constants": [("g", 9.81), ("pi", 3.14159)],
    },

    "Force between two parallel current-carrying wires": {
        "variables": [
            ("f_per_l", "Force per unit length", "N/m", "mu_0 * I1 * I2 / (2 * pi * d)", 1),
            ("I1", "Current 1", "A", "2 * pi * d * f_per_l / (mu_0 * I2)", 2),
            ("I2", "Current 2", "A", "2 * pi * d * f_per_l / (mu_0 * I1)", 3),
            ("d", "Wire separation", "m", "mu_0 * I1 * I2 / (2 * pi * f_per_l)", 4),
        ],
        "constants": [("mu_0", 1.2566e-6), ("pi", 3.14159)],
    },

    "Magnetic Field inside a Toroid": {
        "variables": [
            ("B", "Magnetic field", "T", "mu_0 * N * I / (2 * pi * r)", 1),
            ("N", "Number of turns", "", "2 * pi * r * B / (mu_0 * I)", 2),
            ("I", "Current", "A", "2 * pi * r * B / (mu_0 * N)", 3),
            ("r", "Toroid radius", "m", "mu_0 * N * I / (2 * pi * B)", 4),
        ],
        "constants": [("mu_0", 1.2566e-6), ("pi", 3.14159)],
    },

    "Magnetic Field at Center of a Circular Loop": {
        "variables": [
            ("B", "Magnetic field", "T", "mu_0 * N * I / (2 * R)", 1),
            ("N", "Number of turns", "", "2 * R * B / (mu_0 * I)", 2),
            ("I", "Current", "A", "2 * R * B / (mu_0 * N)", 3),
            ("R", "Loop radius", "m", "mu_0 * N * I / (2 * B)", 4),
        ],
        "constants": [("mu_0", 1.2566e-6)],
    },

    "Power Gain of Amplifier": {
        "variables": [
            ("A_p", "Power gain", "", "beta^2 * (R_out / R_in)", 1),
            ("beta", "Current gain", "", "sqrt(A_p * R_in / R_out)", 2),
            ("R_out", "Output resistance", "ohm", "A_p * R_in / (beta^2)", 3),
            ("R_in", "Input resistance", "ohm", "R_out * (beta^2) / A_p", 4),
        ],
        "constants": [],
    },

    "Voltage Gain of Amplifier": {
        "variables": [
            ("A_v", "Voltage gain", "", "beta * (R_load / R_in)", 1),
            ("beta", "Current gain", "", "A_v * R_in / R_load", 2),
            ("R_load", "Load resistance", "ohm", "A_v * R_in / beta", 3),
            ("R_in", "Input resistance", "ohm", "beta * R_load / A_v", 4),
        ],
        "constants": [],
    },

    "Ripple Factor (Full-Wave)": {
        "variables": [
            ("gamma", "Ripple factor", "", "sqrt((V_rms / V_dc)^2 - 1)", 1),
            ("V_rms", "RMS AC voltage component", "V", "V_dc * sqrt(gamma^2 + 1)", 2),
            ("V_dc", "DC voltage output", "V", "V_rms / sqrt(gamma^2 + 1)", 3),
        ],
        "constants": [],
    },

    "Ripple Factor (Half-Wave)": {
        "variables": [
            ("gamma", "Ripple factor", "", "sqrt((V_rms / V_dc)^2 - 1)", 1),
            ("V_rms", "RMS AC voltage component", "V", "V_dc * sqrt(gamma^2 + 1)", 2),
            ("V_dc", "DC voltage output", "V", "V_rms / sqrt(gamma^2 + 1)", 3),
        ],
        "constants": [],
    },


    "Full-Wave Rectifier Efficiency": {
        "variables": [
            ("eta", "Efficiency", "%", "(P_dc / P_ac) * 100", 1),
            ("P_dc", "DC output power", "W", "(eta / 100) * P_ac", 2),
            ("P_ac", "AC input power", "W", "P_dc / (eta / 100)", 3),
        ],
        "constants": [],
    },


    "Half-Wave Rectifier Efficiency": {
        "variables": [
            ("eta", "Efficiency", "%", "(P_dc / P_ac) * 100", 1),
            ("P_dc", "DC output power", "W", "(eta / 100) * P_ac", 2),
            ("P_ac", "AC input power", "W", "P_dc / (eta / 100)", 3),
        ],
        "constants": [],
    },


    "Diode Equation": {
        "variables": [
            ("I", "Diode current", "A", "I_0 * (exp(V / (eta * V_T)) - 1)", 1),
            ("I_0", "Reverse saturation current", "A", "I / (exp(V / (eta * V_T)) - 1)", 2),
            ("V", "Applied voltage", "V", "eta * V_T * log(I / I_0 + 1)", 3),
        ],
        "constants": [("V_T", 0.026), ("eta", 1.0)],
    },


    "Relation between Alpha and Beta": {
        "variables": [
            ("beta", "Beta current gain", "", "alpha / (1 - alpha)", 1),
            ("alpha", "Alpha current gain", "", "beta / (1 + beta)", 2),
        ],
        "constants": [],
    },


    "Current Amplification Factor (Alpha)": {
        "variables": [
            ("alpha", "Alpha current gain", "", "dI_C / dI_E", 1),
            ("dI_C", "Change in collector current", "A", "alpha * dI_E", 2),
            ("dI_E", "Change in emitter current", "A", "dI_C / alpha", 3),
        ],
        "constants": [],
    },


    "Current Amplification Factor (Beta)": {
        "variables": [
            ("beta", "Beta current gain", "", "dI_C / dI_B", 1),
            ("dI_C", "Change in collector current", "A", "beta * dI_B", 2),
            ("dI_B", "Change in base current", "A", "dI_C / beta", 3),
        ],
        "constants": [],
    },


    "Transistor Current Relation": {
        "variables": [
            ("I_E", "Emitter current", "A", "I_B + I_C", 1),
            ("I_B", "Base current", "A", "I_E - I_C", 2),
            ("I_C", "Collector current", "A", "I_E - I_B", 3),
        ],
        "constants": [],
    },


    "Intensity of a Wave": {
        "variables": [
            ("I", "Intensity", "W/m^2", "0.5 * rho * v * omega^2 * A^2", 1),
            ("rho", "Medium density", "kg/m^3", "2 * I / (v * omega^2 * A^2)", 2),
            ("v", "Wave speed", "m/s", "2 * I / (rho * omega^2 * A^2)", 3),
            ("omega", "Angular frequency", "rad/s", "sqrt(2 * I / (rho * v * A^2))", 4),
            ("A", "Wave amplitude", "m", "sqrt(2 * I / (rho * v * omega^2))", 5),
        ],
        "constants": [],
    },


    "Equation of Progressive Wave": {
        "variables": [
            ("y", "Displacement", "m", "A * sin(omega * t - k * x)", 1),
            ("A", "Amplitude", "m", "y / sin(omega * t - k * x)", 2),
            ("omega", "Angular frequency", "rad/s", "(asin(y / A) + k * x) / t", 3),
            ("t", "Time", "s", "(asin(y / A) + k * x) / omega", 4),
            ("k", "Wave number", "rad/m", "(omega * t - asin(y / A)) / x", 5),
            ("x", "Position", "m", "(omega * t - asin(y / A)) / k", 6),
        ],
        "constants": [],
    },


    "Wave Number": {
        "variables": [
            ("k", "Wave number", "rad/m", "2 * pi / lambda", 1),
            ("lambda", "Wavelength", "m", "2 * pi / k", 2),
        ],
        "constants": [("pi", 3.14159)],
    },


    "Angular Frequency": {
        "variables": [
            ("omega", "Angular frequency", "rad/s", "2 * pi * f", 1),
            ("f", "Frequency", "Hz", "omega / (2 * pi)", 2),
            ("T", "Time period", "s", "2 * pi / omega", 3),
        ],
        "constants": [("pi", 3.14159)],
    },


    "Time Period": {
        "variables": [
            ("T", "Time period", "s", "1 / f", 1),
            ("f", "Frequency", "Hz", "1 / T", 2),
        ],
        "constants": [],
    },


    "Wave Speed": {
        "variables": [
            ("v", "Wave speed", "m/s", "f * lambda", 1),
            ("f", "Frequency", "Hz", "v / lambda", 2),
            ("lambda", "Wavelength", "m", "v / f", 3),
        ],
        "constants": [],
    },


    "Efficiency of a Machine": {
        "variables": [
            ("eta", "Efficiency", "%", "(W_output / W_input) * 100", 1),
            ("W_output", "Output work", "J", "(eta / 100) * W_input", 2),
            ("W_input", "Input work", "J", "W_output / (eta / 100)", 3),
        ],
        "constants": [],
    },


    "Conservation of Mechanical Energy": {
        "variables": [
            ("E", "Total mechanical energy", "J", "KE + PE", 1),
            ("KE", "Kinetic energy", "J", "E - PE", 2),
            ("PE", "Potential energy", "J", "E - KE", 3),
        ],
        "constants": [],
    },


    "Kinetic Energy": {
        "variables": [
            ("KE", "Kinetic energy", "J", "0.5 * m * v^2", 1),
            ("m", "Mass", "kg", "2 * KE / v^2", 2),
            ("v", "Velocity", "m/s", "sqrt(2 * KE / m)", 3),
        ],
        "constants": [],
    },


    "Work done by a Force": {
        "variables": [
            ("W", "Work done", "J", "F * s * cos(theta)", 1),
            ("F", "Force", "N", "W / (s * cos(theta))", 2),
            ("s", "Displacement", "m", "W / (F * cos(theta))", 3),
            ("theta", "Angle", "rad", "acos(W / (F * s))", 4),
        ],
        "constants": [],
    },


    "Coefficient of Restitution": {
        "variables": [
            ("e", "Coefficient of restitution", "", "(v2 - v1) / (u1 - u2)", 1),
            ("v2", "Final velocity 2", "m/s", "v1 + e * (u1 - u2)", 2),
            ("v1", "Final velocity 1", "m/s", "v2 - e * (u1 - u2)", 3),
            ("u1", "Initial velocity 1", "m/s", "u2 + (v2 - v1) / e", 4),
            ("u2", "Initial velocity 2", "m/s", "u1 - (v2 - v1) / e", 5),
        ],
        "constants": [],
    },

    "Conservation of Linear Momentum": {
        "variables": [
            ("p_total", "Total momentum", "kg*m/s", "m1 * u1 + m2 * u2", 1),
            ("m1", "Mass 1", "kg", "(p_total - m2 * u2) / u1", 2),
            ("u1", "Initial velocity 1", "m/s", "(p_total - m2 * u2) / m1", 3),
            ("m2", "Mass 2", "kg", "(p_total - m1 * u1) / u2", 4),
            ("u2", "Initial velocity 2", "m/s", "(p_total - m1 * u1) / m2", 5),
        ],
        "constants": [],
    },


    "Average Velocity": {
        "variables": [
            ("v_avg", "Average velocity", "m/s", "delta_x / delta_t", 1),
            ("delta_x", "Displacement", "m", "v_avg * delta_t", 2),
            ("delta_t", "Time interval", "s", "delta_x / v_avg", 3),
        ],
        "constants": [],
    },


    "Third Equation of Motion": {
        "variables": [
            ("v", "Final velocity", "m/s", "sqrt(u^2 + 2 * a * s)", 1),
            ("u", "Initial velocity", "m/s", "sqrt(v^2 - 2 * a * s)", 2),
            ("a", "Acceleration", "m/s^2", "(v^2 - u^2) / (2 * s)", 3),
            ("s", "Displacement", "m", "(v^2 - u^2) / (2 * a)", 4),
        ],
        "constants": [],
    },


    "Second Equation of Motion": {
        "variables": [
            ("s", "Displacement", "m", "u * t + 0.5 * a * t^2", 1),
            ("u", "Initial velocity", "m/s", "(s - 0.5 * a * t^2) / t", 2),
            ("a", "Acceleration", "m/s^2", "2 * (s - u * t) / t^2", 3),
            ("t", "Time", "s", "(-u + sqrt(u^2 + 2 * a * s)) / a", 4),
        ],
        "constants": [],
    },


    "Gravitational Field Intensity": {
        "variables": [
            ("E_g", "Field intensity", "N/kg", "G * M / r^2", 1),
            ("M", "Mass of source body", "kg", "E_g * r^2 / G", 2),
            ("r", "Distance", "m", "sqrt(G * M / E_g)", 3),
        ],
        "constants": [("G", 6.6743e-11)],
    },


    "Total Energy of Satellite": {
        "variables": [
            ("E", "Total energy", "J", "-G * M * m / (2 * r)", 1),
            ("M", "Planet mass", "kg", "-2 * r * E / (G * m)", 2),
            ("m", "Satellite mass", "kg", "-2 * r * E / (G * M)", 3),
            ("r", "Orbital radius", "m", "-G * M * m / (2 * E)", 4),
        ],
        "constants": [("G", 6.6743e-11)],
    },


    "Kepler's Third Law": {
        "variables": [
            ("T", "Orbital period", "s", "sqrt(4 * pi^2 * r^3 / (G * M))", 1),
            ("r", "Orbital radius", "m", "(G * M * T^2 / (4 * pi^2))^(1/3)", 2),
            ("M", "Central mass", "kg", "4 * pi^2 * r^3 / (G * T^2)", 3),
        ],
        "constants": [("G", 6.6743e-11), ("pi", 3.14159)],
    },

    "Orbital Velocity": {
        "variables": [
            ("v_o", "Orbital velocity", "m/s", "sqrt(G * M / r)", 1),
            ("M", "Mass of central body", "kg", "v_o^2 * r / G", 2),
            ("r", "Orbital radius", "m", "G * M / v_o^2", 3),
        ],
        "constants": [("G", 6.6743e-11)],
    },
    "Gravitational Potential": {
        "variables": [
            ("V", "Gravitational potential", "J/kg", "-G * M / r", 1),
            ("M", "Mass of central body", "kg", "-V * r / G", 2),
            ("r", "Distance", "m", "-G * M / V", 3),
        ],
        "constants": [("G", 6.6743e-11)],
    },
    "Gravitational Potential Energy": {
        "variables": [
            ("U", "Potential energy", "J", "-G * M * m / r", 1),
            ("M", "Source mass", "kg", "-U * r / (G * m)", 2),
            ("m", "Test mass", "kg", "-U * r / (G * M)", 3),
            ("r", "Distance", "m", "-G * M * m / U", 4),
        ],
        "constants": [("G", 6.6743e-11)],
    },
    "Variation of g with depth": {
        "variables": [
            ("g_d", "Gravity at depth d", "m/s^2", "g * (1 - d / R)", 1),
            ("g", "Surface gravity", "m/s^2", "g_d / (1 - d / R)", 2),
            ("d", "Depth below surface", "m", "R * (1 - g_d / g)", 3),
            ("R", "Radius of Earth", "m", "6371000", 4),
        ],
        "constants": [],
    },
    "Variation of g with Height": {
        "variables": [
            ("g_h", "Gravity at height h", "m/s^2", "g * (1 - 2 * h / R)", 1),
            ("g", "Surface gravity", "m/s^2", "g_h / (1 - 2 * h / R)", 2),
            ("h", "Height above surface", "m", "R * (1 - g_h / g) / 2", 3),
            ("R", "Radius of Earth", "m", "6371000", 4),
        ],
        "constants": [],
    },
    "Acceleration due to Gravity (surface)": {
        "variables": [
            ("g", "Surface gravity", "m/s^2", "G * M / R^2", 1),
            ("M", "Mass of planet", "kg", "g * R^2 / G", 2),
            ("R", "Radius of planet", "m", "sqrt(G * M / g)", 3),
        ],
        "constants": [("G", 6.6743e-11)],
    },
    "Malus's Law": {
        "variables": [
            ("I", "Transmitted intensity", "W/m^2", "I_0 * cos(theta)^2", 1),
            ("I_0", "Initial intensity", "W/m^2", "I / cos(theta)^2", 2),
            ("theta", "Angle between polarizers", "rad", "acos(sqrt(I / I_0))", 3),
        ],
        "constants": [],
    },
    "Brewster's Law": {
        "variables": [
            ("theta_B", "Brewster angle", "rad", "atan(n2 / n1)", 1),
            ("n2", "Refractive index 2", "", "n1 * tan(theta_B)", 2),
            ("n1", "Refractive index 1", "", "n2 / tan(theta_B)", 3),
        ],
        "constants": [],
    },
    "Diffraction Grating": {
        "variables": [
            ("d", "Grating element spacing", "m", "n * lambda / sin(theta)", 1),
            ("theta", "Diffraction angle", "rad", "asin(n * lambda / d)", 2),
            ("n", "Order of spectrum", "", "d * sin(theta) / lambda", 3),
            ("lambda", "Wavelength", "m", "d * sin(theta) / n", 4),
        ],
        "constants": [],
    },
    "Conditions for Bright/Dark Fringes": {
        "variables": [
            ("delta", "Path difference", "m", "n * lambda", 1),
            ("n", "Order of fringe", "", "delta / lambda", 2),
            ("lambda", "Wavelength", "m", "delta / n", 3),
        ],
        "constants": [],
    },
    "Young's Double Slit Experiment": {
        "variables": [
            ("beta", "Fringe width", "m", "lambda * D / d", 1),
            ("lambda", "Wavelength", "m", "beta * d / D", 2),
            ("D", "Screen distance", "m", "beta * d / lambda", 3),
            ("d", "Slit separation", "m", "lambda * D / beta", 4),
        ],
        "constants": [],
    },
    "Power of a Lens": {
        "variables": [
            ("P", "Lens power", "D", "1 / f", 1),
            ("f", "Focal length", "m", "1 / P", 2),
        ],
        "constants": [],
    },
    "Lens Maker's Formula": {
        "variables": [
            ("f", "Focal length", "m", "1 / ((n - 1) * (1 / R1 - 1 / R2))", 1),
            ("n", "Refractive index", "", "1 + 1 / (f * (1 / R1 - 1 / R2))", 2),
            ("R1", "Radius of curvature 1", "m", "1 / (1 / R2 + 1 / (f * (n - 1)))", 3),
            ("R2", "Radius of curvature 2", "m", "1 / (1 / R1 - 1 / (f * (n - 1)))", 4),
        ],
        "constants": [],
    },
    "Magnification (mirror)": {
        "variables": [
            ("m", "Magnification", "", "-v / u", 1),
            ("v", "Image distance", "m", "-m * u", 2),
            ("u", "Object distance", "m", "-v / m", 3),
        ],
        "constants": [],
    },
    "Lens Formula": {
        "variables": [
            ("f", "Focal length", "m", "1 / (1 / v - 1 / u)", 1),
            ("v", "Image distance", "m", "1 / (1 / f + 1 / u)", 2),
            ("u", "Object distance", "m", "1 / (1 / v - 1 / f)", 3),
        ],
        "constants": [],
    },
    "Rydberg Formula (spectral lines)": {
        "variables": [
            ("lambda", "Wavelength", "m", "1 / (R_H * Z^2 * (1 / n1^2 - 1 / n2^2))", 1),
            ("Z", "Atomic number", "", "sqrt(1 / (lambda * R_H * (1 / n1^2 - 1 / n2^2)))", 2),
            ("n1", "Lower energy level", "", "1 / sqrt(1 / n2^2 + 1 / (lambda * R_H * Z^2))", 3),
            ("n2", "Higher energy level", "", "1 / sqrt(1 / n1^2 - 1 / (lambda * R_H * Z^2))", 4),
        ],
        "constants": [("R_H", 10973731.57)],
    },
    "Q-value of Nuclear Reaction": {
        "variables": [
            ("Q", "Q-value", "MeV", "(m_reactants - m_products) * 931.5", 1),
            ("m_reactants", "Mass of reactants", "u", "m_products + Q / 931.5", 2),
            ("m_products", "Mass of products", "u", "m_reactants - Q / 931.5", 3),
        ],
        "constants": [],
    },
    "Nuclear Binding Energy": {
        "variables": [
            ("BE", "Binding Energy", "MeV", "(Z * m_p + N * m_n - M) * 931.5", 1),
            ("Z", "Number of protons", "", "(BE / 931.5 + M - N * m_n) / m_p", 2),
            ("N", "Number of neutrons", "", "(BE / 931.5 + M - Z * m_p) / m_n", 3),
            ("M", "Mass of nucleus", "u", "Z * m_p + N * m_n - BE / 931.5", 4),
        ],
        "constants": [("m_p", 1.007276), ("m_n", 1.008665)],
    },
    "Energy of Photon": {
        "variables": [
            ("E", "Photon energy", "J", "h * f", 1),
            ("f", "Frequency", "Hz", "E / h", 2),
            ("lambda", "Wavelength", "m", "h * c / E", 3),
        ],
        "constants": [("h", 6.62607e-34), ("c", 3e8)],
    },
    "de Broglie Wavelength": {
        "variables": [
            ("lambda", "Wavelength", "m", "h / (m * v)", 1),
            ("m", "Particle mass", "kg", "h / (lambda * v)", 2),
            ("v", "Particle velocity", "m/s", "h / (lambda * m)", 3),
        ],
        "constants": [("h", 6.62607e-34)],
    },
    "Resonance in Closed pipe": {
        "variables": [
            ("f", "Resonance frequency", "Hz", "n * v / (4 * L)", 1),
            ("n", "Harmonic number (odd)", "", "4 * L * f / v", 2),
            ("v", "Speed of sound", "m/s", "4 * L * f / n", 3),
            ("L", "Length of pipe", "m", "n * v / (4 * f)", 4),
        ],
        "constants": [],
    },
    "Resonance in Open Pipe": {
        "variables": [
            ("f", "Resonance frequency", "Hz", "n * v / (2 * L)", 1),
            ("n", "Harmonic number", "", "2 * L * f / v", 2),
            ("v", "Speed of sound", "m/s", "2 * L * f / n", 3),
            ("L", "Length of pipe", "m", "n * v / (2 * f)", 4),
        ],
        "constants": [],
    },
    "Beats Frequency": {
        "variables": [
            ("f_beat", "Beat frequency", "Hz", "abs(f1 - f2)", 1),
            ("f1", "Frequency 1", "Hz", "f2 + f_beat", 2),
            ("f2", "Frequency 2", "Hz", "f1 - f_beat", 3),
        ],
        "constants": [],
    },

    "Doppler Effect": {
        "variables": [
            ("f_prime", "Observed frequency", "Hz", "f * (v + v_o) / (v - v_s)", 1),
            ("f", "Source frequency", "Hz", "f_prime * (v - v_s) / (v + v_o)", 2),
            ("v", "Speed of sound", "m/s", "343", 3),
            ("v_o", "Observer velocity", "m/s", "(f_prime * (v - v_s) / f) - v", 4),
            ("v_s", "Source velocity", "m/s", "v - (f * (v + v_o) / f_prime)", 5),
        ],
        "constants": [],
    },
    "Speed of sound in medium": {
        "variables": [
            ("v", "Speed of sound", "m/s", "sqrt(B / rho)", 1),
            ("B", "Bulk modulus", "Pa", "rho * v^2", 2),
            ("rho", "Density of medium", "kg/m^3", "B / v^2", 3),
        ],
        "constants": [],
    },
    "Standing Wave (string)": {
        "variables": [
            ("f_n", "Harmonic frequency", "Hz", "n * v / (2 * L)", 1),
            ("n", "Harmonic number", "", "2 * L * f_n / v", 2),
            ("v", "Wave speed", "m/s", "2 * L * f_n / n", 3),
            ("L", "String length", "m", "n * v / (2 * f_n)", 4),
        ],
        "constants": [],
    },
    "Energy in SHM": {
        "variables": [
            ("E", "Total energy", "J", "0.5 * m * omega^2 * A^2", 1),
            ("m", "Mass", "kg", "2 * E / (omega^2 * A^2)", 2),
            ("omega", "Angular frequency", "rad/s", "sqrt(2 * E / (m * A^2))", 3),
            ("A", "Amplitude", "m", "sqrt(2 * E / (m * omega^2))", 4),
        ],
        "constants": [],
    },
    "Displacement in SHM": {
        "variables": [
            ("x", "Displacement", "m", "A * cos(omega * t)", 1),
            ("A", "Amplitude", "m", "x / cos(omega * t)", 2),
            ("omega", "Angular frequency", "rad/s", "acos(x / A) / t", 3),
            ("t", "Time", "s", "acos(x / A) / omega", 4),
        ],
        "constants": [],
    },
    "Capillary Rise": {
        "variables": [
            ("h", "Height of rise", "m", "2 * T * cos(theta) / (r * rho * g)", 1),
            ("T", "Surface tension", "N/m", "h * r * rho * g / (2 * cos(theta))", 2),
            ("theta", "Contact angle", "rad", "acos(h * r * rho * g / (2 * T))", 3),
            ("r", "Capillary radius", "m", "2 * T * cos(theta) / (h * rho * g)", 4),
            ("rho", "Liquid density", "kg/m^3", "2 * T * cos(theta) / (h * r * g)", 5),
        ],
        "constants": [("g", 9.81)],
    },
    "Surface Tension (excess pressure)": {
        "variables": [
            ("delta_P", "Excess pressure", "Pa", "2 * T / r", 1),
            ("T", "Surface tension", "N/m", "delta_P * r / 2", 2),
            ("r", "Radius", "m", "2 * T / delta_P", 3),
        ],
        "constants": [],
    },
    "Poiseuille's Equation": {
        "variables": [
            ("Q", "Volume flow rate", "m^3/s", "pi * r^4 * delta_P / (8 * eta * L)", 1),
            ("r", "Pipe radius", "m", "(8 * Q * eta * L / (pi * delta_P))^(1/4)", 2),
            ("delta_P", "Pressure difference", "Pa", "8 * Q * eta * L / (pi * r^4)", 3),
            ("eta", "Dynamic viscosity", "Pa*s", "pi * r^4 * delta_P / (8 * Q * L)", 4),
            ("L", "Pipe length", "m", "pi * r^4 * delta_P / (8 * Q * eta)", 5),
        ],
        "constants": [("pi", 3.14159)],
    },
    "Terminal Velocity": {
        "variables": [
            ("v_t", "Terminal velocity", "m/s", "2 * r^2 * (rho - sigma) * g / (9 * eta)", 1),
            ("r", "Sphere radius", "m", "sqrt(9 * eta * v_t / (2 * (rho - sigma) * g))", 2),
            ("rho", "Sphere density", "kg/m^3", "sigma + 9 * eta * v_t / (2 * r^2 * g)", 3),
            ("sigma", "Fluid density", "kg/m^3", "rho - 9 * eta * v_t / (2 * r^2 * g)", 4),
            ("eta", "Fluid viscosity", "Pa*s", "2 * r^2 * (rho - sigma) * g / (9 * v_t)", 5),
        ],
        "constants": [("g", 9.81)],
    },
    "Stokes' Law": {
        "variables": [
            ("F", "Drag force", "N", "6 * pi * eta * r * v", 1),
            ("eta", "Fluid viscosity", "Pa*s", "F / (6 * pi * r * v)", 2),
            ("r", "Sphere radius", "m", "F / (6 * pi * eta * v)", 3),
            ("v", "Velocity", "m/s", "F / (6 * pi * eta * r)", 4),
        ],
        "constants": [("pi", 3.14159)],
    },
    "Archimedes' Principle": {
        "variables": [
            ("F_b", "Buoyant force", "N", "rho * V * g", 1),
            ("rho", "Fluid density", "kg/m^3", "F_b / (V * g)", 2),
            ("V", "Displaced volume", "m^3", "F_b / (rho * g)", 3),
        ],
        "constants": [("g", 9.81)],
    },
    "Transformer Ratio": {
        "variables": [
            ("Vs", "Secondary voltage", "V", "Vp * Ns / Np", 1),
            ("Vp", "Primary voltage", "V", "Vs * Np / Ns", 2),
            ("Ns", "Secondary turns", "", "Np * Vs / Vp", 3),
            ("Np", "Primary turns", "", "Ns * Vp / Vs", 4),
        ],
        "constants": [],
    },
    "Mutual Inductance": {
        "variables": [
            ("EMF", "Induced EMF", "V", "-M * dI_dt", 1),
            ("M", "Mutual inductance", "H", "-EMF / dI_dt", 2),
            ("dI_dt", "Current change rate", "A/s", "-EMF / M", 3),
        ],
        "constants": [],
    },
    "Self Inductance": {
        "variables": [
            ("EMF", "Self-induced EMF", "V", "-L * dI_dt", 1),
            ("L", "Self inductance", "H", "-EMF / dI_dt", 2),
            ("dI_dt", "Current change rate", "A/s", "-EMF / L", 3),
        ],
        "constants": [],
    },
    "Faraday's Law": {
        "variables": [
            ("EMF", "Induced EMF", "V", "-N * dphi_dt", 1),
            ("N", "Number of turns", "", "-EMF / dphi_dt", 2),
            ("dphi_dt", "Magnetic flux change rate", "Wb/s", "-EMF / N", 3),
        ],
        "constants": [],
    },
    "Lorentz Force": {
        "variables": [
            ("F", "Lorentz force", "N", "q * (E + v * B)", 1),
            ("q", "Particle charge", "C", "F / (E + v * B)", 2),
            ("E", "Electric field", "V/m", "(F / q) - (v * B)", 3),
            ("v", "Particle velocity", "m/s", "((F / q) - E) / B", 4),
            ("B", "Magnetic field", "T", "((F / q) - E) / v", 5),
        ],
        "constants": [],
    },
    "Cyclotron Frequency": {
        "variables": [
            ("f", "Cyclotron frequency", "Hz", "q * B / (2 * pi * m)", 1),
            ("q", "Particle charge", "C", "2 * pi * m * f / B", 2),
            ("B", "Magnetic field", "T", "2 * pi * m * f / q", 3),
            ("m", "Particle mass", "kg", "q * B / (2 * pi * f)", 4),
        ],
        "constants": [("pi", 3.14159)],
    },
    "Magnetic Moment": {
        "variables": [
            ("M", "Magnetic moment", "A*m^2", "N * I * A", 1),
            ("N", "Number of turns", "", "M / (I * A)", 2),
            ("I", "Current", "A", "M / (N * A)", 3),
            ("A", "Loop area", "m^2", "M / (N * I)", 4),
        ],
        "constants": [],
    },
    "Ampere's Law": {
        "variables": [
            ("B", "Magnetic field", "T", "mu_0 * I / (2 * pi * r)", 1),
            ("I", "Current", "A", "2 * pi * r * B / mu_0", 2),
            ("r", "Distance", "m", "mu_0 * I / (2 * pi * B)", 3),
        ],
        "constants": [("mu_0", 1.2566e-6), ("pi", 3.14159)],
    },
    "Biot-Savart Law": {
        "variables": [
            ("dB", "Magnetic field element", "T", "(mu_0 / (4 * pi)) * I * dl * sin(theta) / r^2", 1),
            ("I", "Current", "A", "dB * 4 * pi * r^2 / (mu_0 * dl * sin(theta))", 2),
            ("dl", "Length element", "m", "dB * 4 * pi * r^2 / (mu_0 * I * sin(theta))", 3),
            ("theta", "Angle to element", "rad", "asin(dB * 4 * pi * r^2 / (mu_0 * I * dl))", 4),
            ("r", "Distance", "m", "sqrt((mu_0 / (4 * pi)) * I * dl * sin(theta) / dB)", 5),
        ],
        "constants": [("mu_0", 1.2566e-6), ("pi", 3.14159)],
    },
    "Joule's Law of Heating": {
        "variables": [
            ("H", "Heat produced", "J", "I^2 * R * t", 1),
            ("I", "Current", "A", "sqrt(H / (R * t))", 2),
            ("R", "Resistance", "ohm", "H / (I^2 * t)", 3),
            ("t", "Time", "s", "H / (I^2 * R)", 4),
        ],
        "constants": [],
    },
    "Resistance in Parallel": {
        "variables": [
            ("R", "Equivalent resistance", "ohm", "(R1 * R2) / (R1 + R2)", 1),
            ("R1", "Resistor 1", "ohm", "(R * R2) / (R2 - R)", 2),
            ("R2", "Resistor 2", "ohm", "(R * R1) / (R1 - R)", 3),
        ],
        "constants": [],
    },
    "Resistors in Series": {
        "variables": [
            ("R", "Total resistance", "ohm", "R1 + R2 + R3", 1),
            ("R1", "Resistor 1", "ohm", "R - R2 - R3", 2),
            ("R2", "Resistor 2", "ohm", "R - R1 - R3", 3),
            ("R3", "Resistor 3", "ohm", "R - R1 - R2", 4),
        ],
        "constants": [],
    },
    "Electric Field (infinite sheet)": {
        "variables": [
            ("E", "Electric field", "N/C", "sigma / (2 * epsilon_0)", 1),
            ("sigma", "Surface charge density", "C/m^2", "2 * epsilon_0 * E", 2),
        ],
        "constants": [("epsilon_0", 8.854e-12)],
    },
    "Gauss's law": {
        "variables": [
            ("phi", "Electric flux", "N*m^2/C", "Q_enc / epsilon_0", 1),
            ("Q_enc", "Enclosed charge", "C", "phi * epsilon_0", 2),
        ],
        "constants": [("epsilon_0", 8.854e-12)],
    },

    "Capacitors in Parallel": {
        "variables": [
            ("C", "Equivalent capacitance", "F", "C1 + C2 + C3", 1),
            ("C1", "Capacitor 1", "F", "C - C2 - C3", 2),
            ("C2", "Capacitor 2", "F", "C - C1 - C3", 3),
            ("C3", "Capacitor 3", "F", "C - C1 - C2", 4),
        ],
        "constants": [],
    },
    "Capacitors in Series": {
        "variables": [
            ("C", "Equivalent capacitance", "F", "(C1 * C2) / (C1 + C2)", 1),
            ("C1", "Capacitor 1", "F", "(C * C2) / (C2 - C)", 2),
            ("C2", "Capacitor 2", "F", "(C * C1) / (C1 - C)", 3),
        ],
        "constants": [],
    },
    "Newton's Law of Cooling": {
        "variables": [
            ("rate", "Rate of cooling (dT/dt)", "K/s", "k * (T - T_0)", 1),
            ("k", "Cooling constant", "1/s", "rate / (T - T_0)", 2),
            ("T", "Temperature of body", "K", "(rate / k) + T_0", 3),
            ("T_0", "Surrounding temperature", "K", "T - (rate / k)", 4),
        ],
        "constants": [],
    },
    "Specific Heat Capacity": {
        "variables": [
            ("Q", "Heat energy", "J", "m * c * delta_T", 1),
            ("m", "Mass", "kg", "Q / (c * delta_T)", 2),
            ("c", "Specific heat capacity", "J/(kg*K)", "Q / (m * delta_T)", 3),
            ("delta_T", "Temperature change", "K", "Q / (m * c)", 4),
        ],
        "constants": [],
    },
    "Mean Free Path": {
        "variables": [
            ("lambda_mfp", "Mean free path", "m", "1 / (sqrt(2) * n * pi * d^2)", 1),
            ("n", "Number density", "m^-3", "1 / (sqrt(2) * lambda_mfp * pi * d^2)", 2),
            ("d", "Molecular diameter", "m", "sqrt(1 / (sqrt(2) * n * pi * lambda_mfp))", 3),
        ],
        "constants": [("pi", 3.14159)],
    },
    "Charle's Law": {
        "variables": [
            ("V2", "Final volume", "m^3", "V1 * T2 / T1", 1),
            ("V1", "Initial volume", "m^3", "V2 * T1 / T2", 2),
            ("T1", "Initial temperature", "K", "V1 * T2 / V2", 3),
            ("T2", "Final temperature", "K", "V2 * T1 / V1", 4),
        ],
        "constants": [],
    },
    "Boyle's Law": {
        "variables": [
            ("P2", "Final pressure", "Pa", "P1 * V1 / V2", 1),
            ("P1", "Initial pressure", "Pa", "P2 * V2 / V1", 2),
            ("V1", "Initial volume", "m^3", "P2 * V2 / P1", 3),
            ("V2", "Final volume", "m^3", "P1 * V1 / P2", 4),
        ],
        "constants": [],
    },
    "First Law of Thermodynamics": {
        "variables": [
            ("dU", "Internal energy change", "J", "dQ - dW", 1),
            ("dQ", "Heat added", "J", "dU + dW", 2),
            ("dW", "Work done", "J", "dQ - dU", 3),
        ],
        "constants": [],
    },
    "Angular Impulse": {
        "variables": [
            ("J", "Angular impulse", "N*m*s", "tau * delta_t", 1),
            ("tau", "Torque", "N*m", "J / delta_t", 2),
            ("delta_t", "Time interval", "s", "J / tau", 3),
        ],
        "constants": [],
    },
    "Parallel Axis Theorem": {
        "variables": [
            ("I", "Moment of inertia", "kg*m^2", "I_c + M * d^2", 1),
            ("I_c", "Center of mass MOI", "kg*m^2", "I - M * d^2", 2),
            ("M", "Mass", "kg", "(I - I_c) / d^2", 3),
            ("d", "Distance to axis", "m", "sqrt((I - I_c) / M)", 4),
        ],
        "constants": [],
    },
    "Rotational Kinetic Energy": {
        "variables": [
            ("KE", "Rotational KE", "J", "0.5 * I * omega^2", 1),
            ("I", "Moment of inertia", "kg*m^2", "2 * KE / omega^2", 2),
            ("omega", "Angular velocity", "rad/s", "sqrt(2 * KE / I)", 3),
        ],
        "constants": [],
    },
    "Moment of Inertia (sphere)": {
        "variables": [
            ("I", "Moment of inertia", "kg*m^2", "0.4 * M * R^2", 1),
            ("M", "Mass", "kg", "I / (0.4 * R^2)", 2),
            ("R", "Radius", "m", "sqrt(I / (0.4 * M))", 3),
        ],
        "constants": [],
    },
    "Moment of Inertia (disk)": {
        "variables": [
            ("I", "Moment of inertia", "kg*m^2", "0.5 * M * R^2", 1),
            ("M", "Mass", "kg", "2 * I / R^2", 2),
            ("R", "Radius", "m", "sqrt(2 * I / M)", 3),
        ],
        "constants": [],
    },
    "Moment of Inertia (Rod)": {
        "variables": [
            ("I", "Moment of inertia", "kg*m^2", "(1 / 12) * M * L^2", 1),
            ("M", "Mass", "kg", "12 * I / L^2", 2),
            ("L", "Length", "m", "sqrt(12 * I / M)", 3),
        ],
        "constants": [],
    },
    "Banking of Roads": {
        "variables": [
            ("theta", "Banking angle", "rad", "atan(v^2 / (r * g))", 1),
            ("v", "Safe velocity", "m/s", "sqrt(r * g * tan(theta))", 2),
            ("r", "Turn radius", "m", "v^2 / (g * tan(theta))", 3),
        ],
        "constants": [("g", 9.81)],
    },
    "Gravitational Potential Energy": {
        "variables": [
            ("U", "Potential energy", "J", "-G * M * m / r", 1),
            ("M", "Source mass", "kg", "-U * r / (G * m)", 2),
            ("m", "Object mass", "kg", "-U * r / (G * M)", 3),
            ("r", "Distance", "m", "-G * M * m / U", 4),
        ],
        "constants": [("G", 6.6743e-11)],
    },
    "Hooke's Law": {
        "variables": [
            ("F", "Restoring force", "N", "-k * x", 1),
            ("k", "Spring constant", "N/m", "-F / x", 2),
            ("x", "Displacement", "m", "-F / k", 3),
        ],
        "constants": [],
    },
    "Work-Energy Theorem": {
        "variables": [
            ("W", "Work done", "J", "0.5 * m * (v^2 - u^2)", 1),
            ("m", "Mass", "kg", "2 * W / (v^2 - u^2)", 2),
            ("v", "Final velocity", "m/s", "sqrt(u^2 + 2 * W / m)", 3),
            ("u", "Initial velocity", "m/s", "sqrt(v^2 - 2 * W / m)", 4),
        ],
        "constants": [],
    },
    "Centripetal Acceleration": {
        "variables": [
            ("a", "Centripetal acceleration", "m/s^2", "v^2 / r", 1),
            ("v", "Tangential velocity", "m/s", "sqrt(a * r)", 2),
            ("r", "Radius", "m", "v^2 / a", 3),
        ],
        "constants": [],
    },
    "Range of Projectile (horizontal)": {
        "variables": [
            ("R", "Horizontal range", "m", "u^2 * sin(2 * theta) / g", 1),
            ("u", "Initial velocity", "m/s", "sqrt(R * g / sin(2 * theta))", 2),
            ("theta", "Launch angle", "rad", "0.5 * asin(R * g / u^2)", 3),
        ],
        "constants": [("g", 9.81)],
    },
    "First Equation of Motion": {
        "variables": [
            ("v", "Final velocity", "m/s", "u + a * t", 1),
            ("u", "Initial velocity", "m/s", "v - a * t", 2),
            ("a", "Acceleration", "m/s^2", "(v - u) / t", 3),
            ("t", "Time", "s", "(v - u) / a", 4),
        ],
        "constants": [],
    },
    "Half-Life": {
        "variables": [
            ("t_half", "Half-life", "s", "0.693 / lambda_decay", 1),
            ("lambda_decay", "Decay constant", "1/s", "0.693 / t_half", 2),
        ],
        "constants": [],
    },
    "Radioactive Decay Law": {
        "variables": [
            ("N", "Remaining nuclei", "", "N0 * exp(-lambda_decay * t)", 1),
            ("N0", "Initial nuclei", "", "N / exp(-lambda_decay * t)", 2),
            ("lambda_decay", "Decay constant", "1/s", "-log(N / N0) / t", 3),
            ("t", "Time", "s", "-log(N / N0) / lambda_decay", 4),
        ],
        "constants": [],
    },
    "Bohr's Energy (nth Orbit)": {
        "variables": [
            ("E_n", "Orbit energy", "eV", "-13.6 * Z^2 / n^2", 1),
            ("Z", "Atomic number", "", "sqrt(-E_n * n^2 / 13.6)", 2),
            ("n", "Principal quantum number", "", "sqrt(-13.6 * Z^2 / E_n)", 3),
        ],
        "constants": [],
    },

    "Mass-Energy Equivalence": {
        "variables": [
            ("E", "Energy", "J", "m * c^2", 1),
            ("m", "Mass", "kg", "E / (c^2)", 2),
        ],
        "constants": [("c", 3e8)],
    },
    "Photoelectric Effect": {
        "variables": [
            ("KE_max", "Max kinetic energy", "J", "h * f - phi", 1),
            ("f", "Frequency", "Hz", "(KE_max + phi) / h", 2),
            ("phi", "Work function", "J", "h * f - KE_max", 3),
        ],
        "constants": [("h", 6.62607e-34)],
    },
    "Energy stored in Inductor": {
        "variables": [
            ("U", "Stored energy", "J", "0.5 * L * I^2", 1),
            ("L", "Inductance", "H", "2 * U / (I^2)", 2),
            ("I", "Current", "A", "sqrt(2 * U / L)", 3),
        ],
        "constants": [],
    },
    "Magnetic Field of Solenoid": {
        "variables": [
            ("B", "Magnetic field", "T", "mu_0 * n * I", 1),
            ("n", "Turns per unit length", "1/m", "B / (mu_0 * I)", 2),
            ("I", "Current", "A", "B / (mu_0 * n)", 3),
        ],
        "constants": [("mu_0", 1.2566e-6)],
    },
    "Force on Current-carrying  Conductor": {
        "variables": [
            ("F", "Magnetic force", "N", "B * I * L * sin(theta)", 1),
            ("B", "Magnetic field", "T", "F / (I * L * sin(theta))", 2),
            ("I", "Current", "A", "F / (B * L * sin(theta))", 3),
            ("L", "Conductor length", "m", "F / (B * I * sin(theta))", 4),
            ("theta", "Angle to field", "rad", "asin(F / (B * I * L))", 5),
        ],
        "constants": [],
    },
    "Power Dissipated": {
        "variables": [
            ("P", "Power dissipated", "W", "I^2 * R", 1),
            ("I", "Current", "A", "sqrt(P / R)", 2),
            ("R", "Resistance", "ohm", "P / (I^2)", 3),
            ("V", "Voltage", "V", "sqrt(P * R)", 4),
        ],
        "constants": [],
    },
    "Wheatstone Bridge": {
        "variables": [
            ("P", "Resistor P", "ohm", "Q * R / S", 1),
            ("Q", "Resistor Q", "ohm", "P * S / R", 2),
            ("R", "Resistor R", "ohm", "P * S / Q", 3),
            ("S", "Resistor S", "ohm", "Q * R / P", 4),
        ],
        "constants": [],
    },
    "Kirchhoff's Current Law": {
        "variables": [
            ("I_in", "Total current in", "A", "I_out", 1),
            ("I_out", "Total current out", "A", "I_in", 2),
        ],
        "constants": [],
    },
    "Kirchhoff's Voltage Law": {
        "variables": [
            ("V_sum", "Sum of potential drops", "V", "0", 1),
        ],
        "constants": [],
    },
    "Work done by Gas (Isobaric)": {
        "variables": [
            ("W", "Work done", "J", "P * delta_V", 1),
            ("P", "Pressure", "Pa", "W / delta_V", 2),
            ("delta_V", "Volume change", "m^3", "W / P", 3),
        ],
        "constants": [],
    },
    "Time Period of a Satellite": {
        "variables": [
            ("T", "Orbital period", "s", "2 * pi * sqrt(r^3 / (G * M))", 1),
            ("r", "Orbital radius", "m", "(G * M * T^2 / (4 * pi^2))^(1/3)", 2),
            ("M", "Central mass", "kg", "4 * pi^2 * r^3 / (G * T^2)", 3),
        ],
        "constants": [("G", 6.6743e-11), ("pi", 3.14159)],
    },
    "Elastic Potential Energy": {
        "variables": [
            ("PE", "Elastic potential energy", "J", "0.5 * k * x^2", 1),
            ("k", "Spring constant", "N/m", "2 * PE / (x^2)", 2),
            ("x", "Extension/Compression", "m", "sqrt(2 * PE / k)", 3),
        ],
        "constants": [],
    },
    "Friction Force": {
        "variables": [
            ("f", "Friction force", "N", "mu * m * g", 1),
            ("mu", "Coefficient of friction", "", "f / (m * g)", 2),
            ("m", "Mass", "kg", "f / (mu * g)", 3),
        ],
        "constants": [("g", 9.81)],
    },
    "Maximum Height(Projectile)": {
        "variables": [
            ("H", "Maximum height", "m", "u^2 * (sin(theta))^2 / (2 * g)", 1),
            ("u", "Initial velocity", "m/s", "sqrt(2 * g * H) / sin(theta)", 2),
            ("theta", "Launch angle", "rad", "asin(sqrt(2 * g * H) / u)", 3),
        ],
        "constants": [("g", 9.81)],
    },
    "Relative Velocity": {
        "variables": [
            ("v_AB", "Relative velocity A w.r.t B", "m/s", "v_A - v_B", 1),
            ("v_A", "Velocity of A", "m/s", "v_AB + v_B", 2),
            ("v_B", "Velocity of B", "m/s", "v_A - v_AB", 3),
        ],
        "constants": [],
    },
    "Carnot Efficiency": {
        "variables": [
            ("eta", "Efficiency", "", "1 - T_C / T_H", 1),
            ("T_C", "Cold reservoir temp", "K", "T_H * (1 - eta)", 2),
            ("T_H", "Hot reservoir temp", "K", "T_C / (1 - eta)", 3),
        ],
        "constants": [],
    },
    "Angular Momentum": {
        "variables": [
            ("L", "Angular momentum", "kg*m^2/s", "m * v * r", 1),
            ("m", "Mass", "kg", "L / (v * r)", 2),
            ("v", "Velocity", "m/s", "L / (m * r)", 3),
            ("r", "Radius", "m", "L / (m * v)", 4),
        ],
        "constants": [],
    },
    "Torque": {
        "variables": [
            ("tau", "Torque", "N*m", "r * F * sin(theta)", 1),
            ("r", "Distance", "m", "tau / (F * sin(theta))", 2),
            ("F", "Force", "N", "tau / (r * sin(theta))", 3),
            ("theta", "Angle", "rad", "asin(tau / (r * F))", 4),
        ],
        "constants": [],
    },
    "Magnetic force on a charge": {
        "variables": [
            ("F", "Magnetic force", "N", "q * v * B * sin(theta)", 1),
            ("q", "Charge", "C", "F / (v * B * sin(theta))", 2),
            ("v", "Velocity", "m/s", "F / (q * B * sin(theta))", 3),
            ("B", "Magnetic field", "T", "F / (q * v * sin(theta))", 4),
            ("theta", "Angle", "rad", "asin(F / (q * v * B))", 5),
        ],
        "constants": [],
    },
    "Capacitance": {
        "variables": [
            ("C", "Capacitance", "F", "Q / V", 1),
            ("Q", "Charge", "C", "C * V", 2),
            ("V", "Voltage", "V", "Q / C", 3),
        ],
        "constants": [],
    },
    "Electric Potential Energy": {
        "variables": [
            ("U", "Electric potential energy", "J", "k * q1 * q2 / r", 1),
            ("q1", "Charge 1", "C", "U * r / (k * q2)", 2),
            ("q2", "Charge 2", "C", "U * r / (k * q1)", 3),
            ("r", "Separation", "m", "k * q1 * q2 / U", 4),
        ],
        "constants": [("k", 8.99e9)],
    },
    "Mirror Formula": {
        "variables": [
            ("f", "Focal length", "m", "1 / (1 / v + 1 / u)", 1),
            ("v", "Image distance", "m", "1 / (1 / f - 1 / u)", 2),
            ("u", "Object distance", "m", "1 / (1 / f - 1 / v)", 3),
        ],
        "constants": [],
    },
    "Impulse": {
        "variables": [
            ("J", "Impulse", "N*s", "F * delta_t", 1),
            ("F", "Force", "N", "J / delta_t", 2),
            ("delta_t", "Time interval", "s", "J / F", 3),
        ],
        "constants": [],
    },
    "Ideal Gas Equation": {
        "variables": [
            ("P", "Pressure", "Pa", "n * R * T / V", 1),
            ("V", "Volume", "m^3", "n * R * T / P", 2),
            ("n", "Moles", "mol", "P * V / (R * T)", 3),
            ("T", "Temperature", "K", "P * V / (n * R)", 4),
        ],
        "constants": [("R", 8.314)],
    },
    "Pressure": {
        "variables": [
            ("P", "Pressure", "Pa", "F / A", 1),
            ("F", "Force", "N", "P * A", 2),
            ("A", "Area", "m^2", "F / P", 3),
        ],
        "constants": [],
    },
    "Power": {
        "variables": [
            ("P", "Power", "W", "W_work / t", 1),
            ("W_work", "Work done", "J", "P * t", 2),
            ("t", "Time", "s", "W_work / P", 3),
        ],
        "constants": [],
    },
    "Stefan-Boltzmann Law": {
        "variables": [
            ("E", "Emitted power per unit area", "W/m^2", "sigma * T^4", 1),
            ("T", "Absolute temperature", "K", "(E / sigma)^(1/4)", 2),
        ],
        "constants": [("sigma", 5.67037e-8)],
    },
    "Heisenberg Uncertainty Principle": {
        "variables": [
            ("delta_x", "Uncertainty in position", "m", "h / (4 * pi * delta_p)", 1),
            ("delta_p", "Uncertainty in momentum", "kg*m/s", "h / (4 * pi * delta_x)", 2),
        ],
        "constants": [("h", 6.62607e-34), ("pi", 3.14159)],
    },
    "Time Period of Simple Pendulum": {
        "variables": [
            ("T", "Time period", "s", "2 * pi * sqrt(l / g)", 1),
            ("l", "Pendulum length", "m", "g * (T / (2 * pi))^2", 2),
        ],
        "constants": [("g", 9.81), ("pi", 3.14159)],
    },
    "Electric Power": {
        "variables": [
            ("P", "Electric power", "W", "V * I", 1),
            ("V", "Voltage", "V", "P / I", 2),
            ("I", "Current", "A", "P / V", 3),
        ],
        "constants": [],
    },
    "Electric Charge": {
        "variables": [
            ("Q", "Electric charge", "C", "I * t", 1),
            ("I", "Current", "A", "Q / t", 2),
            ("t", "Time", "s", "Q / I", 3),
        ],
        "constants": [],
    },
    "Escape Velocity": {
        "variables": [
            ("v", "Escape velocity", "m/s", "sqrt(2 * G * M / R)", 1),
            ("M", "Mass of planet", "kg", "v^2 * R / (2 * G)", 2),
            ("R", "Radius of planet", "m", "2 * G * M / (v^2)", 3),
        ],
        "constants": [("G", 6.6743e-11)],
    },
    "Gravitational Force": {
        "variables": [
            ("F", "Gravitational force", "N", "G * M * m / r^2", 1),
            ("M", "Mass 1", "kg", "F * r^2 / (G * m)", 2),
            ("m", "Mass 2", "kg", "F * r^2 / (G * M)", 3),
            ("r", "Distance", "m", "sqrt(G * M * m / F)", 4),
        ],
        "constants": [("G", 6.6743e-11)],
    },
    "Newton's First Law of Motion": {
        "variables": [
            ("F_net", "Net force", "N", "0", 1),
            ("a", "Acceleration", "m/s^2", "0", 2),
        ],
        "constants": [],
    },
    "Momentum": {
        "variables": [
            ("p", "Momentum", "kg*m/s", "m * v", 1),
            ("m", "Mass", "kg", "p / v", 2),
            ("v", "Velocity", "m/s", "p / m", 3),
        ],
        "constants": [],
    },
    "Ohm's Law": {
        "variables": [
            ("V", "Voltage", "V", "I * R", 1),
            ("I", "Current", "A", "V / R", 2),
            ("R", "Resistance", "ohm", "V / I", 3),
        ],
        "constants": [],
    },
    "Potential Energy": {
        "variables": [
            ("PE", "Potential energy", "J", "m * g * h", 1),
            ("m", "Mass", "kg", "PE / (g * h)", 2),
            ("h", "Height", "m", "PE / (m * g)", 3),
        ],
        "constants": [("g", 9.81)],
    },

    "Gravitational Potential Energy": {
        "variables": [
            ("U", "Potential energy", "J", "-G * M * m / r", 1),
            ("M", "Source mass", "kg", "-U * r / (G * m)", 2),
            ("m", "Object mass", "kg", "-U * r / (G * M)", 3),
            ("r", "Distance", "m", "-G * M * m / U", 4),
        ],
        "constants": [("G", 6.6743e-11)],
    },
    "NAND / NOR Gates (Universal Gates)": {
        "variables": [
            ("Y_nand", "NAND output", "", "1 if (A * B == 0) else 0", 1),
            ("A", "Input A (0 or 1)", "", "A", 2),
            ("B", "Input B (0 or 1)", "", "B", 3),
        ],
        "constants": [],
    },
    "Magnetic Field on Axis of a Circular Loop": {
        "variables": [
            ("B", "Magnetic field", "T", "mu_0 * N * I * R^2 / (2 * (R^2 + x^2)^(1.5))", 1),
            ("N", "Number of turns", "", "2 * B * (R^2 + x^2)^(1.5) / (mu_0 * I * R^2)", 2),
            ("I", "Current", "A", "2 * B * (R^2 + x^2)^(1.5) / (mu_0 * N * R^2)", 3),
            ("R", "Loop radius", "m", "R", 4),
            ("x", "Distance along axis", "m", "sqrt(((mu_0 * N * I * R^2 / (2 * B))^(2/3)) - R^2)", 5),
        ],
        "constants": [("mu_0", 1.2566e-6)],
    },
    "Torque on a Current Loop/ Magnetic Diople": {
        "variables": [
            ("tau", "Torque", "N*m", "M * B * sin(theta)", 1),
            ("M", "Magnetic moment", "A*m^2", "tau / (B * sin(theta))", 2),
            ("B", "Magnetic field", "T", "tau / (M * sin(theta))", 3),
            ("theta", "Angle to field", "rad", "asin(tau / (M * B))", 4),
        ],
        "constants": [],
    },
    "Magnetic Moment of a Revolving Electron": {
        "variables": [
            ("mu_e", "Magnetic moment", "A*m^2", "e * v * r / 2", 1),
            ("v", "Electron velocity", "m/s", "2 * mu_e / (e * r)", 2),
            ("r", "Orbit radius", "m", "2 * mu_e / (e * v)", 3),
        ],
        "constants": [("e", 1.602e-19)],
    },
    "Damped Oscillation Amplitude": {
        "variables": [
            ("A_t", "Amplitude at time t", "m", "A_0 * exp(-b * t / (2 * m))", 1),
            ("A_0", "Initial amplitude", "m", "A_t / exp(-b * t / (2 * m))", 2),
            ("b", "Damping constant", "kg/s", "-2 * m * log(A_t / A_0) / t", 3),
            ("m", "Mass", "kg", "-b * t / (2 * log(A_t / A_0))", 4),
            ("t", "Time", "s", "-2 * m * log(A_t / A_0) / b", 5),
        ],
        "constants": [],
    },
    "Bernoulli's Equation": {
        "variables": [
            ("P1", "Pressure 1", "Pa", "P2 + 0.5 * rho * (v2^2 - v1^2) + rho * g * (h2 - h1)", 1),
            ("P2", "Pressure 2", "Pa", "P1 + 0.5 * rho * (v1^2 - v2^2) + rho * g * (h1 - h2)", 2),
            ("v1", "Velocity 1", "m/s", "v1", 3),
            ("v2", "Velocity 2", "m/s", "v2", 4),
            ("rho", "Fluid density", "kg/m^3", "rho", 5),
        ],
        "constants": [("g", 9.81)],
    },
    "Principle of Homogeneity of Dimensions": {
        "variables": [
            ("LHS", "Dimension exponent", "", "RHS", 1),
            ("RHS", "Dimension exponent", "", "LHS", 2),
        ],
        "constants": [],
    },
    "Percentage (Relative) Error in a Product/Quotient": {
        "variables": [
            ("rel_err_Z", "Relative error in Z (%)", "%", "rel_err_A + rel_err_B", 1),
            ("rel_err_A", "Relative error in A (%)", "%", "rel_err_Z - rel_err_B", 2),
            ("rel_err_B", "Relative error in B (%)", "%", "rel_err_Z - rel_err_A", 3),
        ],
        "constants": [],
    },
}

class Command(BaseCommand):
    help = "Seeds FormulaVariable and FormulaConstant data"

    def handle(self, *args, **options):
        for title, data in CALCULATOR_DATA.items():
            # Use __iexact to avoid casing mismatches
            formula = Formula.objects.filter(title__iexact=title).first()

            if not formula:
                self.stdout.write(self.style.ERROR(f"Formula NOT found: '{title}'"))
                continue

            # Delete old entries to prevent duplicates/stale data
            FormulaVariable.objects.filter(formula=formula).delete()
            FormulaConstant.objects.filter(formula=formula).delete()

            for symbol, name, unit, expr, order in data["variables"]:
                FormulaVariable.objects.create(
                    formula=formula,
                    symbol=symbol,
                    name=name,
                    unit=unit,
                    expr=expr,
                    is_solvable=True, # IMPORTANT: Must be True
                    order=order,
                )
            for symbol, value in data["constants"]:
                FormulaConstant.objects.create(
                    formula=formula,
                    symbol=symbol,
                    value=value,
                )
            self.stdout.write(self.style.SUCCESS(f"Successfully re-seeded: '{formula.title}'"))
