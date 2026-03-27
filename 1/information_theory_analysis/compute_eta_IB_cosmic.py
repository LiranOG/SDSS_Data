#!/usr/bin/env python3
"""
Compute I(T;Y) and η_IB for the cosmic scale using:
- T: galaxy density map (density_map.fits)
- Y: cluster abundance map (cluster_map.fits)
- I(X;T): from fisher_results.npz
"""

import numpy as np
import healpy as hp
from sklearn.feature_selection import mutual_info_regression
import matplotlib.pyplot as plt
import warnings
warnings.filterwarnings('ignore')

print("=" * 60)
print("Computing I(T;Y) and η_IB for cosmic scale")
print("=" * 60)

# Load maps
print("\n[1] Loading density map (T)...")
density = hp.read_map('density_map.fits')
print(f"  density_map shape: {density.shape}")

print("\n[2] Loading cluster map (Y)...")
cluster = hp.read_map('cluster_map.fits')
print(f"  cluster_map shape: {cluster.shape}")

# Use only pixels with valid data (density > 0)
valid = (density > 0) & (np.isfinite(cluster))
T_valid = density[valid]
Y_valid = cluster[valid]

print(f"  Valid pixels: {np.sum(valid)} / {len(density)}")

# Mutual Information estimation
print("\n[3] Computing I(T;Y)...")
# Reshape for sklearn
T_2d = T_valid.reshape(-1, 1)
mi = mutual_info_regression(T_2d, Y_valid, random_state=42)[0]
print(f"  I(T;Y) = {mi:.6f} nats")

# Load I(X;T)
print("\n[4] Loading I(X;T) from fisher_results.npz...")
fisher = np.load('fisher_results.npz')
I_XT = fisher['MI']
print(f"  I(X;T) = {I_XT:.6f} nats")

# Compute η_IB
print("\n[5] Computing η_IB = I(T;Y) / I(X;T)...")
eta_IB = mi / I_XT
print(f"  η_IB = {eta_IB:.6f}")

# Save results
print("\n[6] Saving results...")
np.savez('eta_IB_cosmic.npz',
         I_TY=mi,
         I_XT=I_XT,
         eta_IB=eta_IB,
         n_valid=np.sum(valid))

with open('eta_IB_cosmic.txt', 'w') as f:
    f.write("Cosmic scale η_IB results\n")
    f.write("=========================\n")
    f.write(f"I(T;Y) = {mi:.6f} nats\n")
    f.write(f"I(X;T) = {I_XT:.6f} nats\n")
    f.write(f"η_IB   = {eta_IB:.6f}\n")
    f.write(f"Valid pixels: {np.sum(valid)}\n")

print("  Saved: eta_IB_cosmic.npz, eta_IB_cosmic.txt")

# Scatter plot
print("\n[7] Creating scatter plot...")
fig, ax = plt.subplots(figsize=(6, 5))
# Sample for plotting (too many points)
idx = np.random.choice(len(T_valid), min(50000, len(T_valid)), replace=False)
ax.scatter(np.log10(T_valid[idx] + 0.1), np.log10(Y_valid[idx] + 0.1), s=1, alpha=0.5)
ax.set_xlabel('log10(galaxy density + 0.1)')
ax.set_ylabel('log10(cluster count + 0.1)')
ax.set_title(f'Galaxy density vs cluster abundance\nI(T;Y) = {mi:.3f} nats, η_IB = {eta_IB:.3f}')
plt.tight_layout()
plt.savefig('eta_IB_cosmic_scatter.png', dpi=150)
print("  Saved: eta_IB_cosmic_scatter.png")

print("\n" + "=" * 60)
print("Summary:")
print(f"  I(X;T) = {I_XT:.4f} nats")
print(f"  I(T;Y) = {mi:.4f} nats")
print(f"  η_IB   = {eta_IB:.4f}")
print("=" * 60)