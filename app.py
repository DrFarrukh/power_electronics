import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# Import circuit modules
from single_phase_rectifiers import (
    simulate_half_wave_uncontrolled,
    simulate_full_wave_uncontrolled,
    simulate_half_wave_controlled,
    simulate_full_wave_controlled
)

from three_phase_rectifiers import (
    simulate_three_phase_uncontrolled,
    simulate_three_phase_controlled
)

from utils import (
    calculate_metrics,
    plot_waveforms
)

# Set page configuration
st.set_page_config(
    page_title="Power Electronics Rectifier Simulator",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        color: #1E88E5;
        text-align: center;
    }
    .sub-header {
        font-size: 1.5rem;
        color: #0D47A1;
    }
    .info-text {
        background-color: #E3F2FD;
        padding: 1rem;
        border-radius: 5px;
    }
    .metric-card {
        background-color: #F5F5F5;
        padding: 1rem;
        border-radius: 5px;
        text-align: center;
    }
</style>
""", unsafe_allow_html=True)

# Application title and introduction
st.markdown("<h1 class='main-header'>Power Electronics Rectifier Simulator</h1>", unsafe_allow_html=True)

st.markdown("""
This interactive application allows you to explore and understand various types of rectifier circuits 
used in power electronics. You can adjust parameters in real-time and observe their effects on the circuit behavior.
""")

# Sidebar for circuit selection and parameters
st.sidebar.markdown("<h2 class='sub-header'>Circuit Configuration</h2>", unsafe_allow_html=True)

# Circuit type selection
circuit_type = st.sidebar.selectbox(
    "Select Circuit Type",
    ["Single-Phase Rectifiers", "Three-Phase Rectifiers"]
)

# Parameters common to all circuits
frequency = st.sidebar.slider("Input Frequency (Hz)", 50, 60, 50)
amplitude = st.sidebar.slider("Input Voltage Amplitude (V)", 100, 500, 220)
load_resistance = st.sidebar.slider("Load Resistance (Ω)", 100, 1000, 10)
load_inductance = st.sidebar.slider("Load Inductance (mH)", 0, 1000, 0)

# Time parameters for simulation
cycles = st.sidebar.slider("Number of Cycles to Display", 1, 5, 2)
t = np.linspace(0, cycles/frequency, 1000*cycles)

# Single-Phase Rectifier options
if circuit_type == "Single-Phase Rectifiers":
    rectifier_type = st.sidebar.selectbox(
        "Rectifier Type",
        ["Half-Wave Uncontrolled", "Full-Wave Uncontrolled", 
         "Half-Wave Controlled", "Full-Wave Controlled"]
    )
    
    # Only show firing angle for controlled rectifiers
    firing_angle = None
    if "Controlled" in rectifier_type:
        firing_angle = st.sidebar.slider("Firing Angle (degrees)", 0, 180, 30)
    
    # Simulate the selected circuit
    if rectifier_type == "Half-Wave Uncontrolled":
        input_voltage, output_voltage, output_current = simulate_half_wave_uncontrolled(
            t, amplitude, frequency, load_resistance, load_inductance/1000
        )
        circuit_explanation = """
        ### Half-Wave Uncontrolled Rectifier
        
        This is the simplest rectifier circuit consisting of a single diode. During the positive half-cycle 
        of the input AC voltage, the diode conducts and current flows through the load. During the negative 
        half-cycle, the diode blocks current flow, resulting in zero output voltage.
        
        **Key characteristics:**
        - Conducts only during positive half-cycles
        - Low efficiency (40.6%)
        - High ripple content
        - DC component = Vm/π (where Vm is the peak input voltage)
        """
        
    elif rectifier_type == "Full-Wave Uncontrolled":
        input_voltage, output_voltage, output_current = simulate_full_wave_uncontrolled(
            t, amplitude, frequency, load_resistance, load_inductance/1000
        )
        circuit_explanation = """
        ### Full-Wave Uncontrolled Rectifier
        
        This circuit uses four diodes arranged in a bridge configuration to convert both the positive and 
        negative half-cycles of the AC input into a unidirectional output. The bridge arrangement ensures 
        that current always flows through the load in the same direction.
        
        **Key characteristics:**
        - Conducts during both positive and negative half-cycles
        - Higher efficiency (81.2%)
        - Lower ripple content compared to half-wave
        - DC component = 2Vm/π (where Vm is the peak input voltage)
        - Ripple frequency is twice the input frequency
        """
        
    elif rectifier_type == "Half-Wave Controlled":
        input_voltage, output_voltage, output_current = simulate_half_wave_controlled(
            t, amplitude, frequency, firing_angle, load_resistance, load_inductance/1000
        )
        rectifier_type = f"Half-Wave Controlled (Firing Angle: {firing_angle})"
        circuit_explanation = f"""
        ### Half-Wave Controlled Rectifier
        
        This circuit replaces the diode with a thyristor (SCR) to control when conduction begins during 
        the positive half-cycle. By delaying the firing of the SCR (controlled by the firing angle α), 
        the average output voltage can be controlled.
        
        **Current firing angle: {firing_angle}°**
        
        **Key characteristics:**
        - Output voltage can be controlled by adjusting the firing angle
        - Average output voltage = (Vm/2π)(1+cos(α))
        - Firing angle range: 0° to 180°
        - At α=0°, behaves like an uncontrolled rectifier
        - At α=180°, no output voltage
        """
        
    elif rectifier_type == "Full-Wave Controlled":
        input_voltage, output_voltage, output_current = simulate_full_wave_controlled(
            t, amplitude, frequency, firing_angle, load_resistance, load_inductance/1000
        )
        rectifier_type = f"Full-Wave Controlled (Firing Angle: {firing_angle})"
        circuit_explanation = f"""
        ### Full-Wave Controlled Rectifier
        
        This circuit uses four SCRs in a bridge configuration, allowing control of the output voltage during 
        both positive and negative half-cycles of the input. This provides more precise control and better 
        efficiency compared to the half-wave controlled rectifier.
        
        **Current firing angle: {firing_angle}°**
        
        **Key characteristics:**
        - Control over both positive and negative half-cycles
        - Average output voltage = (2Vm/π)(1+cos(α))
        - Firing angle range: 0° to 180°
        - Higher efficiency than half-wave controlled rectifier
        - Lower ripple content
        """

# Three-Phase Rectifier options
else:  # Three-Phase Rectifiers
    rectifier_type = st.sidebar.selectbox(
        "Rectifier Type",
        ["Three-Phase Uncontrolled", "Three-Phase Controlled"]
    )
    
    # Only show firing angle for controlled rectifiers
    firing_angle = None
    if "Controlled" in rectifier_type:
        firing_angle = st.sidebar.slider("Firing Angle (degrees)", 0, 180, 30)
    
    # Simulate the selected circuit
    if rectifier_type == "Three-Phase Uncontrolled":
        input_voltage, output_voltage, output_current = simulate_three_phase_uncontrolled(
            t, amplitude, frequency, load_resistance, load_inductance/1000
        )
        circuit_explanation = """
        ### Three-Phase Uncontrolled Rectifier
        
        This circuit uses six diodes to rectify a three-phase AC input. The diodes conduct in pairs, with each 
        pair conducting for 120° of the input cycle. This results in a much smoother output compared to 
        single-phase rectifiers.
        
        **Key characteristics:**
        - Six-pulse operation (each diode conducts for 60° per cycle)
        - Very low ripple content (compared to single-phase)
        - High efficiency (95.5%)
        - DC component = 3√3Vm/π (where Vm is the peak phase voltage)
        - Ripple frequency is six times the input frequency
        """
        
    else:  # Three-Phase Controlled
        input_voltage, output_voltage, output_current = simulate_three_phase_controlled(
            t, amplitude, frequency, firing_angle, load_resistance, load_inductance/1000
        )
        rectifier_type = f"Three-Phase Controlled (Firing Angle: {firing_angle})"
        circuit_explanation = f"""
        ### Three-Phase Controlled Rectifier
        
        This circuit uses six SCRs instead of diodes, allowing control of the output voltage. By adjusting the 
        firing angle of the SCRs, the average output voltage can be precisely controlled.
        
        **Current firing angle: {firing_angle}°**
        
        **Key characteristics:**
        - Control over all three phases
        - Average output voltage = (3√3Vm/π)cos(α)
        - Firing angle range: 0° to 180°
        - Maintains low ripple characteristics of three-phase rectification
        - Used in high-power applications like motor drives and HVDC transmission
        """

# Calculate metrics
metrics = calculate_metrics(input_voltage, output_voltage, output_current, load_resistance)

# Main content area with tabs
tab1, tab2 = st.tabs(["Waveforms", "Theory"])

with tab1:
    st.markdown("<h2 class='sub-header'>Waveform Analysis</h2>", unsafe_allow_html=True)
    
    # Display waveform plots
    plot_waveforms(t, input_voltage, output_voltage, output_current, rectifier_type)
    
    # Display metrics in a grid
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown("<div class='metric-card'>", unsafe_allow_html=True)
        st.metric("Average Output Voltage", f"{metrics['avg_voltage']:.2f} V")
        st.markdown("</div>", unsafe_allow_html=True)
    
    with col2:
        st.markdown("<div class='metric-card'>", unsafe_allow_html=True)
        st.metric("RMS Output Voltage", f"{metrics['rms_voltage']:.2f} V")
        st.markdown("</div>", unsafe_allow_html=True)
    
    with col3:
        st.markdown("<div class='metric-card'>", unsafe_allow_html=True)
        st.metric("Ripple Factor", f"{metrics['ripple_factor']:.2f}")
        st.markdown("</div>", unsafe_allow_html=True)
    
    with col4:
        st.markdown("<div class='metric-card'>", unsafe_allow_html=True)
        st.metric("Form Factor", f"{metrics['form_factor']:.2f}")
        st.markdown("</div>", unsafe_allow_html=True)
    
    # Additional metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown("<div class='metric-card'>", unsafe_allow_html=True)
        st.metric("Average Output Current", f"{metrics['avg_current']:.2f} A")
        st.markdown("</div>", unsafe_allow_html=True)
    
    with col2:
        st.markdown("<div class='metric-card'>", unsafe_allow_html=True)
        st.metric("RMS Output Current", f"{metrics['rms_current']:.2f} A")
        st.markdown("</div>", unsafe_allow_html=True)
    
    with col3:
        st.markdown("<div class='metric-card'>", unsafe_allow_html=True)
        st.metric("Output Power", f"{metrics['output_power']:.2f} W")
        st.markdown("</div>", unsafe_allow_html=True)
    
    with col4:
        st.markdown("<div class='metric-card'>", unsafe_allow_html=True)
        st.metric("Efficiency", f"{metrics['efficiency']:.2f}%")
        st.markdown("</div>", unsafe_allow_html=True)

with tab2:
    st.markdown("<h2 class='sub-header'>Theoretical Background</h2>", unsafe_allow_html=True)

    # Continue with the theory content
    
    st.markdown("""
    ### Rectifier Fundamentals
    
    Rectifiers are electronic circuits that convert alternating current (AC) to direct current (DC). 
    They are fundamental components in power electronics and are used in various applications, from small 
    power supplies to large industrial systems.
    
    ### Types of Rectifiers
    
    **Based on control:**
    - **Uncontrolled Rectifiers**: Use diodes which conduct when forward biased
    - **Controlled Rectifiers**: Use thyristors (SCRs) which conduct when forward biased AND triggered
    
    **Based on input phases:**
    - **Single-Phase Rectifiers**: Convert single-phase AC to DC
    - **Three-Phase Rectifiers**: Convert three-phase AC to DC, offering better efficiency and lower ripple
    
    **Based on conversion:**
    - **Half-Wave Rectifiers**: Utilize only half of the input waveform
    - **Full-Wave Rectifiers**: Utilize both halves of the input waveform
    
    ### Key Performance Metrics
    
    - **Average Output Voltage**: The DC component of the output voltage
    - **RMS Output Voltage**: The effective value of the output voltage
    - **Ripple Factor**: Measure of the AC component in the output (lower is better)
    - **Form Factor**: Ratio of RMS value to average value
    - **Efficiency**: Ratio of output power to input power
    
    ### Effect of Firing Angle in Controlled Rectifiers
    
    The firing angle (α) determines when the thyristor is triggered during each cycle:
    
    - **α = 0°**: Maximum output (equivalent to uncontrolled rectifier)
    - **0° < α < 90°**: Positive output voltage, rectifier operation
    - **α = 90°**: Zero average output voltage
    - **90° < α < 180°**: Negative output voltage, inverter operation
    
    ### Effect of Load Inductance
    
    - **Resistive Load**: Output current follows output voltage
    - **Inductive Load**: Smooths current flow, reducing ripple
    - **Highly Inductive Load**: Can lead to continuous conduction mode
    """)
    
    st.markdown("<div class='info-text'>", unsafe_allow_html=True)
    st.markdown("""
    ### Teaching Tips
    
    1. Start with the simplest circuit (half-wave uncontrolled) and progressively move to more complex ones
    2. Focus on the relationship between firing angle and output voltage in controlled rectifiers
    3. Compare waveforms between different rectifier types to highlight advantages and disadvantages
    4. Discuss practical applications for each rectifier type
    5. Relate theoretical equations to the observed simulation results
    """)
    st.markdown("</div>", unsafe_allow_html=True)

# Footer
st.markdown("---")
st.markdown("© 2025 Power Electronics Educational Simulator")
