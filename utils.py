import numpy as np
import streamlit as st
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import matplotlib.pyplot as plt
import io
import base64
from PIL import Image

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
    # Create subplots with 3 rows
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
    
    # Plot output voltage
    fig.add_trace(
        go.Scatter(x=t, y=output_voltage, name="Output Voltage", line=dict(color='red')),
        row=2, col=1
    )
    
    # Plot output current
    fig.add_trace(
        go.Scatter(x=t, y=output_current, name="Output Current", line=dict(color='green')),
        row=3, col=1
    )
    
    # Update layout
    fig.update_layout(
        height=700,
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
    fig.update_yaxes(title_text="Voltage (V)", row=2, col=1)
    fig.update_yaxes(title_text="Current (A)", row=3, col=1)
    
    # Update x-axis label
    fig.update_xaxes(title_text="Time (s)", row=3, col=1)
    
    # Display the plot
    st.plotly_chart(fig, use_container_width=True)

def plot_circuit_diagram(rectifier_type):
    """
    Display circuit diagram for the selected rectifier type.
    
    Parameters:
    -----------
    rectifier_type : str
        Type of rectifier being simulated
    """
    # Create a matplotlib figure for the circuit diagram
    fig, ax = plt.subplots(figsize=(10, 6))
    
    # Remove axis ticks and labels
    ax.set_xticks([])
    ax.set_yticks([])
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['bottom'].set_visible(False)
    ax.spines['left'].set_visible(False)
    
    # Draw circuit diagram based on rectifier type
    if rectifier_type == "Half-Wave Uncontrolled":
        draw_half_wave_uncontrolled(ax)
    elif rectifier_type == "Full-Wave Uncontrolled":
        draw_full_wave_uncontrolled(ax)
    elif rectifier_type == "Half-Wave Controlled":
        draw_half_wave_controlled(ax)
    elif rectifier_type == "Full-Wave Controlled":
        draw_full_wave_controlled(ax)
    elif rectifier_type == "Three-Phase Uncontrolled":
        draw_three_phase_uncontrolled(ax)
    elif rectifier_type == "Three-Phase Controlled":
        draw_three_phase_controlled(ax)
    
    # Save figure to a buffer
    buf = io.BytesIO()
    fig.savefig(buf, format='png')
    buf.seek(0)
    
    # Display the image in Streamlit
    st.image(buf, use_column_width=True)
    plt.close(fig)

# Helper functions to draw circuit diagrams
def draw_half_wave_uncontrolled(ax):
    ax.text(0.5, 0.5, """
    AC Source                Diode                 Load
        ~                     |>|                  /\/\/
        |                      |                    |
        |----------------------|--------------------| 
        |                                           |
        |-------------------------------------------|
    """, fontsize=14, family='monospace')
    ax.set_title("Half-Wave Uncontrolled Rectifier Circuit", fontsize=16)

def draw_full_wave_uncontrolled(ax):
    ax.text(0.5, 0.5, """
                    |>|
                 |------|
                 |      |
    AC Source    |      |     Load
        ~        |      |    /\/\/
        |        |      |     |
        |--------|------|-----|
        |        |      |     |
        |        |      |     |
                 |------|     
                    |>|       
    """, fontsize=14, family='monospace')
    ax.set_title("Full-Wave Uncontrolled Rectifier Circuit (Bridge)", fontsize=16)

def draw_half_wave_controlled(ax):
    ax.text(0.5, 0.5, """
    AC Source                SCR                  Load
        ~                    /|                   /\/\/
        |                   / |                    |
        |-------------------  --------------------| 
        |                                          |
        |------------------------------------------|
                           Gate
                            |
                            v
    """, fontsize=14, family='monospace')
    ax.set_title("Half-Wave Controlled Rectifier Circuit", fontsize=16)

def draw_full_wave_controlled(ax):
    ax.text(0.5, 0.5, """
                    SCR1
                     /|
                 |---  |
                 |      |
    AC Source    |      |     Load
        ~        |      |    /\/\/
        |        |      |     |
        |--------|------|-----|
        |        |      |     |
        |        |      |     |
                 |---  |     
                     /|       
                    SCR2
    """, fontsize=14, family='monospace')
    ax.set_title("Full-Wave Controlled Rectifier Circuit", fontsize=16)

def draw_three_phase_uncontrolled(ax):
    ax.text(0.5, 0.5, """
    Three-Phase Source         Diode Bridge            Load
                                                      /\/\/
        A o---------o----|>|----o----|>|----o---------o
                    |                 |                |
        B o---------|----o----|>|----o                |
                    |    |                            |
        C o---------|----|----|>|----o                |
                    |    |         |                  |
                    o----|---------|------------------o
                         |         |
                         o----|>|--o
    """, fontsize=12, family='monospace')
    ax.set_title("Three-Phase Uncontrolled Rectifier Circuit", fontsize=16)

def draw_three_phase_controlled(ax):
    ax.text(0.5, 0.5, """
    Three-Phase Source         SCR Bridge             Load
                                                     /\/\/
        A o---------o----/|----o----/|----o---------o
                    |                 |              |
        B o---------|----o----/|----o                |
                    |    |                           |
        C o---------|----|----|/----o                |
                    |    |         |                 |
                    o----|---------|-----------------o
                         |         |
                         o----/|---o
                         
                         Gate Control
    """, fontsize=12, family='monospace')
    ax.set_title("Three-Phase Controlled Rectifier Circuit", fontsize=16)
