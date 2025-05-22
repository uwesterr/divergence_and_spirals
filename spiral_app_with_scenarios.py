# streamlit run spiral_app_with_scenarios.py


import streamlit as st
import streamlit.components.v1 as components

import numpy as np
import pandas as pd
import math
import plotly.express as px
from scipy.stats import binom # Not used, but was in original
import scipy.stats # Not used, but was in original
from scipy import special # Not used, but was in original


# Predefined scenarios
PREDEFINED_SCENARIOS = {
    "Default Balanced": {
        "acquisition_margin": 5, "uncertainty_cone": 1000, "v": 0.31, "b": 5.6
    },
    "Short-Range, High-Speed": {
        "acquisition_margin": 3, "uncertainty_cone": 700, "v": 0.4, "b": 7.0
    },
    "Long-Range, Max Sensitivity": {
        "acquisition_margin": 10, "uncertainty_cone": 1500, "v": 0.2, "b": 4.0
    }
}

apptitle = 'Spiral Speedup Through Divergence Increase'

st.set_page_config(
    page_title=apptitle,
    page_icon="🌀",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        'Get Help': 'https://www.example.com/help', # Placeholder
        'Report a bug': "https://www.example.com/bug", # Placeholder
        'About': f"# {apptitle}\nThis app visualizes how increasing laser beam divergence can speed up spiral scanning for optical acquisition."
    }
)

# --- Core Calculation Logic ---
def calc():
    if "selected_scenario_name" not in st.session_state: 
        st.session_state.selected_scenario_name = list(PREDEFINED_SCENARIOS.keys())[0]
    
    current_scenario_name = st.session_state.selected_scenario_name
    active_scenario = PREDEFINED_SCENARIOS[current_scenario_name]

    for key in ['acquisition_margin', 'uncertainty_cone', 'v', 'b']:
        if key not in st.session_state: # Initialize from active scenario if not present
            st.session_state[key] = active_scenario[key]

    st.session_state.acquisition_margin_linear = 10**(st.session_state.get('acquisition_margin', 0) / 10.0)
    st.session_state.spiral_arm_distance_speedup = st.session_state.acquisition_margin_linear**0.5
    st.session_state.spiral_velocity_speedup = st.session_state.acquisition_margin_linear**0.5
    st.session_state.total_spiral_speedup = st.session_state.spiral_arm_distance_speedup * st.session_state.spiral_velocity_speedup
    
    uc_val = float(st.session_state.get('uncertainty_cone', 1000.0))
    v_val = float(st.session_state.get('v', 0.1))
    b_val = float(st.session_state.get('b', 1.0))

    if v_val <= 0 or b_val <= 0: 
        st.session_state.time_one_spiral = 0.0
    else:
        st.session_state.time_one_spiral = math.pi * (uc_val**2) / (v_val * b_val * 1e6)

    time_array = np.arange(0, st.session_state.time_one_spiral, 0.001)

    if time_array.size == 0:
        data_spiral_time = pd.DataFrame(columns=["time", "phi", "r"])
    else:
        data_spiral_time = pd.DataFrame({"time": time_array})
        if b_val <= 0 or v_val <= 0:
            data_spiral_time['phi'] = 0.0
            data_spiral_time['r'] = 0.0
        else:
            phi_sqrt_factor = math.sqrt(4 * math.pi / b_val * v_val * 1e6) if b_val > 0 else 0 # check b_val again
            data_spiral_time['phi'] = np.sqrt(data_spiral_time['time']) * phi_sqrt_factor
            data_spiral_time['r'] = data_spiral_time["phi"] * b_val / (math.pi * 2) if b_val > 0 else 0 # check b_val again
        data_spiral_time = data_spiral_time[data_spiral_time["r"] <= uc_val].copy()
    
    data_spiral_in = data_spiral_time.copy(deep=True)
    if not data_spiral_time.empty:
        data_spiral_in['r'] = data_spiral_time['r'].values[::-1]
        data_spiral_in['time'] = data_spiral_time['time'] + st.session_state.time_one_spiral
    else: 
        for col in ['r', 'time']:
             if col not in data_spiral_in.columns: data_spiral_in[col] = pd.Series(dtype='float64')

    df_original = pd.concat([data_spiral_time, data_spiral_in]).reset_index(drop=True)
    if not df_original.empty:
        df_original["spiral_name"] = "original"
    else: 
        df_original = pd.DataFrame(columns=['time', 'r', 'phi', 'spiral_name'])
        # df_original["spiral_name"] = "original" # This line would fail if df_original is truly empty

    df_fast = df_original.copy(deep=True)
    if 'total_spiral_speedup' in st.session_state and st.session_state.total_spiral_speedup > 0 and not df_fast.empty :
        df_fast['time'] = df_fast['time'] / st.session_state.total_spiral_speedup
        df_fast["spiral_name"] = "speedup"
    elif not df_fast.empty: 
        # df_fast['time'] = df_fast['time'] # No change if speedup is 0 or 1
        df_fast["spiral_name"] = "speedup (no change)"
    
    # Ensure 'spiral_name' column exists before concat
    if "spiral_name" not in df_original.columns and not df_original.empty: df_original["spiral_name"] = "original"
    if "spiral_name" not in df_fast.columns and not df_fast.empty: df_fast["spiral_name"] = "speedup"

    st.session_state.data_spiral_time_combined = pd.concat([df_original, df_fast]).reset_index(drop=True)
    return

