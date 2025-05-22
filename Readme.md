# Divergence and Spirals: Visualizing Scan Speedup

This Streamlit application demonstrates how increasing laser beam divergence can reduce the time required for spiral scanning.

## Purpose

The primary purpose of this application is to provide a visual and quantitative understanding of the relationship between laser beam divergence and spiral scan speed. By adjusting various input parameters, users can observe the potential speedup achievable in spiral scanning tasks.

## Inputs

The application allows users to configure the following parameters:

-   **Acquisition Margin (dB):** The signal-to-noise ratio margin required for successful acquisition. This affects how much the beam can be diverged.
-   **Uncertainty Cone to Scan (µrad):** The angular extent of the area that needs to be scanned.
-   **Scan Velocity (rad/s):** The angular speed at which the scanner operates.
-   **Spiral Arm Distance (µrad):** The separation between adjacent arms of the spiral pattern.

## Predefined Scenarios

The application includes a selection of predefined scenarios to help users quickly explore different configurations:

-   **Default Balanced:** A standard set of parameters representing a typical use case.
    -   Acquisition Margin: 5 dB
    -   Uncertainty Cone to Scan: 1000 µrad
    -   Scan Velocity: 0.31 rad/s
    -   Spiral Arm Distance: 5.6 µrad
-   **Short-Range, High-Speed:** Optimized for scenarios where the scanning range is smaller, allowing for faster scan velocities and potentially wider spiral arm distances.
    -   Acquisition Margin: 3 dB
    -   Uncertainty Cone to Scan: 700 µrad
    -   Scan Velocity: 0.4 rad/s
    -   Spiral Arm Distance: 7.0 µrad
-   **Long-Range, Max Sensitivity:** Tailored for scenarios requiring longer scanning distances, often necessitating lower scan velocities and tighter spiral arm distances to maintain sensitivity.
    -   Acquisition Margin: 10 dB
    -   Uncertainty Cone to Scan: 1500 µrad
    -   Scan Velocity: 0.2 rad/s
    -   Spiral Arm Distance: 4.0 µrad

Users can select a scenario from a dropdown menu in the sidebar. This will automatically populate the input fields with the scenario's parameters, which can then be further adjusted if needed.

## Outputs and Visualizations

Based on the input parameters, the application generates the following outputs and visualizations:

-   **Total Spiral Speedup:** A numerical value indicating the overall reduction in scan time achieved by increasing divergence.
-   **Acquisition Margin (linear):** The acquisition margin converted to a linear scale.
-   **Spiral Arm Distance Speedup:** The speedup factor specifically due to the change in spiral arm distance.
-   **Spiral Velocity Speedup:** The speedup factor specifically due to the change in scan velocity.
-   **Spiral Animation:** A visual comparison of the original spiral scan pattern and the speedup spiral scan pattern. This animation highlights how the increased divergence allows for a faster scan.
-   **Scan Time vs. Radius Chart:** A line chart that plots the scan time against the radius for both the original and speedup spirals, providing a clear comparison of their efficiencies.
-   **Laser Beam Divergence Animation:** An animation illustrating the concept of laser beam divergence and how it changes.

## How to Run the Application

1.  **Ensure you have Python and Streamlit installed.** If not, you can install Streamlit using pip:
    ```bash
    pip install streamlit
    ```
2.  **Navigate to the directory containing the application file.**
3.  **Run the application using the following command in your terminal:**
    ```bash
    streamlit run spiral_app_with_scenarios.py
    ```
    **Note on Filename:** The application script is now `spiral_app_with_scenarios.py`. This change was made due to technical difficulties encountered with the original filename `1_🌀divergence_and_spirals.py` which contained a special character (`🌀`) causing issues with development tools. You may wish to delete the old file and/or rename `spiral_app_with_scenarios.py` if desired, keeping in mind potential future tool interactions if special characters are reintroduced.

4.  The application will open in your default web browser. You can then interact with the input controls and observe the resulting visualizations.