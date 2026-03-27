#!/usr/bin/env python3
import numpy as np
import astropy.io.fits as fits
from astropy.coordinates import SkyCoord
import astropy.units as u
import healpy as hp
import matplotlib.pyplot as plt

# Load data
hdul = fits.open('spAll-v6_0_4.fits')
data = hdul[1].data
hdul.close()

# Select galaxies (CLASS == 'GALAXY')
galaxy_mask = (data['CLASS'] == 'GALAXY')
# Optional: quality cut (ZWARNING == 0)
galaxy_mask &= (data['ZWARNING'] == 0)

ra = data['PLUG_RA'][galaxy_mask]
dec = data['PLUG_DEC'][galaxy_mask]
# Redshift is available as 'Z' if needed, but for angular map we don't need it.

# HEALPix parameters
nside = 512
npix = hp.nside2npix(nside)

# Convert RA/Dec to pixel indices
pix = hp.ang2pix(nside, np.radians(90 - dec), np.radians(ra))

# Count galaxies per pixel
counts = np.bincount(pix, minlength=npix)

# Normalise to mean density (ignore empty pixels)
mean_density = np.mean(counts[counts > 0])
density = counts / mean_density

# Save map
hp.write_map('density_map.fits', density, overwrite=True, coord='C')
print("Density map saved to density_map.fits")

# Visualise
hp.mollview(density, title='SDSS DR18 Galaxy Density Map (nside=512)')
plt.savefig('density_map.png', dpi=150)
plt.close()
print("Visualisation saved to density_map.png")