import numpy as np
from datetime import datetime, timedelta
from astroquery.jplhorizons import Horizons

def get_orbital_elements_astroquery(target_id, epoch=None, location='500@10'):
    """
    Get orbital elements from JPL Horizons using astroquery.
    
    Parameters:
    target_id : str - Target identifier (e.g., '399' for Earth, '90000001' for Halley)
    epoch : str or datetime - Epoch in format 'YYYY-MM-DD' or datetime object (default: current date)
    location : str - Observer location (default: '500@10' for Sun center)
    
    Returns:
    dict - Orbital elements
    """
    
    if epoch is None:
        epoch = datetime.now()
    elif isinstance(epoch, str):
        epoch = datetime.strptime(epoch, '%Y-%m-%d')
    
    try:
        # Format epoch as Julian Day for astroquery
        from astropy.time import Time
        if isinstance(epoch, datetime):
            time_obj = Time(epoch.strftime('%Y-%m-%d'))
        else:
            time_obj = Time(epoch)
        
        # Create Horizons object
        obj = Horizons(id=target_id, location=location, epochs=time_obj.jd)
        
        # Get orbital elements
        elements = obj.elements()
        
        if len(elements) == 0:
            print(f"No orbital elements found for target {target_id}")
            return None
        
        # Extract the first (and typically only) row
        elem = elements[0]
        
        # Convert to our standard format
        orbital_elements = {
            'epoch_jd': float(elem['datetime_jd']),
            'eccentricity': float(elem['e']),
            'semi_major_axis': float(elem['a']),  # Already in AU
            'inclination': float(elem['incl']),  # Already in degrees
            'longitude_ascending_node': float(elem['Omega']),  # Already in degrees
            'argument_periapsis': float(elem['w']),  # Already in degrees
            'mean_anomaly': float(elem['M']),  # Already in degrees
            'true_anomaly': float(elem['nu']),  # Already in degrees
            'periapsis_dist': float(elem['q']),  # Already in AU
            'apoapsis_dist': float(elem['Q']),  # Already in AU
            'period': float(elem['P']),  # Already in days
            'mean_motion': float(elem['n']),  # Already in degrees/day
            'time_periapsis_jd': float(elem['Tp_jd'])
        }
        
        return orbital_elements
        
    except Exception as e:
        print(f"Error fetching orbital elements for {target_id}: {e}")
        return None

def format_elements_for_animation(elements, epoch_datetime, name="Object"):
    """Format astroquery elements for use with orbit animation"""
    
    if not elements:
        return None
    
    formatted = {
        'a': elements.get('semi_major_axis', 0.0),
        'e': elements.get('eccentricity', 0.0),
        'i': elements.get('inclination', 0.0),
        'omega': elements.get('argument_periapsis', 0.0),
        'Omega': elements.get('longitude_ascending_node', 0.0),
        'M0': elements.get('mean_anomaly', 0.0),
        'period': elements.get('period', 365.25),
        'epoch': epoch_datetime,
        'name': name
    }
    
    return formatted

def get_orbital_elements_for_objects(object_ids, names=None, epoch=None):
    """
    Get orbital elements for multiple objects using astroquery
    
    Parameters:
    object_ids : list - JPL Horizons object IDs (e.g., ['399', '90000001', '499'])
    names : list - Object names for labeling (optional, defaults to Object 1, 2, etc.)
    epoch : str or datetime - Epoch (default: current date)
    
    Returns:
    list of dict - Formatted orbital elements for animation
    """
    
    if epoch is None:
        current_date = datetime.now()
        epoch_str = current_date.strftime('%Y-%m-%d')
    elif isinstance(epoch, str):
        current_date = datetime.strptime(epoch, '%Y-%m-%d')
        epoch_str = epoch
    else:
        current_date = epoch
        epoch_str = epoch.strftime('%Y-%m-%d')
    
    if names is None:
        names = [f"Object {i+1}" for i in range(len(object_ids))]
    
    print(f"Fetching orbital elements for epoch: {epoch_str}")
    
    elements_list = []
    for i, obj_id in enumerate(object_ids):
        name = names[i] if i < len(names) else f"Object {i+1}"
        print(f"Fetching {name} orbital elements (ID: {obj_id})...")
        
        elements = get_orbital_elements_astroquery(obj_id, current_date)
        if elements:
            formatted = format_elements_for_animation(elements, current_date, name)
            if formatted:
                elements_list.append(formatted)
                print(f"  ✓ Successfully retrieved {name} elements")
            else:
                print(f"  ✗ Failed to format elements for {name}")
        else:
            print(f"  ✗ Failed to retrieve elements for {name}")
    
    return elements_list

