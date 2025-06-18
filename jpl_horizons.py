import requests
import numpy as np
from datetime import datetime, timedelta
import re

def get_orbital_elements_horizons(target_id, epoch=None, output_format='json'):
    """
    Get orbital elements from JPL Horizons system.
    
    Parameters:
    target_id : str - Target identifier (e.g., '399' for Earth, '1P' for Halley)
    epoch : str - Epoch in format 'YYYY-MM-DD' (default: current date)
    output_format : str - 'json' or 'text' (default: 'json')
    
    Returns:
    dict - Orbital elements
    """
    
    if epoch is None:
        epoch = datetime.now().strftime('%Y-%m-%d')
    
    # JPL Horizons API endpoint
    url = 'https://ssd.jpl.nasa.gov/api/horizons.api'
    
    # Calculate stop time (1 day after start)
    start_date = datetime.strptime(epoch, '%Y-%m-%d')
    stop_date = start_date + timedelta(days=1)
    stop_epoch = stop_date.strftime('%Y-%m-%d')
    
    # Parameters for orbital elements request
    params = {
        'format': output_format,
        'COMMAND': f"'{target_id}'",  # Quote the command
        'EPHEM_TYPE': 'ELEMENTS',
        'CENTER': '500@10',  # Sun center
        'START_TIME': f"'{epoch}'",  # Quote the date
        'STOP_TIME': f"'{stop_epoch}'",  # Quote the date
        'STEP_SIZE': '1d'
    }
    
    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        
        # Debug: check if there's an error in the response
        if output_format == 'json':
            result = response.json()
            if 'result' in result and 'ERROR' in result['result']:
                print(f"JPL Horizons API error: {result['result']}")
                return None
            return parse_horizons_json(result)
        else:
            if 'ERROR' in response.text:
                print(f"JPL Horizons API error: {response.text}")
                return None
            return parse_horizons_text(response.text)
            
    except requests.exceptions.RequestException as e:
        print(f"Error fetching data from JPL Horizons: {e}")
        return None
    except Exception as e:
        print(f"Unexpected error: {e}")
        return None

def parse_horizons_json(data):
    """Parse JSON response from JPL Horizons"""
    try:
        if 'result' in data:
            result_text = data['result']
            return parse_horizons_text(result_text)
        else:
            print("No result field in JSON response")
            return None
    except Exception as e:
        print(f"Error parsing JSON: {e}")
        return None

def parse_horizons_text(text):
    """Parse text response from JPL Horizons to extract orbital elements"""
    
    elements = {}
    
    try:
        # Split into lines
        lines = text.split('\n')
        
        # Find the ephemeris data section
        ephemeris_start = -1
        for i, line in enumerate(lines):
            if '$$SOE' in line:  # Start of ephemeris
                ephemeris_start = i + 1
                break
        
        if ephemeris_start == -1:
            print("Could not find ephemeris data in response")
            return None
        
        # Look for orbital elements in the ephemeris section
        elements = {}
        current_epoch_jd = None
        
        for i in range(ephemeris_start, len(lines)):
            line = lines[i].strip()
            
            if '$$EOE' in line:  # End of ephemeris
                break
                
            # Look for epoch line (JD = A.D. date)
            if '=' in line and 'A.D.' in line and 'TDB' in line:
                parts = line.split()
                if len(parts) > 0:
                    try:
                        current_epoch_jd = float(parts[0])
                    except ValueError:
                        pass
                continue
            
            # Parse orbital elements lines with key=value format
            if line and not line.startswith('$$') and not line.startswith('*') and '=' in line and 'A.D.' not in line:
                # Use regex to find key=value pairs (handles both KEY= and KEY =)
                import re
                matches = re.findall(r'([A-Z]+)\s*=\s*([0-9E\+\-\.]+)', line)
                for key, value in matches:
                    try:
                        val = float(value)
                        if key == 'EC':
                            elements['eccentricity'] = val
                        elif key == 'QR':
                            elements['periapsis_dist'] = val / 1e8  # Convert km to AU
                        elif key == 'IN':
                            elements['inclination'] = val
                        elif key == 'OM':
                            elements['longitude_ascending_node'] = val
                        elif key == 'W':
                            elements['argument_periapsis'] = val
                        elif key == 'Tp':
                            elements['time_periapsis_jd'] = val
                        elif key == 'MA':
                            elements['mean_anomaly'] = val
                        elif key == 'TA':
                            elements['true_anomaly'] = val
                        elif key == 'A':
                            elements['semi_major_axis'] = val / 1e8  # Convert km to AU
                        elif key == 'AD':
                            elements['apoapsis_dist'] = val / 1e8  # Convert km to AU
                        elif key == 'PR':
                            elements['period'] = val / 86400.0  # Convert seconds to days
                        elif key == 'N':
                            elements['mean_motion'] = val
                    except ValueError:
                        continue
        
        # Add epoch if found
        if current_epoch_jd:
            elements['epoch_jd'] = current_epoch_jd
        
        # Calculate missing values
        if 'semi_major_axis' not in elements and 'periapsis_dist' in elements and 'eccentricity' in elements:
            elements['semi_major_axis'] = elements['periapsis_dist'] / (1 - elements['eccentricity'])
        
        if 'period' not in elements and 'semi_major_axis' in elements:
            elements['period'] = 365.25 * (elements['semi_major_axis'] ** 1.5)
        
        
        return elements if elements else None
        
    except Exception as e:
        print(f"Error parsing Horizons text: {e}")
        return None

