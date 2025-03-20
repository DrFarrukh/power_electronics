import numpy as np
import streamlit as st
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import matplotlib.pyplot as plt
import io
import base64
from PIL import Image

def generate_gate_pulses(t, rectifier_type):
    """
    Generate gate pulse signals for controlled rectifiers.
    
    Parameters:
    -----------
    t : array
        Time array for simulation
    rectifier_type : str
        Type of rectifier being simulated
        
    Returns:
    --------
    gate_pulses : array or list of arrays
        Gate pulse waveforms
    """
    # Get frequency from time array (assuming at least 2 cycles)
    cycle_time = t[-1] / 2
    frequency = 1 / cycle_time
    omega = 2 * np.pi * frequency
    
    # Get firing angle from the rectifier type name (default to 30 degrees if not found)
    import re
    match = re.search(r'firing angle: (\d+)', rectifier_type.lower())
    firing_angle = 30 if not match else int(match.group(1))
    firing_time = np.deg2rad(firing_angle) / omega
    
    # Generate appropriate gate pulses based on rectifier type
    if "Three-Phase" in rectifier_type:
        # For three-phase controlled rectifier (6 SCRs)
        gate_pulses = []
        phase_shift = 2 * np.pi / 6  # 60 degrees phase shift between SCRs
        
        for i in range(6):
            pulse = np.zeros_like(t)
            for cycle in range(int(np.ceil(t[-1] * frequency))):
                cycle_start = cycle / frequency
                # Each SCR fires once per cycle with appropriate phase shift
                trigger_time = cycle_start + firing_time + (i * phase_shift / omega)
                pulse_width = 0.002  # 2ms pulse width
                
                # Set pulse high for the duration of the pulse width
                pulse_indices = (t >= trigger_time) & (t < trigger_time + pulse_width)
                pulse[pulse_indices] = 1.0
            
            gate_pulses.append(pulse)
        
        return gate_pulses
    
    elif "Half-Wave" in rectifier_type:
        # For single-phase half-wave controlled rectifier (1 SCR)
        pulse = np.zeros_like(t)
        
        for cycle in range(int(np.ceil(t[-1] * frequency))):
            cycle_start = cycle / frequency
            # SCR fires once per cycle
            trigger_time = cycle_start + firing_time
            pulse_width = 0.002  # 2ms pulse width
            
            # Set pulse high for the duration of the pulse width
            pulse_indices = (t >= trigger_time) & (t < trigger_time + pulse_width)
            pulse[pulse_indices] = 1.0
        
        return [pulse]
    
    else:  # Full-Wave Controlled
        # For single-phase full-wave controlled rectifier (2 SCRs)
        pulse1 = np.zeros_like(t)
        pulse2 = np.zeros_like(t)
        half_cycle = 1 / (2 * frequency)
        
        for cycle in range(int(np.ceil(t[-1] * frequency * 2))):
            half_cycle_start = cycle * half_cycle
            # Each SCR fires once per half-cycle, alternating
            trigger_time = half_cycle_start + firing_time
            pulse_width = 0.002  # 2ms pulse width
            
            # Set appropriate pulse high based on which half-cycle we're in
            pulse_indices = (t >= trigger_time) & (t < trigger_time + pulse_width)
            
            if cycle % 2 == 0:
                pulse1[pulse_indices] = 1.0
            else:
                pulse2[pulse_indices] = 1.0
        
        return [pulse1, pulse2]

def calculate_metrics(input_voltage, output_voltage, output_current, load_resistance):
    """
    Calculate performance metrics for a rectifier circuit.
    
    Parameters:
    -----------
    input_voltage : array
        Input voltage waveform
    output_voltage : array
        Output voltage waveform
    output_current : array
        Output current waveform
    load_resistance : float
        Load resistance in ohms
        
    Returns:
    --------
    metrics : dict
        Dictionary containing calculated metrics
    """
    # If input_voltage is 2D (for three-phase), use RMS of all phases
    if len(input_voltage.shape) > 1:
        input_voltage_rms = np.sqrt(np.mean(input_voltage**2))
    else:
        input_voltage_rms = np.sqrt(np.mean(input_voltage**2))
    
    # Calculate average (DC) output voltage
    avg_voltage = np.mean(output_voltage)
    
    # Calculate RMS output voltage
    rms_voltage = np.sqrt(np.mean(output_voltage**2))
    
    # Calculate ripple factor
    ac_component = np.sqrt(rms_voltage**2 - avg_voltage**2)
    ripple_factor = ac_component / avg_voltage if avg_voltage > 0 else 0
    
    # Calculate form factor
    form_factor = rms_voltage / avg_voltage if avg_voltage > 0 else 0
    
    # Calculate average and RMS output current
    avg_current = np.mean(output_current)
    rms_current = np.sqrt(np.mean(output_current**2))
    
    # Calculate output power
    output_power = avg_voltage * avg_current
    
    # Calculate input power (approximate)
    input_power = input_voltage_rms * rms_current
    
    # Calculate efficiency
    efficiency = (output_power / input_power * 100) if input_power > 0 else 0
    
    # Return all metrics as a dictionary
    return {
        'avg_voltage': avg_voltage,
        'rms_voltage': rms_voltage,
        'ripple_factor': ripple_factor,
        'form_factor': form_factor,
        'avg_current': avg_current,
        'rms_current': rms_current,
        'output_power': output_power,
        'efficiency': efficiency
    }

