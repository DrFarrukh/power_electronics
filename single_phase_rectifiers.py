import numpy as np
from scipy.signal import lfilter

def simulate_half_wave_uncontrolled(t, amplitude, frequency, load_resistance, load_inductance):
    """
    Simulate a single-phase half-wave uncontrolled rectifier.
    
    Parameters:
    -----------
    t : array
        Time array for simulation
    amplitude : float
        Peak amplitude of input voltage
    frequency : float
        Frequency of input voltage in Hz
    load_resistance : float
        Load resistance in ohms
    load_inductance : float
        Load inductance in henries
        
    Returns:
    --------
    input_voltage : array
        Input voltage waveform
    output_voltage : array
        Output voltage waveform
    output_current : array
        Output current waveform
    """
    omega = 2 * np.pi * frequency
    
    # Input voltage (sinusoidal)
    input_voltage = amplitude * np.sin(omega * t)
    
    # For half-wave uncontrolled rectifier, output voltage is positive half of input
    output_voltage = np.maximum(0, input_voltage)
    
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


def simulate_full_wave_uncontrolled(t, amplitude, frequency, load_resistance, load_inductance):
    """
    Simulate a single-phase full-wave uncontrolled rectifier.
    
    Parameters:
    -----------
    t : array
        Time array for simulation
    amplitude : float
        Peak amplitude of input voltage
    frequency : float
        Frequency of input voltage in Hz
    load_resistance : float
        Load resistance in ohms
    load_inductance : float
        Load inductance in henries
        
    Returns:
    --------
    input_voltage : array
        Input voltage waveform
    output_voltage : array
        Output voltage waveform
    output_current : array
        Output current waveform
    """
    omega = 2 * np.pi * frequency
    
    # Input voltage (sinusoidal)
    input_voltage = amplitude * np.sin(omega * t)
    
    # For full-wave uncontrolled rectifier, output voltage is absolute value of input
    output_voltage = np.abs(input_voltage)
    
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


def simulate_half_wave_controlled(t, amplitude, frequency, firing_angle, load_resistance, load_inductance):
    """
    Simulate a single-phase half-wave controlled rectifier.
    
    Parameters:
    -----------
    t : array
        Time array for simulation
    amplitude : float
        Peak amplitude of input voltage
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
        Input voltage waveform
    output_voltage : array
        Output voltage waveform
    output_current : array
        Output current waveform
    """
    omega = 2 * np.pi * frequency
    period = 1 / frequency
    firing_angle_rad = np.deg2rad(firing_angle)
    
    # Input voltage (sinusoidal)
    input_voltage = amplitude * np.sin(omega * t)
    
    # Initialize output voltage array
    output_voltage = np.zeros_like(input_voltage)
    
    # Calculate firing time within each cycle
    for i in range(int(np.ceil(t[-1] * frequency))):
        # Start and end of this cycle
        cycle_start = i * period
        cycle_end = (i + 1) * period
        
        # Find indices for this cycle
        cycle_indices = (t >= cycle_start) & (t < cycle_end)
        
        # Calculate time within cycle
        cycle_time = t[cycle_indices] - cycle_start
        
        # Calculate firing time within cycle
        firing_time = firing_angle_rad / omega
        
        # Calculate conduction period
        conduction_indices = (cycle_time >= firing_time) & (cycle_time < (period/2))
        
        # Set output voltage during conduction
        if np.any(conduction_indices):
            cycle_voltage = input_voltage[cycle_indices]
            output_voltage[cycle_indices] = np.where(
                conduction_indices,
                np.maximum(0, cycle_voltage),  # Only positive values during conduction
                0
            )
    
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


def simulate_full_wave_controlled(t, amplitude, frequency, firing_angle, load_resistance, load_inductance):
    """
    Simulate a single-phase full-wave controlled rectifier.
    
    Parameters:
    -----------
    t : array
        Time array for simulation
    amplitude : float
        Peak amplitude of input voltage
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
        Input voltage waveform
    output_voltage : array
        Output voltage waveform
    output_current : array
        Output current waveform
    """
    omega = 2 * np.pi * frequency
    period = 1 / frequency
    half_period = period / 2
    firing_angle_rad = np.deg2rad(firing_angle)
    
    # Input voltage (sinusoidal)
    input_voltage = amplitude * np.sin(omega * t)
    
    # Initialize output voltage array
    output_voltage = np.zeros_like(input_voltage)
    
    # Calculate firing time within each half-cycle
    for i in range(int(np.ceil(t[-1] * frequency * 2))):
        # Start and end of this half-cycle
        half_cycle_start = i * half_period
        half_cycle_end = (i + 1) * half_period
        
        # Find indices for this half-cycle
        half_cycle_indices = (t >= half_cycle_start) & (t < half_cycle_end)
        
        # Calculate time within half-cycle
        half_cycle_time = t[half_cycle_indices] - half_cycle_start
        
        # Calculate firing time within half-cycle
        firing_time = firing_angle_rad / omega
        
        # Calculate conduction period
        conduction_indices = half_cycle_time >= firing_time
        
        # Set output voltage during conduction
        if np.any(conduction_indices):
            # For positive half-cycle
            if i % 2 == 0:
                half_cycle_voltage = np.abs(input_voltage[half_cycle_indices])
            # For negative half-cycle
            else:
                half_cycle_voltage = np.abs(input_voltage[half_cycle_indices])
            
            output_voltage[half_cycle_indices] = np.where(
                conduction_indices,
                half_cycle_voltage,
                0
            )
    
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