def get_earth_elements(epoch=None):
    """Get Earth's orbital elements from JPL Horizons"""
    return get_orbital_elements_horizons('399', epoch)

def get_halley_elements(epoch=None):
    """Get Halley's Comet orbital elements from JPL Horizons"""
    # Use the correct JPL comet ID for Halley
    return get_orbital_elements_horizons('90000001', epoch)

def format_elements_for_animation(elements, epoch_datetime, name="Object"):
    """Format JPL Horizons elements for use with orbit animation"""
    
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

def get_fallback_elements():
    """Get fallback orbital elements based on research if API fails"""
    current_date = datetime.now()
    j2000 = datetime(2000, 1, 1, 12, 0, 0)
    halley_epoch = datetime(1986, 2, 9)
    
    earth_fallback = {
        'a': 1.00000011, 'e': 0.01671022, 'i': 0.00005, 'omega': 114.20783,
        'Omega': -11.26064, 'M0': 357.51716, 'period': 365.25636, 'epoch': j2000,
        'name': 'Earth'
    }
    
    halley_fallback = {
        'a': 17.94, 'e': 0.967, 'i': 162.3, 'omega': 111.33,
        'Omega': 58.42, 'M0': 0.0, 'period': 27759, 'epoch': halley_epoch,
        'name': "Halley's Comet"
    }
    
    return earth_fallback, halley_fallback

def get_orbital_elements_for_objects(object_ids, names=None, epoch=None):
    """
    Get orbital elements for multiple objects from JPL Horizons
    
    Parameters:
    object_ids : list - JPL Horizons object IDs (e.g., ['399', '90000001', '499'])
    names : list - Object names for labeling (optional, defaults to Object 1, 2, etc.)
    epoch : str - Epoch in format 'YYYY-MM-DD' (default: current date)
    
    Returns:
    list of dict - Formatted orbital elements for animation
    """
    
    if epoch is None:
        current_date = datetime.now()
        epoch_str = current_date.strftime('%Y-%m-%d')
    else:
        current_date = datetime.strptime(epoch, '%Y-%m-%d')
        epoch_str = epoch
    
    if names is None:
        names = [f"Object {i+1}" for i in range(len(object_ids))]
    
    print(f"Fetching orbital elements for epoch: {epoch_str}")
    
    elements_list = []
    for i, obj_id in enumerate(object_ids):
        name = names[i] if i < len(names) else f"Object {i+1}"
        print(f"Fetching {name} orbital elements (ID: {obj_id})...")
        
        elements = get_orbital_elements_horizons(obj_id, epoch_str)
        if elements:
            formatted = format_elements_for_animation(elements, current_date, name)
            if formatted:
                elements_list.append(formatted)
            else:
                print(f"Failed to format elements for {name}")
        else:
            print(f"Failed to retrieve elements for {name}")
    
    return elements_list

def get_current_orbital_elements():
    """Get current orbital elements for Earth and Halley's Comet (legacy function)"""
    elements = get_orbital_elements_for_objects(['399', '90000001'], ['Earth', "Halley's Comet"])
    return elements[0] if len(elements) > 0 else None, elements[1] if len(elements) > 1 else None

# Example usage and testing
if __name__ == "__main__":
    # Test with simple request
    print("Testing JPL Horizons orbital elements retrieval...")
    
    # Get current elements
    earth, halley = get_current_orbital_elements()
    
    if earth:
        print("\nEarth orbital elements:")
        for key, value in earth.items():
            if key != 'epoch':
                print(f"  {key}: {value}")
            else:
                print(f"  {key}: {value.strftime('%Y-%m-%d %H:%M:%S')}")
    else:
        print("Failed to retrieve Earth elements")
    
    if halley:
        print("\nHalley's Comet orbital elements:")
        for key, value in halley.items():
            if key != 'epoch':
                print(f"  {key}: {value}")
            else:
                print(f"  {key}: {value.strftime('%Y-%m-%d %H:%M:%S')}")
    else:
        print("Failed to retrieve Halley elements")
    
    # Example of using with animation
    if earth and halley:
        print("\nFormatted for orbit animation:")
        print("orbits = [")
        print(f"    {earth},")
        print(f"    {halley}")
        print("]")
        print("labels = ['Earth', \"Halley's Comet\"]")
        print("animate_orbits(orbits, labels, duration_days=80*365, time_step_days=30)")