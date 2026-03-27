#!/usr/bin/env python3
"""
3D Cosmic Web Classification from SDSS DR18
Following Nandi & Pandey 2025 (arXiv:2507.18614)
"""

import numpy as np
import astropy.io.fits as fits
from astropy.cosmology import Planck18 as cosmo
from astropy.coordinates import SkyCoord, CartesianRepresentation, ICRS
import astropy.units as u
import healpy as hp
from scipy.ndimage import gaussian_filter
import matplotlib.pyplot as plt
import warnings
warnings.filterwarnings('ignore')

# ------------------------------------------------------------
# 1. Load and prepare galaxy catalog
# ------------------------------------------------------------
print("Loading SDSS DR18 galaxy catalog...")
hdul = fits.open('spAll-v6_0_4.fits')
data = hdul[1].data
hdul.close()

# Select galaxies with reliable redshift and classification
gal_mask = (data['CLASS'] == 'GALAXY') & (data['ZWARNING'] == 0)
ra = data['PLUG_RA'][gal_mask]
dec = data['PLUG_DEC'][gal_mask]
z = data['Z'][gal_mask]
print(f"Number of galaxies selected: {len(ra)}")

# ------------------------------------------------------------
# 2. Convert to comoving Cartesian coordinates
# ------------------------------------------------------------
print("Converting to comoving coordinates...")
coord_sky = SkyCoord(ra=ra*u.deg, dec=dec*u.deg, distance=cosmo.comoving_distance(z))
x = coord_sky.cartesian.x.value
y = coord_sky.cartesian.y.value
z_coord = coord_sky.cartesian.z.value

# ------------------------------------------------------------
# 3. Define 3D grid with margins
# ------------------------------------------------------------
margin = 0.1   # add 10% margin to avoid edge effects
xmin, xmax = np.min(x), np.max(x)
ymin, ymax = np.min(y), np.max(y)
zmin, zmax = np.min(z_coord), np.max(z_coord)
xmin -= margin * (xmax - xmin)
xmax += margin * (xmax - xmin)
ymin -= margin * (ymax - ymin)
ymax += margin * (ymax - ymin)
zmin -= margin * (zmax - zmin)
zmax += margin * (zmax - zmin)

# Number of grid cells (reduce if memory is an issue)
ngrid = 128   # 128^3 is 2M cells – comfortable with 6k galaxies
print(f"Grid size: {ngrid}^3")

x_edges = np.linspace(xmin, xmax, ngrid+1)
y_edges = np.linspace(ymin, ymax, ngrid+1)
z_edges = np.linspace(zmin, zmax, ngrid+1)

# ------------------------------------------------------------------
# 4. Cloud-in-Cell assignment with safe boundary handling
# ------------------------------------------------------------------
def cic_weights(pos, edges):
    """Return indices and weights for CIC interpolation. Clamps indices to valid range."""
    idx = np.searchsorted(edges, pos) - 1
    idx = np.clip(idx, 0, len(edges)-2)
    w1 = (edges[idx+1] - pos) / (edges[idx+1] - edges[idx])
    w2 = 1.0 - w1
    w1 = np.clip(w1, 0.0, 1.0)
    w2 = np.clip(w2, 0.0, 1.0)
    return idx, w1, w2

rho = np.zeros((ngrid, ngrid, ngrid), dtype=np.float32)
print("Assigning galaxies to grid...")
for i in range(len(x)):
    ix, wx1, wx2 = cic_weights(x[i], x_edges)
    iy, wy1, wy2 = cic_weights(y[i], y_edges)
    iz, wz1, wz2 = cic_weights(z_coord[i], z_edges)
    rho[ix, iy, iz] += wx1*wy1*wz1
    rho[ix+1, iy, iz] += wx2*wy1*wz1
    rho[ix, iy+1, iz] += wx1*wy2*wz1
    rho[ix, iy, iz+1] += wx1*wy1*wz2
    rho[ix+1, iy+1, iz] += wx2*wy2*wz1
    rho[ix+1, iy, iz+1] += wx2*wy1*wz2
    rho[ix, iy+1, iz+1] += wx1*wy2*wz2
    rho[ix+1, iy+1, iz+1] += wx2*wy2*wz2

# ------------------------------------------------------------
# 5. Density contrast and smoothing
# ------------------------------------------------------------
mean_rho = np.mean(rho)
delta = (rho - mean_rho) / mean_rho
print(f"Mean density: {mean_rho:.3f}, min delta: {delta.min():.3f}, max delta: {delta.max():.3f}")

# Gaussian smoothing (8 Mpc scale)
cell_size = (xmax - xmin) / ngrid   # in Mpc
smooth_scale = 8.0  # Mpc
sigma_cells = smooth_scale / cell_size
print(f"Smoothing with Gaussian sigma = {sigma_cells:.2f} cells")
delta_smooth = gaussian_filter(delta, sigma=sigma_cells, mode='wrap')

