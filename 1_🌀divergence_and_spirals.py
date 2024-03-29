#  streamlit run /Users/uwesterr/CloudProjectsUnderWork/ProjectsUnderWork/AlbaLight/BSA/bsa_step_duration_calc.py


import streamlit as st
import streamlit.components.v1 as components

import numpy as np
import pandas as pd
import math
# from utils import show_code
from scipy.stats import binom
import scipy.stats
from scipy import special
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px




expanded_flag=True

apptitle = 'Spiral speedup through divergence increase'

st.set_page_config(
page_title="Spiral speedup through divergence increase",
page_icon="👋",
layout="wide",
initial_sidebar_state="expanded",
menu_items={
    'Get Help': 'https://www.extremelycoolapp.com/help',
    'Report a bug': "https://www.extremelycoolapp.com/bug",
    'About': "# This app is a collection of useful calculations"
}
)

def calc():

    st.session_state_acquisition_margin_linear=10**(st.session_state.acquisition_margin/10)
    st.session_state.spiral_arm_distance_speedup=st.session_state_acquisition_margin_linear**.5
    st.session_state.spiral_velocity_speedup=st.session_state_acquisition_margin_linear**.5
    st.session_state.total_spiral_speedup=st.session_state.spiral_arm_distance_speedup*st.session_state.spiral_velocity_speedup
    st.session_state.time_one_spiral=math.pi*st.session_state.uncertainty_cone**2/(st.session_state.v*st.session_state.b*1e6)
    time1=np.arange (0, st.session_state.time_one_spiral, .001)

    #time=[x / granularity for x in range(0,(int(st.session_state.time_one_spiral)+1)*granularity )]
    data_spiral_time=pd.DataFrame({"time":time1})
    del time1
    
    data_spiral_time['phi'] =np.sqrt(data_spiral_time['time'])* math.sqrt(4*math.pi/st.session_state.b*st.session_state.v*1e6)
    
    data_spiral_time['r'] = data_spiral_time["phi"]*st.session_state.b/(math.pi*2)
    data_spiral_time = data_spiral_time.loc[data_spiral_time["r"]<=st.session_state.uncertainty_cone]
    data_spiral_in=data_spiral_time.copy(deep=True)
    data_spiral_in.r=data_spiral_time.r.values[::-1]
    data_spiral_in.time=data_spiral_in.time + st.session_state.time_one_spiral
    frames=[data_spiral_time, data_spiral_in]
    
    st.session_state.data_spiral_time=pd.concat(frames)
    # add column named spiral_name and set it with "slow"
    st.session_state.data_spiral_time["spiral_name"]="original"                        
    
    # generate fast spiral
    st.session_state.data_spiral_time_fast=st.session_state.data_spiral_time.copy(deep=True)
    st.session_state.data_spiral_time_fast.time=st.session_state.data_spiral_time_fast.time/st.session_state.total_spiral_speedup
    # add column named spiral_name and set it with "speedup"
    st.session_state.data_spiral_time_fast["spiral_name"]="speedup"                        
    
    st.session_state.data_spiral_time=pd.concat([st.session_state.data_spiral_time, st.session_state.data_spiral_time_fast])

    return


st.sidebar.markdown("""
## Input acquisition margin
""")
acquisition_margin = st.sidebar.slider("Acquisition margin [dB]:", key="acquisition_margin", on_change=calc, value=5, min_value=0, max_value=20, step=1)

st.sidebar.markdown("""
## Input spiral parameters
""")

with st.container():
    col_left, col_right = st.columns([1,1])
    with col_right:
        st.markdown("""
                    
                    ## There are several scenarios which impact the reduction of the acquisition time:
- Speedup is on terminal which starts as master
    - Speedup of spatial acquisition will be close to total speedup
- Speedup is on terminal which starts as slave
    - Speedup of spatial acquisition will be not very high
- Speedup is on both terminals
    - Speedup of spatial acquisition will be very close to total speedup

""")  
         
        
        st.markdown('#### <strong style="color: green;">Note: If due to reduced straylight selfblinding can be avoided and a full master/master spatial acquisition is possible, the speedup will be another factor of about 7, depending on the scenario.</strong>', unsafe_allow_html=True)
 
    st.markdown("""
    <hr>
    """, unsafe_allow_html=True)        
    with col_left:
        st.markdown("""
                    # Spiral speedup through divergence increase
                    In case that there is margin in the acquisition budget because the link is communication budget driven, the acquisition time can be reduced by increasing the divergence.
        
                    This app calculates how much the divergence can be increased and how much the acquisition time can be reduced.
                    
                    The steps are:
                    - Input the acquisition margin [dB] on the left hand slider
                    - The possible divergence increase is calculated
                    - The spiral duration can be reduced by 
                        - increasing the spiral velocity
                        - increasing the spiral arm distance  
                    - The factor by which the spiral duration can be reduced is calculated
                    
                    """)

        # Insert vertical line