def plot_waveforms(t, input_voltage, output_voltage, output_current, rectifier_type):
    """
    Plot input and output waveforms using Plotly.
    
    Parameters:
    -----------
    t : array
        Time array for simulation
    input_voltage : array
        Input voltage waveform
    output_voltage : array
        Output voltage waveform
    output_current : array
        Output current waveform
    rectifier_type : str
        Type of rectifier being simulated
    """
    # Determine if we need to show gate pulses (for controlled rectifiers)
    show_gate_pulses = "Controlled" in rectifier_type
    
    # Create subplots with appropriate number of rows
    if show_gate_pulses:
        fig = make_subplots(rows=4, cols=1, 
                          subplot_titles=("Input Voltage", "Gate Pulses", "Output Voltage", "Output Current"),
                          shared_xaxes=True,
                          vertical_spacing=0.08,
                          row_heights=[0.25, 0.15, 0.3, 0.3])
    else:
        fig = make_subplots(rows=3, cols=1, 
                          subplot_titles=("Input Voltage", "Output Voltage", "Output Current"),
                          shared_xaxes=True,
                          vertical_spacing=0.1)
    
    # Plot input voltage
    if len(input_voltage.shape) > 1:  # For three-phase input
        for i, phase in enumerate(['Phase A', 'Phase B', 'Phase C']):
            fig.add_trace(
                go.Scatter(x=t, y=input_voltage[i], name=phase),
                row=1, col=1
            )
    else:  # For single-phase input
        fig.add_trace(
            go.Scatter(x=t, y=input_voltage, name="Input Voltage"),
            row=1, col=1
        )
    
    # Add gate pulses for controlled rectifiers
    if show_gate_pulses:
        # Generate gate pulses based on rectifier type
        gate_pulses = generate_gate_pulses(t, rectifier_type)
        
        # Plot gate pulses
        if "Three-Phase" in rectifier_type:
            # For three-phase, show multiple gate signals
            for i, pulse_name in enumerate(['SCR1', 'SCR2', 'SCR3', 'SCR4', 'SCR5', 'SCR6']):
                # Offset each pulse for better visualization
                offset = i * 0.2
                fig.add_trace(
                    go.Scatter(x=t, y=gate_pulses[i] + offset, name=pulse_name, line=dict(width=2)),
                    row=2, col=1
                )
        else:
            # For single-phase, show one or two gate signals
            if "Half-Wave" in rectifier_type:
                fig.add_trace(
                    go.Scatter(x=t, y=gate_pulses[0], name="SCR Gate", line=dict(width=2, color='purple')),
                    row=2, col=1
                )
            else:  # Full-Wave
                fig.add_trace(
                    go.Scatter(x=t, y=gate_pulses[0], name="SCR1 Gate", line=dict(width=2, color='purple')),
                    row=2, col=1
                )
                fig.add_trace(
                    go.Scatter(x=t, y=gate_pulses[1] + 0.2, name="SCR2 Gate", line=dict(width=2, color='darkblue')),
                    row=2, col=1
                )
    
    # Plot output voltage
    output_row = 3 if show_gate_pulses else 2
    fig.add_trace(
        go.Scatter(x=t, y=output_voltage, name="Output Voltage", line=dict(color='red')),
        row=output_row, col=1
    )
    
    # Plot output current
    output_row = 4 if show_gate_pulses else 3
    fig.add_trace(
        go.Scatter(x=t, y=output_current, name="Output Current", line=dict(color='green')),
        row=output_row, col=1
    )
    
    # Update layout
    fig.update_layout(
        height=800 if show_gate_pulses else 700,
        title_text=f"{rectifier_type} Waveforms",
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        )
    )
    
    # Update y-axis labels
    fig.update_yaxes(title_text="Voltage (V)", row=1, col=1)
    
    if show_gate_pulses:
        fig.update_yaxes(title_text="Gate Signal", row=2, col=1)
        fig.update_yaxes(title_text="Voltage (V)", row=3, col=1)
        fig.update_yaxes(title_text="Current (A)", row=4, col=1)
        fig.update_xaxes(title_text="Time (s)", row=4, col=1)
    else:
        fig.update_yaxes(title_text="Voltage (V)", row=2, col=1)
        fig.update_yaxes(title_text="Current (A)", row=3, col=1)
        fig.update_xaxes(title_text="Time (s)", row=3, col=1)
    
    # Display the plot
    st.plotly_chart(fig, use_container_width=True)

# Circuit diagram functions have been removed as requested