# ------------------------------------------------------------
# 6. Poisson equation for potential (FFT)
# ------------------------------------------------------------
print("Solving Poisson equation...")
delta_fft = np.fft.fftn(delta_smooth)
kx = np.fft.fftfreq(ngrid, d=cell_size) * (2*np.pi)
ky = np.fft.fftfreq(ngrid, d=cell_size) * (2*np.pi)
kz = np.fft.fftfreq(ngrid, d=cell_size) * (2*np.pi)
K2 = kx[:,None,None]**2 + ky[None,:,None]**2 + kz[None,None,:]**2
K2[0,0,0] = 1.0   # avoid division by zero
phi_fft = -delta_fft / K2
phi_fft[0,0,0] = 0.0
phi = np.real(np.fft.ifftn(phi_fft))

# ------------------------------------------------------------
# 7. Compute Hessian (second derivatives) of Φ
# ------------------------------------------------------------
print("Computing Hessian...")
def deriv2(phi_fft, kx, ky, kz, axis1, axis2):
    if axis1 == axis2:
        k = [kx, ky, kz][axis1]
        return np.real(np.fft.ifftn(-k**2 * phi_fft))
    else:
        k1 = [kx, ky, kz][axis1]
        k2 = [kx, ky, kz][axis2]
        return np.real(np.fft.ifftn(-k1 * k2 * phi_fft))

phi_fft = np.fft.fftn(phi)
phi_xx = deriv2(phi_fft, kx, ky, kz, 0, 0)
phi_yy = deriv2(phi_fft, kx, ky, kz, 1, 1)
phi_zz = deriv2(phi_fft, kx, ky, kz, 2, 2)
phi_xy = deriv2(phi_fft, kx, ky, kz, 0, 1)
phi_xz = deriv2(phi_fft, kx, ky, kz, 0, 2)
phi_yz = deriv2(phi_fft, kx, ky, kz, 1, 2)

# ------------------------------------------------------------
# 8. Classify each cell by number of positive eigenvalues
# ------------------------------------------------------------
print("Classifying cells...")
def classify_cell(H):
    eig = np.linalg.eigvalsh(H)
    return np.sum(eig > 0)

npos = np.zeros((ngrid, ngrid, ngrid), dtype=np.int8)
for i in range(ngrid):
    for j in range(ngrid):
        for k in range(ngrid):
            H = np.array([[phi_xx[i,j,k], phi_xy[i,j,k], phi_xz[i,j,k]],
                          [phi_xy[i,j,k], phi_yy[i,j,k], phi_yz[i,j,k]],
                          [phi_xz[i,j,k], phi_yz[i,j,k], phi_zz[i,j,k]]])
            npos[i,j,k] = classify_cell(H)

cluster_mask = (npos == 3)   # cluster cells
print(f"Number of cluster cells: {np.sum(cluster_mask)} / {ngrid**3}")

# ------------------------------------------------------------
# 9. Project cluster cells to HEALPix map (Y)
# ------------------------------------------------------------
print("Projecting cluster cells to HEALPix map...")
grid_x = (x_edges[:-1] + x_edges[1:]) / 2.0
grid_y = (y_edges[:-1] + y_edges[1:]) / 2.0
grid_z = (z_edges[:-1] + z_edges[1:]) / 2.0

nside = 512
npix = hp.nside2npix(nside)
cluster_map = np.zeros(npix, dtype=np.float32)

# Flatten coordinates and mask
coords = np.stack(np.meshgrid(grid_x, grid_y, grid_z, indexing='ij'), axis=-1).reshape(-1, 3)
cluster_flat = cluster_mask.reshape(-1)

# Process in chunks to avoid memory issues
chunk_size = 200000
n_cells = coords.shape[0]
print(f"Processing {n_cells} cells in chunks of {chunk_size}...")
for start in range(0, n_cells, chunk_size):
    end = min(start+chunk_size, n_cells)
    chunk = coords[start:end]
    
    # Convert Cartesian coordinates to SkyCoord properly
    cart = CartesianRepresentation(chunk[:,0]*u.Mpc, chunk[:,1]*u.Mpc, chunk[:,2]*u.Mpc)
    sc = SkyCoord(cart, frame=ICRS)
    
    ra_deg = sc.ra.deg
    dec_deg = sc.dec.deg
    
    pix = hp.ang2pix(nside, np.radians(90 - dec_deg), np.radians(ra_deg))
    
    # Add cluster counts
    for p, c in zip(pix, cluster_flat[start:end]):
        cluster_map[p] += c

# Save Y map
hp.write_map('cluster_map.fits', cluster_map, overwrite=True, coord='C')
print("Cluster map saved to cluster_map.fits")

# Visualisation
hp.mollview(cluster_map, title='Cluster abundance Y (from Hessian classification)', nest=False)
plt.savefig('cluster_map.png')
plt.close()
print("Visualisation saved to cluster_map.png")

# Optional: save classification
np.save('classification_3d.npy', npos)
print("3D classification saved to classification_3d.npy")