# --- Sidebar Setup & State Initialization ---
st.sidebar.markdown("## Scenario & Inputs")

def apply_scenario_to_state(scenario_name_from_key):
    scenario_config = PREDEFINED_SCENARIOS[st.session_state[scenario_name_from_key]]
    st.session_state.acquisition_margin = scenario_config["acquisition_margin"]
    st.session_state.uncertainty_cone = scenario_config["uncertainty_cone"]
    st.session_state.v = scenario_config["v"]
    st.session_state.b = scenario_config["b"]

if "selected_scenario_name" not in st.session_state:
    st.session_state.selected_scenario_name = list(PREDEFINED_SCENARIOS.keys())[0] 
    apply_scenario_to_state("selected_scenario_name")

def scenario_selectbox_callback():
    apply_scenario_to_state("selected_scenario_name")
    # calc() # Implicitly called by sliders' on_change

st.sidebar.selectbox(
    "Predefined Scenario:",
    options=list(PREDEFINED_SCENARIOS.keys()),
    key="selected_scenario_name", 
    on_change=scenario_selectbox_callback 
)

st.sidebar.markdown("---") 
st.sidebar.markdown("### Manual Adjustments:")

st.sidebar.slider("Acquisition margin [dB]:", key="acquisition_margin", on_change=calc, min_value=0, max_value=20, step=1)
st.sidebar.slider("UC to scan [µrad]:", key="uncertainty_cone", on_change=calc, min_value=100, max_value=3000, step=10)
st.sidebar.slider("Scan velocity [rad/s]:", key="v", on_change=calc, min_value=0.00001, max_value=0.5, step=0.00001, format="%.5f") 
st.sidebar.slider("Spiral arm distance [µrad]:", key="b", on_change=calc, min_value=3.0, max_value=50.0, step=0.1, format="%.1f")

for key, default_val in [
    ('acquisition_margin_linear', 1.0), ('spiral_arm_distance_speedup', 1.0),
    ('spiral_velocity_speedup', 1.0), ('total_spiral_speedup', 1.0),
    ('time_one_spiral', 0.0), ('show_trace', False)
]:
    if key not in st.session_state:
        st.session_state[key] = default_val

if 'data_spiral_time_combined' not in st.session_state: 
    st.session_state.data_spiral_time_combined = pd.DataFrame(columns=['time', 'r', 'phi', 'spiral_name'])

calc() 

# --- Main Page Layout & Visualizations ---
st.markdown("---")
col_metrics, col_animation = st.columns([1, 1])

with col_metrics:
    st.markdown(f'### Calculated Speedups for "{st.session_state.selected_scenario_name}" Scenario')
    st.metric("Total Spiral Speedup Factor", "%.1f x" % st.session_state.get("total_spiral_speedup", 1.0))
    st.metric("Acquisition Margin (linear factor)", "%.1f" % st.session_state.get("acquisition_margin_linear", 1.0))
    st.metric("Arm Distance Speedup (due to margin)", "%.1f x" % st.session_state.get("spiral_arm_distance_speedup", 1.0))
    st.metric("Velocity Speedup (due to margin)", "%.1f x" % st.session_state.get("spiral_velocity_speedup", 1.0))

