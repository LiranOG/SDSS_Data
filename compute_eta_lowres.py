import numpy as np
import healpy as hp
from sklearn.feature_selection import mutual_info_regression
import matplotlib.pyplot as plt
import warnings
warnings.filterwarnings('ignore')

print("=" * 60)
print("Computing I(T;Y) and eta_IB for cosmic scale (nside=64)")
print("=" * 60)

# Load low-resolution maps
density = hp.read_map('density_map_nside64.fits')
cluster = hp.read_map('cluster_map_nside64.fits')

print(f"Density map: nside={hp.get_nside(density)}, npix={len(density)}")
print(f"Cluster map: nside={hp.get_nside(cluster)}, npix={len(cluster)}")

# Use only pixels with valid data
valid = (density > 0) & (np.isfinite(cluster))
T_valid = density[valid]
Y_valid = cluster[valid]

print(f"Valid pixels: {np.sum(valid)} / {len(density)}")

# Mutual Information
T_2d = T_valid.reshape(-1, 1)
mi = mutual_info_regression(T_2d, Y_valid, random_state=42)[0]
print(f"I(T;Y) = {mi:.6f} nats")

# Load I(X;T) from earlier
fisher = np.load('fisher_results.npz')
I_XT = fisher['MI']
print(f"I(X;T) = {I_XT:.6f} nats")

# eta_IB
eta_IB = mi / I_XT
print(f"eta_IB = {eta_IB:.6f}")

# Save results
np.savez('eta_IB_cosmic_lowres.npz',
         I_TY=mi,
         I_XT=I_XT,
         eta_IB=eta_IB,
         n_valid=np.sum(valid))

with open('eta_IB_cosmic_lowres.txt', 'w') as f:
    f.write("Cosmic scale eta_IB results (nside=64)\n")
    f.write("======================================\n")
    f.write(f"I(T;Y) = {mi:.6f} nats\n")
    f.write(f"I(X;T) = {I_XT:.6f} nats\n")
    f.write(f"eta_IB = {eta_IB:.6f}\n")
    f.write(f"Valid pixels: {np.sum(valid)}\n")

print("\nSaved: eta_IB_cosmic_lowres.npz, eta_IB_cosmic_lowres.txt")

# Scatter plot
idx = np.random.choice(len(T_valid), min(10000, len(T_valid)), replace=False)
plt.figure(figsize=(6, 5))
plt.scatter(np.log10(T_valid[idx] + 0.01), np.log10(Y_valid[idx] + 0.01), s=1, alpha=0.5)
plt.xlabel('log10(galaxy density + 0.01)')
plt.ylabel('log10(cluster count + 0.01)')
plt.title(f'Galaxy density vs cluster abundance\nI(T;Y) = {mi:.3f} nats, eta_IB = {eta_IB:.3f}')
plt.tight_layout()
plt.savefig('eta_IB_cosmic_scatter_lowres.png', dpi=150)
print("Saved: eta_IB_cosmic_scatter_lowres.png")

print("\n" + "=" * 60)
print("Summary:")
print(f"  I(X;T) = {I_XT:.4f} nats")
print(f"  I(T;Y) = {mi:.4f} nats")
print(f"  eta_IB = {eta_IB:.4f}")
print("=" * 60)