def get_current_orbital_elements():
    """Get current orbital elements for Earth and Halley's Comet using astroquery"""
    elements = get_orbital_elements_for_objects(['399', '90000001'], ['Earth', "Halley's Comet"])
    return elements[0] if len(elements) > 0 else None, elements[1] if len(elements) > 1 else None

def get_earth_elements(epoch=None):
    """Get Earth's orbital elements using astroquery"""
    return get_orbital_elements_astroquery('399', epoch)

def get_halley_elements(epoch=None):
    """Get Halley's Comet orbital elements using astroquery"""
    return get_orbital_elements_astroquery('90000001', epoch)

def get_mars_elements(epoch=None):
    """Get Mars orbital elements using astroquery"""
    return get_orbital_elements_astroquery('499', epoch)

def get_jupiter_elements(epoch=None):
    """Get Jupiter orbital elements using astroquery"""
    return get_orbital_elements_astroquery('599', epoch)

def get_saturn_elements(epoch=None):
    """Get Saturn orbital elements using astroquery"""
    return get_orbital_elements_astroquery('699', epoch)

def compare_with_manual_api():
    """Compare astroquery results with manual API implementation"""
    from jpl_horizons import get_orbital_elements_for_objects as get_manual
    
    print("=== COMPARISON: Astroquery vs Manual API ===\n")
    
    # Get elements using both methods
    aq_elements = get_orbital_elements_for_objects(['399', '90000001'], ['Earth', 'Halley'])
    manual_elements = get_manual(['399', '90000001'], ['Earth', 'Halley'])
    
    for i, name in enumerate(['Earth', 'Halley']):
        print(f"{name.upper()}:")
        if i < len(aq_elements) and i < len(manual_elements):
            aq = aq_elements[i]
            manual = manual_elements[i]
            
            print(f"  Semi-major axis: AQ={aq['a']:.6f} vs Manual={manual['a']:.6f} AU")
            print(f"  Eccentricity:    AQ={aq['e']:.6f} vs Manual={manual['e']:.6f}")
            print(f"  Inclination:     AQ={aq['i']:.4f}° vs Manual={manual['i']:.4f}°")
            print(f"  Arg. periapsis:  AQ={aq['omega']:.2f}° vs Manual={manual['omega']:.2f}°")
            print(f"  Long. asc. node: AQ={aq['Omega']:.2f}° vs Manual={manual['Omega']:.2f}°")
            print(f"  Mean anomaly:    AQ={aq['M0']:.2f}° vs Manual={manual['M0']:.2f}°")
            print(f"  Period:          AQ={aq['period']:.2f} vs Manual={manual['period']:.2f} days")
        print()

# Example usage and testing
if __name__ == "__main__":
    print("Testing JPL Horizons with astroquery...\n")
    
    # Test individual object
    print("=== INDIVIDUAL OBJECT TEST ===")
    earth_elements = get_earth_elements()
    if earth_elements:
        print("Earth orbital elements:")
        for key, value in earth_elements.items():
            print(f"  {key}: {value}")
    else:
        print("Failed to retrieve Earth elements")
    
    print("\n=== MULTIPLE OBJECTS TEST ===")
    # Test multiple objects
    object_ids = ['399', '90000001', '499']
    names = ['Earth', "Halley's Comet", 'Mars']
    elements = get_orbital_elements_for_objects(object_ids, names)
    
    print(f"\nSuccessfully retrieved {len(elements)} objects:")
    for elem in elements:
        print(f"  {elem['name']}: a={elem['a']:.3f} AU, e={elem['e']:.3f}, i={elem['i']:.1f}°")
    
    print("\n=== COMPARISON TEST ===")
    # Compare with manual API if available
    try:
        compare_with_manual_api()
    except ImportError:
        print("Manual API not available for comparison")
    
    print("\n=== ANIMATION READY ===")
    print("To use with animation:")
    print("from jpl_horizons_aq import get_orbital_elements_for_objects")
    print("from orbit_plotly_animate import animate_orbits")
    print()
    print("object_ids = ['399', '90000001']")
    print("names = ['Earth', \"Halley's Comet\"]")
    print("orbits = get_orbital_elements_for_objects(object_ids, names)")
    print("animate_orbits(orbits, names, duration_days=80*365, time_step_days=30)")