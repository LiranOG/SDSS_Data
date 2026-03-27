#!/usr/bin/env python3
"""
Compute persistent homology and estimate Φ_TDA from a subset of galaxies.
"""
import numpy as np
import astropy.io.fits as fits
from astropy.coordinates import SkyCoord
import astropy.units as u
from sklearn.neighbors import kneighbors_graph
import giotto_tda as gt
import matplotlib.pyplot as plt

# ------------------------------
# Load data and subsample
# ------------------------------
hdul = fits.open('spAll-v6_0_4.fits')
data = hdul[1].data
hdul.close()

# Select galaxies (CLASS == 'GALAXY') with good redshift
galaxy_mask = (data['CLASS'] == 'GALAXY') & (data['ZWARNING'] == 0)
ra = data['PLUG_RA'][galaxy_mask]
dec = data['PLUG_DEC'][galaxy_mask]
z = data['Z'][galaxy_mask]

# Random subsample for tractability
np.random.seed(42)
n_sample = 10000
if len(ra) > n_sample:
    idx = np.random.choice(len(ra), size=n_sample, replace=False)
    ra_sub = ra[idx]
    dec_sub = dec[idx]
    z_sub = z[idx]
else:
    ra_sub = ra
    dec_sub = dec
    z_sub = z

# Convert to Cartesian coordinates (unit sphere)
coord = SkyCoord(ra=ra_sub*u.deg, dec=dec_sub*u.deg)
x, y, z_coord = coord.cartesian.xyz.value
points = np.column_stack([x, y, z_coord])

# ------------------------------
# Persistent homology with Ripser
# ------------------------------
rips = gt.Rips(max_edge_length=0.2, metric='euclidean')
diagrams = rips.fit_transform([points])[0]

# ------------------------------
# Compute Φ_TDA scalar
# ------------------------------
birth = diagrams[:, 0]
death = diagrams[:, 1]
dim = diagrams[:, 2].astype(int)

# Replace infinite persistence with max_edge_length
max_edge = rips.max_edge_length
death = np.where(np.isinf(death), max_edge, death)

persistence = death - birth
phi_tda = np.sum(persistence / ((dim + 1) * np.log(death + 1e-8)))

print(f"Φ_TDA estimate = {phi_tda:.4f}")

# Save results
np.save('phi_tda.npy', phi_tda)
np.save('persistence_diagrams.npy', diagrams)

# Plot persistence diagram
gt.plot_diagram(diagrams)
plt.savefig('persistence_diagram.png')
plt.close()
print("Persistence diagram saved to persistence_diagram.png")