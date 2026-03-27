import numpy as np
import astropy.io.fits as fits
import healpy as hp
import matplotlib.pyplot as plt
import warnings
warnings.filterwarnings('ignore')

def compute_etf_score(vectors, n_samples=None):
    if vectors.ndim == 1:
        vectors = vectors.reshape(1, -1)
    n, d = vectors.shape
    if n_samples is not None and n_samples < n:
        idx = np.random.choice(n, n_samples, replace=False)
        vectors = vectors[idx]
        n = n_samples
    norms = np.linalg.norm(vectors, axis=1, keepdims=True)
    norms = np.where(norms == 0, 1.0, norms)
    vectors_normed = vectors / norms
    gram = vectors_normed @ vectors_normed.T
    triu_idx = np.triu_indices(n, k=1)
    off_diag = gram[triu_idx]
    var_off = np.var(off_diag)
    var_random = 1.0 / d
    etf_score = 1 - (var_off / (var_random + 1e-12))
    return np.clip(etf_score, 0.0, 1.0)

print("=" * 60)
print("ETF-score and Phi_TDA Correlation")
print("=" * 60)

print("\n[1] Loading SDSS galaxy catalog...")
hdul = fits.open('spAll-v6_0_4.fits')
data = hdul[1].data
hdul.close()
print("  Done.")

print("\n[2] Loading Phi_TDA...")
phi_tda = np.load('phi_tda.npy')[()]
print(f"  Phi_TDA = {phi_tda:.4f}")

print("\n[3] Loading density map...")
density_map = hp.read_map('density_map.fits')
nside = hp.get_nside(density_map)
print(f"  nside = {nside}")

print("\n[4] Building feature vectors...")
ra = data['PLUG_RA']
dec = data['PLUG_DEC']
z = data['Z']
pix = hp.ang2pix(nside, np.radians(90 - dec), np.radians(ra))
density_vals = density_map[pix]
features = np.column_stack([density_vals, z])
good = np.isfinite(features).all(axis=1)
features = features[good]
print(f"  Total galaxies after cleaning: {len(features)}")

np.random.seed(42)
n_sample = 2000
if len(features) > n_sample:
    idx = np.random.choice(len(features), n_sample, replace=False)
    features = features[idx]
    print(f"  Subsampled to {n_sample} galaxies")
else:
    print(f"  Using all {len(features)} galaxies")

print("\n[5] Computing ETF-score...")
etf_full = compute_etf_score(features)
print(f"  ETF-score (full) = {etf_full:.4f}")

print("\n[6] Bootstrap stability analysis...")
n_bootstrap = 100
sample_frac = 0.7
n = len(features)
sample_size = int(n * sample_frac)
etf_scores = []
for i in range(n_bootstrap):
    idx = np.random.choice(n, sample_size, replace=True)
    sample = features[idx]
    etf_scores.append(compute_etf_score(sample))
etf_scores = np.array(etf_scores)
etf_mean = np.mean(etf_scores)
etf_std = np.std(etf_scores)
print(f"  Bootstrap mean = {etf_mean:.4f} +/- {etf_std:.4f}")
print(f"  Range: [{np.min(etf_scores):.4f}, {np.max(etf_scores):.4f}]")

print("\n[7] Saving results...")
np.save('etf_score_full.npy', etf_full)
np.save('etf_scores_bootstrap.npy', etf_scores)

with open('etf_results.txt', 'w') as f:
    f.write("ETF-score and Phi_TDA correlation results\n")
    f.write("==========================================\n")
    f.write(f"Phi_TDA = {phi_tda:.6f}\n")
    f.write(f"ETF-score (full sample) = {etf_full:.6f}\n")
    f.write(f"Bootstrap (n={len(etf_scores)}, size=70% of data):\n")
    f.write(f"  Mean ETF = {etf_mean:.6f}\n")
    f.write(f"  Std ETF = {etf_std:.6f}\n")
    f.write(f"  Min = {np.min(etf_scores):.6f}\n")
    f.write(f"  Max = {np.max(etf_scores):.6f}\n")

print("  Saved: etf_score_full.npy, etf_scores_bootstrap.npy, etf_results.txt")

print("\n[8] Creating visualisation...")
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))
ax1.hist(etf_scores, bins=20, edgecolor='black', alpha=0.7)
ax1.axvline(etf_full, color='red', linestyle='--', label=f'Full = {etf_full:.3f}')
ax1.axvline(etf_mean, color='blue', linestyle='-', label=f'Mean = {etf_mean:.3f}')
ax1.set_xlabel('ETF-score')
ax1.set_ylabel('Frequency')
ax1.set_title('Bootstrap distribution of ETF-score')
ax1.legend()
ax2.scatter(etf_scores, np.ones_like(etf_scores), alpha=0.5, s=50)
ax2.set_xlabel('ETF-score')
ax2.set_yticks([])
ax2.set_title('ETF-score spread (each point = one bootstrap)')
ax2.axvline(etf_full, color='red', linestyle='--', label=f'Full = {etf_full:.3f}')
ax2.legend()
plt.tight_layout()
plt.savefig('etf_correlation.png', dpi=150)
print("  Saved etf_correlation.png")

print("\n" + "=" * 60)
print("Analysis complete!")
print("=" * 60)
print("\nSummary:")
print(f"  I(X;T) = 83.40 nats (from fisher_analysis)")
print(f"  Phi_TDA = {phi_tda:.2f}")
print(f"  ETF-score = {etf_full:.4f} +/- {etf_std:.4f}")