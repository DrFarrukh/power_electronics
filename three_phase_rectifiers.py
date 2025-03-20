import numpy as np
from scipy.signal import lfilter

def simulate_three_phase_uncontrolled(t, amplitude, frequency, load_resistance, load_inductance):
    """
    Simulate a three-phase uncontrolled rectifier (six-pulse bridge).
    
    Parameters:
    -----------
    t : array
        Time array for simulation
    amplitude : float
        Peak amplitude of input voltage (phase voltage)
    frequency : float
        Frequency of input voltage in Hz
    load_resistance : float
        Load resistance in ohms
    load_inductance : float
        Load inductance in henries
        
    Returns:
    --------
    input_voltage : array
        Input voltage waveforms (3 phases)
    output_voltage : array
        Output voltage waveform
    output_current : array
        Output current waveform
    """
    omega = 2 * np.pi * frequency
    
    # Generate three-phase input voltages (120° phase shift)
    phase_a = amplitude * np.sin(omega * t)
    phase_b = amplitude * np.sin(omega * t - 2*np.pi/3)
    phase_c = amplitude * np.sin(omega * t - 4*np.pi/3)
    
    # Combine phases into a single array for return
    input_voltage = np.vstack((phase_a, phase_b, phase_c))
    
    # For three-phase uncontrolled bridge, output is the maximum of the line-to-line voltages
    line_ab = phase_a - phase_b
    line_bc = phase_b - phase_c
    line_ca = phase_c - phase_a
    
    # Calculate the instantaneous output voltage (envelope of the highest line-to-line voltage)
    output_voltage = np.zeros_like(t)
    for i in range(len(t)):
        # Get the maximum absolute line-to-line voltage
        max_line = max(abs(line_ab[i]), abs(line_bc[i]), abs(line_ca[i]))
        
        # Determine which line-to-line voltage has the maximum absolute value
        if abs(line_ab[i]) == max_line:
            output_voltage[i] = abs(line_ab[i])
        elif abs(line_bc[i]) == max_line:
            output_voltage[i] = abs(line_bc[i])
        else:
            output_voltage[i] = abs(line_ca[i])
    
    # In a three-phase bridge, the output voltage is approximately 1.35 times the phase voltage
    # This is a simplification of the actual behavior
    output_voltage = output_voltage * np.sqrt(3)/2
    
    # Calculate output current based on RL load
    if load_inductance > 0:
        # For inductive load, use filter to model the inductor effect
        tau = load_inductance / load_resistance
        dt = t[1] - t[0]
        alpha = dt / (tau + dt)
        output_current = lfilter([alpha], [1, -(1-alpha)], output_voltage / load_resistance)
    else:
        # For purely resistive load
        output_current = output_voltage / load_resistance
    
    return input_voltage, output_voltage, output_current


def simulate_three_phase_controlled(t, amplitude, frequency, firing_angle, load_resistance, load_inductance):
    """
    Simulate a three-phase controlled rectifier (six-pulse bridge with SCRs).
    
    Parameters:
    -----------
    t : array
        Time array for simulation
    amplitude : float
        Peak amplitude of input voltage (phase voltage)
    frequency : float
        Frequency of input voltage in Hz
    firing_angle : float
        Firing angle in degrees
    load_resistance : float
        Load resistance in ohms
    load_inductance : float
        Load inductance in henries
        
    Returns:
    --------
    input_voltage : array
        Input voltage waveforms (3 phases)
    output_voltage : array
        Output voltage waveform
    output_current : array
        Output current waveform
    """
    omega = 2 * np.pi * frequency
    period = 1 / frequency
    firing_angle_rad = np.deg2rad(firing_angle)
    
    # Generate three-phase input voltages (120° phase shift)
    phase_a = amplitude * np.sin(omega * t)
    phase_b = amplitude * np.sin(omega * t - 2*np.pi/3)
    phase_c = amplitude * np.sin(omega * t - 4*np.pi/3)
    
    # Combine phases into a single array for return
    input_voltage = np.vstack((phase_a, phase_b, phase_c))
    
    # For three-phase controlled bridge, we need to calculate the line-to-line voltages
    line_ab = phase_a - phase_b
    line_bc = phase_b - phase_c
    line_ca = phase_c - phase_a
    
    # Calculate the natural commutation points (60° intervals)
    commutation_interval = period / 6
    
    # Initialize output voltage array
    output_voltage = np.zeros_like(t)
    
    # Process each 60° interval
    for i in range(int(np.ceil(t[-1] / commutation_interval))):
        interval_start = i * commutation_interval
        interval_end = (i + 1) * commutation_interval
        
        # Find indices for this interval
        interval_indices = (t >= interval_start) & (t < interval_end)
        
        # Skip if no points in this interval
        if not np.any(interval_indices):
            continue
        
        # Calculate firing time within interval
        firing_time = interval_start + firing_angle_rad / omega
        
        # Find indices after firing time
        conduction_indices = (t >= firing_time) & (t < interval_end)
        
        # Determine which line-to-line voltage is active in this interval
        # This is a simplified model - in reality, the commutation sequence is more complex
        active_line = i % 6
        
        if active_line == 0:
            line_voltage = line_ab
        elif active_line == 1:
            line_voltage = -line_ca
        elif active_line == 2:
            line_voltage = line_bc
        elif active_line == 3:
            line_voltage = -line_ab
        elif active_line == 4:
            line_voltage = line_ca
        else:  # active_line == 5
            line_voltage = -line_bc
        
        # Set output voltage during conduction
        if np.any(conduction_indices):
            output_voltage[conduction_indices] = abs(line_voltage[conduction_indices])
    
    # Apply the scaling factor for three-phase bridge
    output_voltage = output_voltage * np.sqrt(3)/2
    
    # Apply the effect of firing angle on average output voltage
    # For controlled rectifier, average voltage is proportional to cos(alpha)
    output_voltage = output_voltage * np.cos(firing_angle_rad)
    
    # Calculate output current based on RL load
    if load_inductance > 0:
        # For inductive load, use filter to model the inductor effect
        tau = load_inductance / load_resistance
        dt = t[1] - t[0]
        alpha = dt / (tau + dt)
        output_current = lfilter([alpha], [1, -(1-alpha)], output_voltage / load_resistance)
    else:
        # For purely resistive load
        output_current = output_voltage / load_resistance
    
    return input_voltage, output_voltage, output_current
