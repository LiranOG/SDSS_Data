import numpy as np
import astropy.io.fits as fits
from astropy.coordinates import SkyCoord
import astropy.units as u
import ripser
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

print("Computing persistent homology...")
max_edge = 0.2
result = ripser.ripser(points, maxdim=2, thresh=max_edge)
dgms = result['dgms']

print("Processing persistence...")
phi_tda = 0.0
for dim, diagram in enumerate(dgms):
    print(f"Dimension {dim}: {len(diagram)} features")
    for point in diagram:
        birth, death = point
        if death == np.inf:
            death = max_edge
        persistence = death - birth
        if persistence > 0:   # רק חיוביים
            term = persistence / ((dim + 1) * np.log(death + 1))
            phi_tda += term
            print(f"  dim={dim}, birth={birth:.4f}, death={death:.4f}, term={term:.4f}")
        else:
            print(f"  Skipping non-positive persistence: {persistence:.4f}")

print(f"Φ_TDA = {phi_tda:.4f}")
np.save('phi_tda.npy', phi_tda)

# Plot persistence diagram
plt.figure()
for dim, diagram in enumerate(dgms):
    if len(diagram) == 0:
        continue
    # הסר אינסוף לצורך הצגה
    finite = diagram[np.isfinite(diagram[:, 1])]
    plt.scatter(finite[:, 0], finite[:, 1], label=f'dim {dim}')
plt.plot([0, max_edge], [0, max_edge], 'k--')
plt.xlabel('Birth')
plt.ylabel('Death')
plt.legend()
plt.savefig('persistence_diagram.png')
print("Saved persistence_diagram.png")