# ⚛️ Pygame Physics Simulations

This repository contains a collection of interactive physics simulations developed using the Pygame library in Python. Each simulation visually and customizably demonstrates fundamental concepts of mechanics and dynamics.

The primary goal of this project is to serve as a practical foundation for creating controlled physics scenarios.

## ✨ Included Simulations

### 1. Projectile Motion (`projectile_motion.py`)

A simulation of a projectile in parabolic motion under the influence of gravity.

**Features:**
* **Customizable Inputs:** Define initial velocity, launch angle, and initial height via interactive text boxes.
* **Real-World Scaling:** All quantities are converted and displayed in real-world units (meters, m/s, m/s²).
* **Trajectory Visualization:** Visual trail of the projectile's path.
* **Velocity Vectors:** Arrows indicating the magnitude and direction of horizontal (Vx) and vertical (Vy) velocity components.
* **Real-Time Metrics:** Continuous display of position (X, Y), velocity components, time of flight, horizontal range, and maximum height reached.
* **Controls:** "LAUNCH" button to start the simulation and 'R' key to reset the simulation to the current input values.

### 2. Simple Pendulum (`simple_pendulum.py`)

A simulation of a simple pendulum oscillating under gravity.

**Features:**
* **Customizable Inputs:** Define string length, bob mass, and initial angle.
* **Real-World Scaling:** Quantities converted to real-world units.
* **Oscillation Visualization:** Smooth pendulum motion.
* **Real-Time Metrics:** Display of length, mass, current angle, angular velocity, and total simulation time.
* **Energy Visualization:** Continuous calculation and display of the system's Potential Energy (PE), Kinetic Energy (KE), and Total Energy (TE), demonstrating energy conservation.
* **Controls:** "START" button to begin oscillation and 'R' key to reset the simulation (keeping input values).

### 3. Double Pendulum (`double_pendulum.py`)

A simulation of a double pendulum system, known for its chaotic behavior and extreme sensitivity to initial conditions.

**Features:**
* **Customizable Inputs:** Define lengths (L1, L2), masses (M1, M2), and initial angles (Theta1, Theta2) for both pendulum segments.
* **Real-World Scaling:** Quantities converted to real-world units.
* **Dynamic Visualization:** Clear visual representation of both pendulum segments and bobs.
* **Chaotic Trajectory:** Trajectory trail for the second bob to visualize the system's unpredictable behavior.
* **Real-Time Metrics:** Continuous display of lengths, masses, angles, and angular velocities for both segments, plus total simulation time.
* **Controls:** "START" button to begin the simulation and 'R' key to reset (keeping input values).

## 🚀 How to Run

To run these simulations, follow the steps below:

1.  **Prerequisites:**
    * Ensure you have [Python 3.x](https://www.python.org/downloads/) installed on your system.
    * You will need the Pygame library.

2.  **Pygame Installation:**
    Open your terminal or command prompt and execute:
    ```bash
    pip install pygame
    ```

3.  **Clone the Repository (or Download Files):**
    If you have Git, you can clone the repository:
    ```bash
    git clone [https://github.com/YourUsername/YourRepository.git](https://github.com/YourUsername/YourRepository.git)
    cd YourRepository
    ```
    Alternatively, download the ZIP files directly from GitHub and extract them to a folder.

4.  **Execute the Simulation:**
    Navigate to the folder where you saved the files (using `cd your_folder_name` in the terminal) and run the desired file:
    ```bash
    python projectile_motion.py
    # or
    python simple_pendulum.py
    # or
    python double_pendulum.py
    ```

## 💡 Next Steps & Possible Enhancements

This project serves as a starting point. Future enhancements could include:
* **Graphing Modes:** Add real-time plotting of metrics (e.g., energy vs. time, angle vs. time).
* **Collision Detection:** Implement collisions for projectiles with boundaries/other objects.
* **UI Enhancements:** Improvements to the user interface (sliders, more buttons).
* **Multi-Body Simulation:** Add more interacting projectiles or pendulums.
* **Damping and Forcing:** Add air resistance or controllable external forces to the pendulums.
