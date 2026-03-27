import numpy as np
import astropy.io.fits as fits
from astropy.coordinates import SkyCoord
import astropy.units as u
from sklearn.neighbors import kneighbors_graph
import giotto_tda as gt
import matplotlib.pyplot as plt

print("Loading data...")
hdul = fits.open('spAll-v6_0_4.fits')
data = hdul[1].data
hdul.close()

galaxy_mask = (data['CLASS'] == 'GALAXY') & (data['ZWARNING'] == 0)
ra = data['PLUG_RA'][galaxy_mask]
dec = data['PLUG_DEC'][galaxy_mask]
print(f"Found {len(ra)} galaxies")

np.random.seed(42)
n_sample = 1000
idx = np.random.choice(len(ra), size=n_sample, replace=False)
ra_sub = ra[idx]
dec_sub = dec[idx]

print("Converting to Cartesian...")
coord = SkyCoord(ra=ra_sub*u.deg, dec=dec_sub*u.deg)
x, y, z = coord.cartesian.xyz.value
points = np.column_stack([x, y, z])

print("Computing persistent homology (this may take a moment)...")
rips = gt.Rips(max_edge_length=0.2, metric='euclidean')
diagrams = rips.fit_transform([points])[0]

print("Processing persistence...")
birth = diagrams[:, 0]
death = diagrams[:, 1]
dim = diagrams[:, 2].astype(int)
max_edge = rips.max_edge_length
death = np.where(np.isinf(death), max_edge, death)
persistence = death - birth
phi_tda = np.sum(persistence / ((dim + 1) * np.log(death + 1e-8)))

print(f"Φ_TDA = {phi_tda:.4f}")
np.save('phi_tda.npy', phi_tda)

gt.plot_diagram(diagrams)
plt.savefig('persistence_diagram.png')
print("Done.")