with col_animation:
    st.markdown("### Spiral Scan Animation")
    st.session_state.show_trace = st.toggle('Show full trace in animation', value=st.session_state.get('show_trace', False), key='toggle_show_trace_main')
                
    # Prepare values for JavaScript, ensuring they are valid JS numbers/booleans
    js_vel_speedup = float(st.session_state.get('spiral_velocity_speedup', 1.0))
    js_arm_dist_speedup = float(st.session_state.get('spiral_arm_distance_speedup', 1.0))
    js_show_trace = str(st.session_state.get('show_trace', False)).lower() # JS expects 'true' or 'false'

    actual_html_content = f"""
<!DOCTYPE html><html><head><style>
canvas {{ background-color: black; border: 1px solid #555; border-radius: 50%; }}
.star {{ position: absolute; width: 1px; height: 1px; background-color: white; opacity: 0.7; }}
</style></head><body style="background-color: black; display: flex; justify-content: center; align-items: center; margin:0; overflow:hidden;">
<canvas id="spiralCanvas" width="380" height="380"></canvas>
<script>
const canvas = document.getElementById('spiralCanvas'); const ctx = canvas.getContext('2d');
const centerX = canvas.width/2; const centerY = canvas.height/2; let spiralTime = 0;
const ballR1 = 12, ballR2 = 12 * Math.max(1, {js_vel_speedup*0.8}); // Make speedup ball slightly smaller if faster
const velFactor = Math.max(0.1, {js_vel_speedup}); const armFactor = Math.max(0.1, {js_arm_dist_speedup});
const baseSpeed = 4, speed1 = baseSpeed, speed2 = baseSpeed * velFactor;
const baseArmDist = 10.0; // Visual parameter for JS animation, not directly from calc
const rPhi1 = baseArmDist / (2*Math.PI);
const phiStep1 = (baseArmDist > 0) ? (4*Math.PI*speed1) / (baseArmDist * 1) : 0;
const effArmDist2 = baseArmDist * armFactor;
const rPhi2 = (effArmDist2 > 0) ? effArmDist2 / (2*Math.PI) : 0;
const phiStep2 = (effArmDist2 > 0) ? (4*Math.PI*speed2) / (effArmDist2 * 1) : 0;       
const pOffset1=90, pOffset2=22; let pos1=[], pos2=[];
const MAX_POS = {js_show_trace} === 'true' ? 300 : 5; // Longer trace if full trace is on

function draw() {{
    if ({js_show_trace} === 'false') {{ ctx.clearRect(0,0,canvas.width,canvas.height); }}
    else {{ ctx.fillStyle = 'rgba(0,0,0,0.1)'; ctx.fillRect(0,0,canvas.width,canvas.height); }} // Fade effect for trace

    for(let i=0; i<100; i++) {{ if(Math.random() > 0.99) {{ ctx.fillStyle='white'; ctx.fillRect(Math.random()*canvas.width, Math.random()*canvas.height, 1, 1); }} }} //簡易星空

    ['pos1', 'pos2'].forEach((p, idx) => {{
        let arr = (idx===0) ? pos1 : pos2; let radius = (idx===0) ? ballR1 : ballR2;
        for (let i=0; i<arr.length; i++) {{
            let pt = arr[i]; let alpha = Math.max(0, 0.5 - ( (arr.length-1-i) / arr.length) * 0.5 ); // Fade out older points
            ctx.beginPath(); ctx.arc(pt.x, pt.y, radius, 0, 2*Math.PI);
            let grad = ctx.createRadialGradient(pt.x,pt.y,0, pt.x,pt.y,radius);
            grad.addColorStop(0, idx===0 ? 'rgba(255,50,50,'+alpha+')' : 'rgba(50,50,255,'+alpha+')');
            grad.addColorStop(1, 'rgba(255,255,255,'+alpha*0.7+')');
            ctx.fillStyle = grad; ctx.fill();
        }}
    }});

    let r_1=0, x_1=centerX, y_1=centerY;
    if(phiStep1 > 0 && rPhi1 > 0) {{ let pS = Math.sqrt(phiStep1*spiralTime); r_1=rPhi1*pS; x_1=centerX+r_1*Math.cos(pOffset1+pS); y_1=centerY+r_1*Math.sin(pOffset1+pS); }}
    pos1.push({{x:x_1, y:y_1}}); if(pos1.length > MAX_POS) pos1.shift();
    
    let r_2=0, x_2=centerX, y_2=centerY;
    if(phiStep2 > 0 && rPhi2 > 0) {{ let pS = Math.sqrt(phiStep2*spiralTime); r_2=rPhi2*pS; x_2=centerX+r_2*Math.cos(pOffset2+pS); y_2=centerY+r_2*Math.sin(pOffset2+pS); }}
    pos2.push({{x:x_2, y:y_2}}); if(pos2.length > MAX_POS) pos2.shift();
    
    spiralTime += 0.2; // Slower animation time step for smoother visual
    const limit = Math.max(centerX-ballR1, centerY-ballR1);
    if(r_1 > limit || r_2 > limit) {{ spiralTime=0; pos1=[]; pos2=[]; if({js_show_trace} === 'false') ctx.clearRect(0,0,canvas.width,canvas.height); }}
    requestAnimationFrame(draw);
}}
draw();
</script></body></html>
"""
    html_content = actual_html_content

    components.html(html_content, height=400, scrolling=False)

