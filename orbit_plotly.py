import numpy as np
import plotly.graph_objects as go
import plotly.express as px

def plot_orbits(orbital_elements_list, labels=None, n_points=1000):
    """
    Plot multiple orbits of solar system objects given their orbital elements using Plotly.
    
    Parameters:
    orbital_elements_list : list of dicts - Each dict contains orbital elements:
        {'a': float, 'e': float, 'i': float, 'omega': float, 'Omega': float, 'M0': float}
    labels : list of str - Names for each orbit (optional)
    n_points : int - Number of points to plot per orbit
    """
    
    fig = go.Figure()
    
    # Add Sun at origin
    fig.add_trace(go.Scatter3d(
        x=[0], y=[0], z=[0],
        mode='markers',
        marker=dict(size=15, color='yellow'),
        name='Sun'
    ))
    
    colors = px.colors.qualitative.Set1
    all_x, all_y, all_z = [], [], []
    
    for i, elements in enumerate(orbital_elements_list):
        a = elements['a']
        e = elements['e']
        i_deg = elements['i']
        omega = elements['omega']
        Omega = elements['Omega']
        M0 = elements['M0']
        
        # Convert angles to radians
        i_rad = np.radians(i_deg)
        omega_rad = np.radians(omega)
        Omega_rad = np.radians(Omega)
        
        # Generate true anomaly values
        nu = np.linspace(0, 2*np.pi, n_points)
        
        # Calculate distance from focus
        r = a * (1 - e**2) / (1 + e * np.cos(nu))
        
        # Orbital plane coordinates
        x_orb = r * np.cos(nu)
        y_orb = r * np.sin(nu)
        z_orb = np.zeros_like(x_orb)
        
        # Rotation matrices
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
        
        # Combined rotation matrix
        R = R_Omega @ R_i @ R_omega
        
        # Transform to heliocentric coordinates
        coords_orb = np.array([x_orb, y_orb, z_orb])
        coords_helio = R @ coords_orb
        
        x, y, z = coords_helio
        
        # Collect all coordinates for axis scaling
        all_x.extend(x)
        all_y.extend(y)
        all_z.extend(z)
        
        # Plot orbit
        label = labels[i] if labels and i < len(labels) else f'Orbit {i+1}'
        color = colors[i % len(colors)]
        
        fig.add_trace(go.Scatter3d(
            x=x, y=y, z=z,
            mode='lines',
            line=dict(width=4, color=color),
            name=label
        ))
        
        # Plot periapsis
        r_peri = a * (1 - e)
        peri_orb = np.array([r_peri, 0, 0])
        peri_helio = R @ peri_orb
        
        fig.add_trace(go.Scatter3d(
            x=[peri_helio[0]], y=[peri_helio[1]], z=[peri_helio[2]],
            mode='markers',
            marker=dict(size=6, color=color),
            name=f'{label} Periapsis',
            showlegend=False
        ))
    
    # Calculate symmetric ranges centered on Sun at origin
    max_x = max(abs(min(all_x)), abs(max(all_x)))
    max_y = max(abs(min(all_y)), abs(max(all_y)))
    max_z = max(abs(min(all_z)), abs(max(all_z)))
    
    # Set layout
    fig.update_layout(
        title='Solar System Orbits',
        scene=dict(
            xaxis_title='X (AU)',
            yaxis_title='Y (AU)',
            zaxis_title='Z (AU)',
            xaxis=dict(range=[-max_x, max_x]),
            yaxis=dict(range=[-max_y, max_y]),
            zaxis=dict(range=[-max_z, max_z]),
            aspectmode='cube'
        ),
        width=800,
        height=600
    )
    
    fig.show()
    return fig

def plot_orbit(a, e, i, omega, Omega, M0, n_points=1000):
    """
    Plot the orbit of a single solar system object given its orbital elements using Plotly.
    
    Parameters:
    a : float - Semi-major axis (AU)
    e : float - Eccentricity
    i : float - Inclination (degrees)
    omega : float - Argument of periapsis (degrees)
    Omega : float - Longitude of ascending node (degrees)
    M0 : float - Mean anomaly at epoch (degrees)
    n_points : int - Number of points to plot
    """
    
    elements = {'a': a, 'e': e, 'i': i, 'omega': omega, 'Omega': Omega, 'M0': M0}
    return plot_orbits([elements], n_points=n_points)

# Example usage
if __name__ == "__main__":
    # Plot multiple orbits
    orbits = [
        {'a': 1.0, 'e': 0.0167, 'i': 0.0, 'omega': 102.9, 'Omega': 0.0, 'M0': 0.0},  # Earth
        {'a': 17.8, 'e': 0.967, 'i': 162.3, 'omega': 111.3, 'Omega': 58.4, 'M0': 0.0},  # Halley's Comet
    ]
    labels = ['Earth', "Halley's Comet"]
    
    plot_orbits(orbits, labels)