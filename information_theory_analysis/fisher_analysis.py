#!/usr/bin/env python3
"""
Compute Fisher information and I(X;T) from the HEALPix density map.
"""
import numpy as np
import healpy as hp
import matplotlib.pyplot as plt

# ------------------------------
# Load map
# ------------------------------
density = hp.read_map('density_map.fits')

# ------------------------------
# Parameters
# ------------------------------
lmax = 512          # maximum multipole (should be <= 2*nside)
# For a simple noise model, we estimate N_l from the variance of the map.
# In reality, N_l is often derived from the Poisson shot noise.
# We'll compute the power spectrum of the map and then assume that on large scales,
# the signal dominates; we can estimate N_l as the mean of C_l at high l where signal is negligible.
# For a more accurate noise estimate, one would use the number of galaxies per pixel.

# ------------------------------
# Spherical harmonic transform
# ------------------------------
alm = hp.map2alm(density, lmax=lmax)
Cl = hp.alm2cl(alm)

# ------------------------------
# Noise power spectrum
# ------------------------------
# Estimate noise level from the power at high l (e.g., l > 0.8*lmax)
l_high = int(0.8 * lmax)
noise_level = np.mean(Cl[l_high:])
# Alternatively, compute the shot noise: N_l = 1 / n_bar, where n_bar is mean counts per pixel.
# We'll use the noise_level from the high-l region as a simple estimate.
Nl = np.ones_like(Cl) * noise_level

# ------------------------------
# Fisher Information per l
# ------------------------------
Fl = (2 * np.arange(lmax+1) + 1) * (Cl / (Cl + Nl))**2

# ------------------------------
# Mutual information I(X;T)
# ------------------------------
def mutual_info_from_fisher(Fl, lmin=2):
    MI = 0.0
    for l in range(lmin, len(Fl)):
        MI += 0.5 * np.log(1 + Fl[l] / (2*l + 1))
    return MI

MI = mutual_info_from_fisher(Fl)
print(f"Estimated I(X;T) = {MI:.4f} nats")

# ------------------------------
# Save results
# ------------------------------
np.savez('fisher_results.npz', l=np.arange(lmax+1), Cl=Cl, Nl=Nl, Fl=Fl, MI=MI)

# ------------------------------
# Plot power spectrum
# ------------------------------
plt.figure()
plt.loglog(Cl, label='C_l')
plt.loglog(Nl, '--', label='Noise N_l')
plt.xlabel(r'$\ell$')
plt.ylabel(r'$C_\ell$')
plt.legend()
plt.savefig('power_spectrum.png')
plt.close()
print("Power spectrum plot saved to power_spectrum.png")