st.markdown("---")
st.markdown("### Comparative Analysis Charts")
col_chart1, col_chart2 = st.columns(2)

plot_df = st.session_state.get('data_spiral_time_combined', pd.DataFrame())
max_radius_plot = st.session_state.get('uncertainty_cone', 1000) * 1.15 

with col_chart1:
    st.markdown("#### Spiral Scan: Time vs. Radius (Animated)")
    if not plot_df.empty and 'r' in plot_df.columns and pd.api.types.is_numeric_dtype(plot_df['r']) and plot_df['r'].max() > 0:
        fig_anim = px.scatter(plot_df, x="time", y="r", animation_frame="spiral_name", color="spiral_name", 
                              range_y=[0, max_radius_plot], range_x=[0, plot_df['time'].max()*1.1 if plot_df['time'].max() > 0 else 1],
                              labels={{"time":"Time (s)", "r":"Radius (µrad)", "spiral_name":"Spiral Type"}})
        fig_anim.update_layout(font=dict(family="Arial, sans-serif", size=12), showlegend=False)
        st.plotly_chart(fig_anim, use_container_width=True)
    else:
        st.info("Insufficient data for Time vs. Radius animation chart.")

with col_chart2:
    st.markdown("#### Static Comparison: Time vs. Radius")
    if not plot_df.empty and 'r' in plot_df.columns and pd.api.types.is_numeric_dtype(plot_df['r']) and plot_df['r'].max() > 0:
        fig_static = px.scatter(plot_df, x="time", y="r", color="spiral_name",
                                range_y=[0, max_radius_plot], range_x=[0, plot_df['time'].max()*1.1 if plot_df['time'].max() > 0 else 1],
                                labels={{"time":"Time (s)", "r":"Radius (µrad)", "spiral_name":"Spiral Type"}})
        fig_static.update_layout(font=dict(family="Arial, sans-serif", size=12), legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1))
        st.plotly_chart(fig_static, use_container_width=True)
    else:
        st.info("Insufficient data for Static Comparison chart.")

st.markdown("---")
st.markdown("### Laser Beam Divergence Visualization (Conceptual)")
beam_arm_speedup = st.session_state.get('spiral_arm_distance_speedup', 1.0)
if beam_arm_speedup <= 0: beam_arm_speedup = 1.0 

base_beam_radius_viz = 30 
uc_for_viz = st.session_state.get('uncertainty_cone', 1000)
dynamic_base_radius = base_beam_radius_viz * (uc_for_viz / 1000.0) 
dynamic_base_radius = max(10, min(dynamic_base_radius, 50)) 

df_beam_viz = pd.DataFrame({
    "radius_viz": [dynamic_base_radius, dynamic_base_radius * beam_arm_speedup],
    "state": ["Original Divergence", f"Increased Divergence ({beam_arm_speedup:.1f}x arm dist.)"],
    "center": [dynamic_base_radius * beam_arm_speedup, dynamic_base_radius * beam_arm_speedup] 
})
df_beam_viz["radius_viz"] = df_beam_viz["radius_viz"].apply(lambda x: max(x, 1.0))

if not df_beam_viz.empty and df_beam_viz["radius_viz"].max() > 0 :
    max_viz_r = df_beam_viz["radius_viz"].max()
    fig_beam = px.scatter(df_beam_viz, x="center", y="center", color="state", size="radius_viz", 
                           size_max=max_viz_r * 1.2, 
                           hover_name="state",
                           labels={{"state":"Beam State", "radius_viz":"Relative Size"}})
    
    plot_limit = max_viz_r * 2.2 
    if plot_limit < 50 : plot_limit = 50 # Ensure a minimum plot area
    fig_beam.update_layout(
        xaxis=dict(range=[0, plot_limit], showgrid=False, zeroline=False, showticklabels=False, scaleanchor="y", scaleratio=1, visible=False),
        yaxis=dict(range=[0, plot_limit], showgrid=False, zeroline=False, showticklabels=False, visible=False),
        showlegend=True, legend_title_text='Beam State',
        plot_bgcolor='rgba(240,240,240,0.8)' 
    )
    st.plotly_chart(fig_beam, use_container_width=True)
else:
    st.warning("Cannot display laser beam visualization.")

st.sidebar.markdown("---")
st.sidebar.info("This app is a conceptual tool. Actual system performance may vary.")