st.session_state['alpha'] = 0.05
if 'acquisition_margin' not in st.session_state:
    st.session_state['acquisition_margin'] = 5
    st.session_state['session_state_acquisition_margin_linear'] = 0
    st.session_state['spiral_arm_distance_speedup'] = 0 
    st.session_state['spiral_velocity_speedup'] = 10 
    st.session_state['total_spiral_speedup'] = 0
    st.session_state['show_trace'] = 1
    #calc()
start_fov = st.sidebar.slider( "UC to scan [µrad]:", key="uncertainty_cone", on_change=calc, value= 1000, min_value= 100, max_value= 3000, step=10)

vel = st.sidebar.slider( "Scan velocity [rad/s]:", key="v", on_change=calc, value= .31, min_value= 0.00001, max_value= .5, step=.01)
b = st.sidebar.slider( "Spiral arm distance [µrad]:", key="b", on_change=calc, value= 5.6, min_value= 3.0, max_value= 50.0, step=.1)

with st.container():
    col_left, col_right = st.columns([1,1])
    with col_right:
        calc()
        st.markdown(f'<h1 style="color:green">{"Total Spiral Speedup: %.1f" % st.session_state.total_spiral_speedup}</h1>', unsafe_allow_html=True)
        
        st.metric("Acquisition Margin (linear)", ("%.0f" % st.session_state_acquisition_margin_linear))
        st.metric("Spiral Arm Distance Speedup", ("%.1f" % st.session_state.spiral_arm_distance_speedup))
        st.metric("Spiral Velocity Speedup", ("%.1f" % st.session_state.spiral_velocity_speedup))  

    with col_left:
        st.session_state.show_trace = st.toggle('Show trace', False, key='my_checkbox')
                
        # JavaScript/HTML code with dynamic ballRadius

        # HTML code as a multiline string
        html_code = f"""
        <!DOCTYPE html>
        <html>
        <head>
        <style>
        canvas {{
            background-color: black;
            border: 1px solid black;
            border-radius: 50%; /* Make the canvas round */
        }}
        .star {{
        position: absolute;
        width: 2px;
        height: 2px;
        background-color: white;
    }} 
        </style>
        </head>
        <body style="background-color: black; display: flex; justify-content: center; align-items: center;">
        <canvas id="myCanvas" width="400" height="400"></canvas>
        <script>
        var num_stars = 100;
        function createStar() {{
            const star = document.createElement('div');
            star.classList.add('star');
            star.style.left = Math.random() * window.innerWidth + 'px';
            star.style.top = Math.random() * window.innerHeight + 'px';
            document.body.appendChild(star);
    }}

    for (let i = 0; i < num_stars; i++) {{
        createStar();
    }}        
        
        var canvas = document.getElementById('myCanvas');
        var ctx = canvas.getContext('2d');
        var centerX = canvas.width / 2;
        var centerY = canvas.height / 2;

        var ballRadius = 15; // Dynamic ball radius
        var ballRadius2 = ballRadius*{st.session_state.spiral_velocity_speedup}; // Dynamic ball radius
        var velocity_speedup =  {st.session_state.spiral_velocity_speedup}; // Dynamic speedup
        var spiral_arm_distance_speedup = {st.session_state.spiral_arm_distance_speedup}; // Dynamic speedup
        var speed1 = 05, speed2 = speed1 * velocity_speedup; // Second ball is twice as fast
        
        // ******************* spiral 1 parameters     *******************
        var spiral_arm_distance = 10.5; // Spiral arm distance
        var sampling_rate = 1; // Sampling rate
        var radius_as_function_of_phi=spiral_arm_distance/(2*Math.PI) 
        var phi_step_per_sampling=4*Math.PI*speed1/(spiral_arm_distance*sampling_rate)
        
        // ******************* spiral 2 parameters  *******************
        var spiral_arm_distance2 = spiral_arm_distance*.99 * spiral_arm_distance_speedup; // Spiral arm distance
        var sampling_rate2 = 1; // Sampling rate
        var radius_as_function_of_phi2=spiral_arm_distance2/(2*Math.PI)
        var phi_step_per_sampling2=4*Math.PI*speed2/(spiral_arm_distance2*sampling_rate2)        
        var spiral_time=0;


        var a1 = 0, b1 = 1.5; // Constants for the first ball's spiral
        var a2 = 0, b2 = b1 * spiral_arm_distance_speedup; // Constants for the second ball's spiral  
        // add different offset so it is the dots are not always at same angular position
        // this is the case since the the increased radius is compensated by the increased speed for the second ball
        var phi_offset1=90;
        var phi_offset2=22;

        var ball1Positions = []; // Array to store the positions of the first ball
        var ball2Positions = []; // Array to store the positions of the second ball

        function drawBall() {{
            // add if statement based on st.session_state.show_trace to clear canvas or not

            if ({'false' if st.session_state.show_trace else 'true'}) {{
                    ctx.clearRect(0, 0, canvas.width, canvas.height);

                    }}                            
            // Draw fading traces for the last 3 positions of the first ball
            for (var i = 0; i < ball1Positions.length; i++) {{
                var position = ball1Positions[i];
                var alpha = .15 - (i / ball1Positions.length); // Calculate alpha value for fading effect
                ctx.beginPath();
                ctx.arc(position.x, position.y, ballRadius, 0, Math.PI * 2);
                var gradient = ctx.createRadialGradient(position.x, position.y, 0, position.x, position.y, ballRadius);
                gradient.addColorStop(0, 'rgba(255, 0, 0, ' + alpha + ')');
                gradient.addColorStop(1, 'rgba(255, 255, 255, ' + alpha + ')');
                ctx.fillStyle = gradient;
                ctx.fill();
                ctx.closePath();
            }}

            // Draw fading traces for the last 3 positions of the second ball
            for (var i = 0; i < ball2Positions.length; i++) {{
                var position = ball2Positions[i];
                var alpha = .15 - (i / .1*ball2Positions.length); // Calculate alpha value for fading effect
                ctx.beginPath();
                ctx.arc(position.x, position.y, ballRadius2, 0, Math.PI * 2);
                var gradient = ctx.createRadialGradient(position.x, position.y, 0, position.x, position.y, ballRadius2);
                gradient.addColorStop(0, 'rgba(0, 0, 255, ' + alpha + ')');
                gradient.addColorStop(1, 'rgba(255, 255, 255, ' + alpha + ')');
                ctx.fillStyle = gradient;
                ctx.fill();
                ctx.closePath();
            }}

            // First ball
            var phi=Math.sqrt(phi_step_per_sampling*spiral_time)
            var r = radius_as_function_of_phi * phi;// * (1 - Math.exp(-spiral_time));
            phi=phi_offset1+phi;
            spiral_time=spiral_time+1
            x1= centerX + r*Math.cos(phi);
            y1= centerY +r*Math.sin(phi);
            ctx.beginPath();
            ctx.arc(x1, y1, ballRadius, 0, Math.PI * 2);
            var gradient = ctx.createRadialGradient(x1, y1, 0, x1, y1, ballRadius);
            gradient.addColorStop(0, 'red');
            gradient.addColorStop(1, 'white');
            ctx.fillStyle = gradient;
            ctx.fill();
            ctx.closePath();

            // Second ball
            var phi2=Math.sqrt(phi_step_per_sampling2*spiral_time)
            var r2 = radius_as_function_of_phi2 * phi2 * (1 - Math.exp(-spiral_time));
            phi2=phi_offset2+phi2;
            x2= centerX + r2*Math.cos(phi2);
            y2= centerY +r2*Math.sin(phi2);
            
            ctx.beginPath();
            ctx.arc(x2, y2, ballRadius2, 0, Math.PI * 2);
            gradient = ctx.createRadialGradient(x2, y2, 0, x2, y2, ballRadius2);
            gradient.addColorStop(0, 'blue');
            gradient.addColorStop(1 , 'white');
            ctx.fillStyle = gradient;
            ctx.fill();
            ctx.closePath();
                        
            /*
            // add function that counts number of spiral arms and writes it to the canvas
            var spiral_arms=Math.floor(phi/(2*Math.PI))
            ctx.font = "30px Arial";
            ctx.fillStyle = "white";
            ctx.fillText("radius: " + Math.floor(r), 100, 50);   
            ctx.fillText("radius fast: " + Math.floor(r2), 100, 90);   
            */         
                     

            // Store the positions of the first ball
            ball1Positions.push({{ x: x1, y: y1 }});
            if (ball1Positions.length > 3) {{
                ball1Positions.shift(); // Remove the oldest position if there are more than 3
            }}

            // Store the positions of the second ball
            ball2Positions.push({{ x: x2, y: y2 }});
            if (ball2Positions.length > 3) {{
                ball2Positions.shift(); // Remove the oldest position if there are more than 3
            }}
        if ({'false' if st.session_state.show_trace else 'true'}) {{
            

            // Draw the line for the first ball
            if (ball1Positions.length > 1) {{
                ctx.beginPath();
                ctx.moveTo(ball1Positions[0].x, ball1Positions[0].y);
                for (var i = 1; i < ball1Positions.length; i++) {{
                    ctx.lineTo(ball1Positions[i].x, ball1Positions[i].y);
                }}
                ctx.strokeStyle = 'red';
                ctx.stroke();
            }}

 
        }}
        // Stop the animation if the first ball reaches the edge of the canvas
        if (x1 > canvas.width - ballRadius || x1 < ballRadius || y1 > canvas.height - ballRadius || y1 < ballRadius) {{
            // Reset positions
            spiral_time=0;
            ball1Positions = [];
            ball2Positions = [];
            ctx.clearRect(0, 0, canvas.width, canvas.height);
        }}
        // Stop the animation if the second ball reaches the edge of the canvas
        if (x2 > canvas.width + ballRadius2 || x2 < -ballRadius2 || y2 > canvas.height + ballRadius2 || y2 < -ballRadius2) {{
            // Reset positions
            spiral_time=0;
            ball1Positions = [];
            ball2Positions = [];
            ctx.clearRect(0, 0, canvas.width, canvas.height);
        }}
        
        if (x1 < r && x2 < r2) {{
            // Reset positions
            spiral_time=0;
            ball1Positions = [];
            ball2Positions = [];
            ctx.clearRect(0, 0, canvas.width, canvas.height);
        }}            

            requestAnimationFrame(drawBall);
        }}
        drawBall();
  
        </script>
        </body>
        </html>
        """

        # Embed in Streamlit
        st.markdown(f'<h1 style="color:green">{"Spiral Animation"}</h1>', unsafe_allow_html=True)
        # add radio button to select if trace shall be shown or not
        
        components.html(html_code, height=420)
        
        # add horizontal line with html
        st.markdown("""
        <hr>
        """, unsafe_allow_html=True)
        

        st.markdown(f'<h1 style="color:green">{"Spiral Animation Speedup line chart"}</h1>', unsafe_allow_html=True)
