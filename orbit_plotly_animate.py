import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta

def solve_kepler(M, e, tol=1e-10):
    """
    Solve Kepler's equation M = E - e*sin(E) for eccentric anomaly E
    using Newton-Raphson method.
    """
    E = M  # Initial guess
    for _ in range(100):  # Max iterations
        f = E - e * np.sin(E) - M
        df = 1 - e * np.cos(E)
        E_new = E - f / df
        if abs(E_new - E) < tol:
            break
        E = E_new
    return E

def animate_orbits(orbital_elements_list, labels=None, start_date=None, duration_days=365, time_step_days=1):
    """
    Animate multiple orbits of solar system objects over time.
    
    Parameters:
    orbital_elements_list : list of dicts - Each dict contains orbital elements:
        {'a': float, 'e': float, 'i': float, 'omega': float, 'Omega': float, 
         'M0': float, 'period': float, 'epoch': datetime}
    labels : list of str - Names for each orbit (optional)
    start_date : datetime - Starting date for animation (default: today)
    duration_days : int - Duration of animation in days (default: 365)
    time_step_days : int - Time step for animation in days (default: 1)
    """
    
    if start_date is None:
        start_date = datetime.now()
    
    # Calculate time steps
    time_steps = np.arange(0, duration_days + time_step_days, time_step_days)
    dates = [start_date + timedelta(days=int(t)) for t in time_steps]
    
    colors = px.colors.qualitative.Set1
    
    # Calculate full orbits for reference
    n_orbit_points = 1000
    all_x, all_y, all_z = [], [], []
    orbit_data = []
    
    for i, elements in enumerate(orbital_elements_list):
        a = elements['a']
        e = elements['e']
        i_deg = elements['i']
        omega = elements['omega']
        Omega = elements['Omega']
        M0 = elements['M0']
        period = elements['period']  # Period in days
        
        # Convert angles to radians
        i_rad = np.radians(i_deg)
        omega_rad = np.radians(omega)
        Omega_rad = np.radians(Omega)
        M0_rad = np.radians(M0)
        
        # Calculate rotation matrix
        R_Omega = np.array([
            [np.cos(Omega_rad), -np.sin(Omega_rad), 0],
            [np.sin(Omega_rad), np.cos(Omega_rad), 0],
            [0, 0, 1]
        ])
        
        R_i = np.array([
            [1, 0, 0],
            [0, np.cos(i_rad), -np.sin(i_rad)],
            [0, np.sin(i_rad), np.cos(i_rad)]
        ])
        
        R_omega = np.array([
            [np.cos(omega_rad), -np.sin(omega_rad), 0],
            [np.sin(omega_rad), np.cos(omega_rad), 0],
            [0, 0, 1]
        ])
        
        R = R_Omega @ R_i @ R_omega
        
        # Full orbit for reference
        nu_full = np.linspace(0, 2*np.pi, n_orbit_points)
        r_full = a * (1 - e**2) / (1 + e * np.cos(nu_full))
        x_orb_full = r_full * np.cos(nu_full)
        y_orb_full = r_full * np.sin(nu_full)
        z_orb_full = np.zeros_like(x_orb_full)
        
        coords_orb_full = np.array([x_orb_full, y_orb_full, z_orb_full])
        coords_helio_full = R @ coords_orb_full
        x_full, y_full, z_full = coords_helio_full
        
        all_x.extend(x_full)
        all_y.extend(y_full)
        all_z.extend(z_full)
        
        # Get epoch for this object
        epoch = elements.get('epoch', start_date)
        
        # Calculate positions at each time step
        positions = []
        for t in time_steps:
            current_date = start_date + timedelta(days=int(t))
            
            # Time difference from epoch in days
            dt_days = (current_date - epoch).total_seconds() / 86400.0
            
            # Mean motion (radians per day)
            n = 2 * np.pi / period
            
            # Mean anomaly at current time
            M = M0_rad + n * dt_days
            M = M % (2 * np.pi)  # Normalize to [0, 2π]
            
            # Solve Kepler's equation for eccentric anomaly
            E = solve_kepler(M, e)
            
            # True anomaly
            nu = 2 * np.arctan2(np.sqrt(1 + e) * np.sin(E/2), np.sqrt(1 - e) * np.cos(E/2))
            
            # Distance from focus
            r = a * (1 - e * np.cos(E))
            
            # Position in orbital plane
            x_orb = r * np.cos(nu)
            y_orb = r * np.sin(nu)
            z_orb = 0
            
            # Transform to heliocentric coordinates
            pos_orb = np.array([x_orb, y_orb, z_orb])
            pos_helio = R @ pos_orb
            
            positions.append(pos_helio)
        
        orbit_data.append({
            'orbit_x': x_full,
            'orbit_y': y_full,
            'orbit_z': z_full,
            'positions': positions,
            'color': colors[i % len(colors)],
            'label': labels[i] if labels and i < len(labels) else f'Object {i+1}'
        })
    
    # Calculate symmetric ranges
    max_x = max(abs(min(all_x)), abs(max(all_x)))
    max_y = max(abs(min(all_y)), abs(max(all_y)))
    max_z = max(abs(min(all_z)), abs(max(all_z)))
    max_range = max(max_x, max_y, max_z)
    
    # Create frames for animation
    frames = []
    for frame_idx, (t, date) in enumerate(zip(time_steps, dates)):
        frame_data = []
        
        # Add Sun
        frame_data.append(go.Scatter3d(
            x=[0], y=[0], z=[0],
            mode='markers',
            marker=dict(size=15, color='yellow'),
            name='Sun',
            showlegend=(frame_idx == 0)
        ))
        
        # Add orbit traces and current positions
        for i, orbit in enumerate(orbit_data):
            # Orbit trace
            frame_data.append(go.Scatter3d(
                x=orbit['orbit_x'],
                y=orbit['orbit_y'],
                z=orbit['orbit_z'],
                mode='lines',
                line=dict(width=3, color=orbit['color']),
                opacity=0.4,
                name=f"{orbit['label']} Orbit",
                showlegend=(frame_idx == 0)
            ))
            
            # Current position
            pos = orbit['positions'][frame_idx]
            frame_data.append(go.Scatter3d(
                x=[pos[0]], y=[pos[1]], z=[pos[2]],
                mode='markers',
                marker=dict(size=8, color=orbit['color']),
                name=orbit['label'],
                showlegend=(frame_idx == 0)
            ))
        
        frames.append(go.Frame(
            data=frame_data,
            name=str(frame_idx),
            layout=go.Layout(
                title=f"Solar System Animation - {date.strftime('%B %d, %Y')}"
            )
        ))
    
    # Create initial figure
    fig = go.Figure(
        data=frames[0].data,
        frames=frames
    )
    
    # Add animation controls
    fig.update_layout(
        title=f"Solar System Animation - {start_date.strftime('%B %d, %Y')}",
        scene=dict(
            xaxis_title='X (AU)',
            yaxis_title='Y (AU)',
            zaxis_title='Z (AU)',
            xaxis=dict(range=[-max_range, max_range]),
            yaxis=dict(range=[-max_range, max_range]),
            zaxis=dict(range=[-max_range, max_range]),
            aspectmode='cube'
        ),
        width=900,
        height=700,
        updatemenus=[{
            'type': 'buttons',
            'showactive': False,
            'buttons': [
                {
                    'label': 'Play',
                    'method': 'animate',
                    'args': [None, {
                        'frame': {'duration': 100, 'redraw': True},
                        'fromcurrent': True,
                        'transition': {'duration': 50}
                    }]
                },
                {
                    'label': 'Pause',
                    'method': 'animate',
                    'args': [[None], {
                        'frame': {'duration': 0, 'redraw': False},
                        'mode': 'immediate',
                        'transition': {'duration': 0}
                    }]
                }
            ]
        }],
        sliders=[{
            'steps': [
                {
                    'args': [[frame.name], {
                        'frame': {'duration': 0, 'redraw': True},
                        'mode': 'immediate',
                        'transition': {'duration': 0}
                    }],
                    'label': date.strftime('%b %d'),
                    'method': 'animate'
                }
                for frame, date in zip(frames, dates)
            ],
            'active': 0,
            'currentvalue': {'prefix': 'Date: '},
            'len': 0.9,
            'x': 0.1,
            'xanchor': 'left',
            'y': 0,
            'yanchor': 'top'
        }]
    )
    
    fig.show()
    return fig

# Example usage
if __name__ == "__main__":
    # Define orbital elements with periods and epochs
    from datetime import datetime
    
    # J2000.0 epoch (January 1, 2000, 12:00 TT)
    j2000 = datetime(2000, 1, 1, 12, 0, 0)
    
    # Halley's Comet last perihelion was February 9, 1986
    halley_epoch = datetime(1986, 2, 9)
    
    orbits = [
        {
            'a': 1.00000011, 'e': 0.01671022, 'i': 0.00005, 'omega': 114.20783,
            'Omega': -11.26064, 'M0': 357.51716, 'period': 365.25636, 'epoch': j2000
        },  # Earth - accurate J2000.0 elements
        {
            'a': 17.94, 'e': 0.967, 'i': 162.3, 'omega': 111.33,
            'Omega': 58.42, 'M0': 0.0, 'period': 27759, 'epoch': halley_epoch  # 76 years average
        },  # Halley's Comet - accurate elements
    ]
    labels = ['Earth', "Halley's Comet"]
    
    # Animate for 80 years starting from today, with 30-day steps
    animate_orbits(orbits, labels, duration_days=80*365, time_step_days=30)