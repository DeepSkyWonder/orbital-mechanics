import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D

def plot_orbits(orbital_elements_list, labels=None, n_points=1000):
    """
    Plot multiple orbits of solar system objects given their orbital elements.
    
    Parameters:
    orbital_elements_list : list of dicts - Each dict contains orbital elements:
        {'a': float, 'e': float, 'i': float, 'omega': float, 'Omega': float, 'M0': float}
    labels : list of str - Names for each orbit (optional)
    n_points : int - Number of points to plot per orbit
    """
    
    fig = plt.figure(figsize=(12, 10))
    ax = fig.add_subplot(111, projection='3d')
    
    # Plot Sun at origin
    ax.scatter([0], [0], [0], color='yellow', s=200, label='Sun')
    
    colors = plt.cm.tab10(np.linspace(0, 1, len(orbital_elements_list)))
    
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
        ax.plot(x, y, z, color=colors[i], linewidth=2, label=label)
        
        # Plot periapsis
        r_peri = a * (1 - e)
        peri_orb = np.array([r_peri, 0, 0])
        peri_helio = R @ peri_orb
        ax.scatter(*peri_helio, color=colors[i], s=30, marker='o', alpha=0.7)
    
    # Set labels and title
    ax.set_xlabel('X (AU)')
    ax.set_ylabel('Y (AU)')
    ax.set_zlabel('Z (AU)')
    ax.set_title('Solar System Orbits')
    ax.legend()
    
    # Set axis limits based on actual orbital data bounds
    ax.set_xlim([min(all_x), max(all_x)])
    ax.set_ylim([min(all_y), max(all_y)])
    ax.set_zlim([min(all_z), max(all_z)])
    
    plt.show()
    
    return fig, ax

def plot_orbit(a, e, i, omega, Omega, M0, n_points=1000):
    """
    Plot the orbit of a single solar system object given its orbital elements.
    
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