############## second plot
        fig = px.scatter(st.session_state.data_spiral_time, x="time", y="r", animation_frame="spiral_name", color="spiral_name")
        fig.update_layout(
            title="Spiral speedup through divergence increase",
            xaxis_title="Time [s]",
            yaxis_title="Radius [µrad]",
            font=dict(
                family="Courier New, monospace",
                size=18,
                color="RebeccaPurple"
            ),
            showlegend=False
        )
        st.plotly_chart(fig, use_container_width=True)
    

# insert horizontal line
st.markdown("""
<hr>
""", unsafe_allow_html=True)
with st.container():
    col_left, col_right = st.columns([2,2])
    
    #######  Duration spiral    ############## 
    with col_left:
        st.markdown(f'<h1 style="color:green">{"Spiral duration line chart "}</h1>', unsafe_allow_html=True)
        fig = px.scatter(st.session_state.data_spiral_time, x="time", y="r", color="spiral_name")
        fig.update_layout(
            title="Spiral speedup through divergence increase",
            xaxis_title="Time [s]",
            font=dict(
                family="Courier New, monospace",
                size=18,
                color="RebeccaPurple"
            ),
            legend=dict(
                title="Name of spiral",
                x=0.5,
                y=-0.3,
                xanchor='center',
                yanchor='top',
                orientation='h'
            )
        )
        fig.update_yaxes(title="Radius [µrad]")
        #st.plotly_chart(fig, use_container_width=True)
        fig

                ###############


        # add horizontal line with html
        st.markdown("""
        <hr>
        """, unsafe_allow_html=True)


    with col_left:
        st.markdown(f'<h1 style="color:green">{"Laser beam animation"}</h1>', unsafe_allow_html=True)

