# Orbital Mechanics Visualization Tools

Interactive 3D visualization tools for plotting and animating celestial object orbits using JPL Horizons data.

## Files Overview

- **`jpl_horizons_aq.py`** - JPL Horizons API using astroquery (RECOMMENDED)
- **`orbit_plotly_animate.py`** - Interactive 3D orbit animation with time evolution
- **`orbit_plotly.py`** - Static 3D orbit plotting
- **`jpl_horizons.py`** - Manual JPL Horizons API implementation (backup)
- **`orbit.py`** - Original matplotlib version

## Quick Setup

```python
# Install dependencies
!pip install plotly astroquery numpy requests

# Import and use
from jpl_horizons_aq import get_orbital_elements_for_objects
from orbit_plotly_animate import animate_orbits

# Get orbital elements for Earth and Halley's Comet
object_ids = ['399', '90000001']  # Earth, Halley's Comet
names = ['Earth', "Halley's Comet"]
orbits = get_orbital_elements_for_objects(object_ids, names)

# Create 80-year animation
animate_orbits(orbits, names, duration_days=80*365, time_step_days=30)
```

## Common JPL Horizons Object IDs

- **399**: Earth
- **499**: Mars
- **599**: Jupiter
- **699**: Saturn
- **90000001**: Halley's Comet
- **90000010**: Comet NEOWISE
- **2000001**: Ceres (asteroid)

## Key Comparisons Made

### JPL Horizons vs Research Data
- **Earth semi-major axis**: JPL=1.495544 AU vs Research=1.000000 AU
- **Halley semi-major axis**: JPL=26.97 AU vs Research=17.94 AU
- JPL provides osculating elements (instantaneous) vs mean elements (averaged)
- JPL data is more accurate for current positions

### Astroquery vs Manual API
- **Earth semi-major axis**: AQ=0.999542 AU vs Manual=1.495544 AU
- **Astroquery is more accurate** due to better unit handling
- **Astroquery recommended** for production use

## Authentication Setup for GitHub

```bash
# Check if gh CLI is installed
!gh --version

# Authenticate (follow prompts)
!gh auth login

# Create repository and push files
!git init
!git add *.py *.md
!git commit -m "Initial commit: orbital mechanics tools"
!gh repo create orbital-mechanics --public
!git remote add origin https://github.com/$(gh api user --jq .login)/orbital-mechanics.git
!git branch -M main
!git push -u origin main
```

## Restoration Script for New Sessions

```python
def setup_orbital_tools():
    """Quick setup for orbital mechanics tools in new Colab session"""
    import os, subprocess, sys
    
    # Install dependencies
    subprocess.run(['pip', 'install', '-q', 'plotly', 'astroquery'])
    
    # Clone repository (replace USERNAME with your GitHub username)
    repo_url = "https://github.com/USERNAME/orbital-mechanics.git"
    if not os.path.exists('/content/orbital-mechanics'):
        print("📡 Cloning repository...")
        subprocess.run(['git', 'clone', repo_url], cwd='/content')
    
    # Add to Python path and change directory
    sys.path.append('/content/orbital-mechanics')
    os.chdir('/content/orbital-mechanics')
    
    print("✅ Orbital mechanics tools ready!")

# Run this at start of new sessions
setup_orbital_tools()
```

## Example Usage

### Earth and Halley Animation
```python
from jpl_horizons_aq import get_orbital_elements_for_objects
from orbit_plotly_animate import animate_orbits

# Earth and Halley's Comet over 80 years
orbits = get_orbital_elements_for_objects(['399', '90000001'], ['Earth', "Halley's Comet"])
animate_orbits(orbits, ['Earth', "Halley's Comet"], duration_days=80*365, time_step_days=30)
```

### Multiple Planets
```python
# Inner solar system
object_ids = ['399', '499', '599']  # Earth, Mars, Jupiter
names = ['Earth', 'Mars', 'Jupiter']
orbits = get_orbital_elements_for_objects(object_ids, names)
animate_orbits(orbits, names, duration_days=10*365, time_step_days=10)
```

### Static Plot
```python
from orbit_plotly import plot_orbits

orbits = [
    {'a': 1.0, 'e': 0.017, 'i': 0.0, 'omega': 114.2, 'Omega': -11.3, 'M0': 357.5, 'period': 365.25, 'epoch': datetime.now()},
    {'a': 17.94, 'e': 0.967, 'i': 162.3, 'omega': 111.33, 'Omega': 58.42, 'M0': 0.0, 'period': 27759, 'epoch': datetime(1986, 2, 9)}
]
labels = ['Earth', "Halley's Comet"]
plot_orbits(orbits, labels)
```

## Technical Notes

- Uses JPL Horizons API for accurate orbital elements
- Implements Kepler's equation solver for position calculation
- Supports heliocentric ecliptic coordinate system
- Handles time evolution and orbital perturbations
- Interactive 3D visualization with Plotly

## Dependencies

- plotly (3D visualization)
- astroquery (JPL Horizons API)
- numpy (numerical calculations)
- requests (HTTP requests)
- datetime (time handling)

Created with Claude Code assistance for accurate orbital mechanics visualization.