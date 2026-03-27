# degrade_cluster_map.py
import numpy as np
import healpy as hp

# Load the original cluster map
cluster_high = hp.read_map('cluster_map.fits')
nside_high = hp.get_nside(cluster_high)

# Degrade to nside=64 (pixels: 12*64^2 = 49152)
nside_low = 64
cluster_low = hp.ud_grade(cluster_high, nside_out=nside_low, order_in='NESTED', order_out='NESTED')

# Save
hp.write_map('cluster_map_nside64.fits', cluster_low, overwrite=True)
print(f"Cluster map degraded to nside={nside_low}, npix={len(cluster_low)}")
print(f"Min: {cluster_low.min():.2f}, Max: {cluster_low.max():.2f}, Mean: {cluster_low.mean():.2f}")

# degrade_density_map.py
import numpy as np
import healpy as hp

density_high = hp.read_map('density_map.fits')
nside_low = 64
density_low = hp.ud_grade(density_high, nside_out=nside_low, order_in='NESTED', order_out='NESTED')

hp.write_map('density_map_nside64.fits', density_low, overwrite=True)
print(f"Density map degraded to nside={nside_low}, npix={len(density_low)}")
print(f"Min: {density_low.min():.2f}, Max: {density_low.max():.2f}")