# add animated graph of st.session_state.data_spiral_time_fast x=time, y=r and animation_frame=spiral_name
        import plotly.graph_objects as go
        # generate dataframes with  columns radius and center_x, center_y, the values of center_x and center_y are radius, radius has the value 1 and 2
        df_circle_data=pd.DataFrame({"radius": [20,70]})
        # set center_x to max(radius) and center_y to max(radius)
        df_circle_data["center_x"]=max(df_circle_data["radius"] )       
        df_circle_data["center_y"]=max(df_circle_data["radius"] )
        df_circle_data["divergence"]=["original", "speedup"]
        
        #fig = go.Figure()
        fig = px.scatter(df_circle_data, x="center_x", y="center_y", animation_frame="divergence", color="divergence", size="radius", size_max=df_circle_data["radius"].max())
# dont show grid, dont show axis, dont show legend
        fig.update_layout(
            title="Spiral speedup through divergence increase",
            xaxis_title="",
            yaxis_title="",
            font=dict(
                family="Courier New, monospace",
                size=18,
                color="RebeccaPurple"
            ),
            showlegend=False
        )
        # dont show grid, dont show axis
        fig.update_xaxes(showgrid=False, zeroline=False)
        fig.update_yaxes(showgrid=False, zeroline=False)
        #dont show axis labels
        fig.update_xaxes(showticklabels=False)
        fig.update_yaxes(showticklabels=False)

        st.plotly_chart(fig, use_container_width=True)