# SDSS Cosmic Web & Topological Information Pipeline 🌌

![Python](https://img.shields.io/badge/Python-3.8%2B-blue)
![Data](https://img.shields.io/badge/Data-SDSS%20DR18-orange)
![License](https://img.shields.io/badge/License-MIT-green)

A comprehensive Python pipeline for the analysis of the Cosmic Web using data from the Sloan Digital Sky Survey (SDSS). This project integrates cosmological mapping, Topological Data Analysis (TDA), and Information Theory (Information Bottleneck) to classify and analyze large-scale structures in the universe.

## 🚀 Key Features

* **Automated Data Retrieval:** Fetches and processes SDSS RedMaPPer cluster catalogs (DR18).
* **HEALPix Mapping:** Generates high-resolution and degraded density and cluster maps.
* **Cosmic Web Classification:** Classifies the large-scale structure into physical components: Voids, Sheets, Filaments, and Knots.
* **Topological Data Analysis (TDA):** Utilizes Ripser to compute persistent homology and extract topological features (persistence diagrams, Betti numbers).
* **Information Theory Metrics:** Calculates the Information Bottleneck efficiency (eta_IB) across different cosmic structures.
* **Statistical Analysis:** Includes Fisher matrix analysis and ETF (Empirical Transfer Function) scoring for robust statistical validation.

## 📁 Repository Structure

The project is organized into modular directories based on functionality:

* 📂 **`data_processing_and_maps/`**
    * Scripts for downloading SDSS data (`download_redmapper_dr18.py`).
    * HEALPix map generation and degradation (`build_density_map.py`, `degrade_maps.py`).
    * Cosmic Web classification logic (`classify_cosmic_web.py`).
    * `.fits` files containing spatial density data.
* 📂 **`tda_and_topology/`**
    * TDA computations and persistent homology (`tda_ripser.py`, `tda_simple.py`, `tda_phi.py`).
* 📂 **`information_theory_analysis/`**
    * Information Bottleneck calculations (`compute_eta_IB_cosmic.py`, `compute_eta_lowres.py`).
    * Fisher matrix forecasting (`fisher_analysis.py`).
* 📂 **`statistical_metrics/`**
    * Correlation and ETF scoring (`etf_correlation.py`).
* 📂 **`visualizations_and_plots/`**
    * Generated outputs: Density maps, cluster distributions, power spectra, and TDA persistence diagrams.
* 📄 **`run_all.bat` / `run_sdss_pipeline.bat`**
    * Batch scripts for automated, end-to-end execution of the pipeline.

## 🛠️ Prerequisites & Installation

Ensure you have Python 3.8+ installed. You will need the following key scientific libraries:

```bash
pip install numpy scipy matplotlib astropy healpy ripser scikit-learn
````

## 🖥️ Usage

To run the full pipeline automatically, simply execute the batch script from the root directory:

**On Windows:**

```cmd
run_all.bat
```

*(Alternatively, use `run_sdss_pipeline.bat` for specific SDSS routines).*

### Manual Execution Pipeline:

If you prefer to run the stages manually, follow this logical order:

1.  **Fetch Data:** Run `download_redmapper_dr18.py`.
2.  **Build Maps:** Execute `build_density_map.py` to create the initial HEALPix `.fits` maps.
3.  **Classify Structure:** Run `classify_cosmic_web.py` to segment the universe into Voids/Sheets/Filaments/Knots.
4.  **Topology Analysis:** Run `tda_ripser.py` and `tda_phi.py` on the generated arrays.
5.  **Information Metrics:** Compute eta\_IB using `compute_eta_IB_cosmic.py`.
6.  **Visualize:** Check the `visualizations_and_plots/` folder for newly generated `.png` graphs.

## 📊 Visual Outputs

The pipeline automatically generates several high-quality plots for analysis:

  * **`density_map.png` & `cluster_map.png`:** Visual representations of mass and cluster distributions.
  * **`persistence_diagram.png`:** TDA output showing the birth and death of topological features.
  * **`eta_IB_cosmic_scatter_lowres.png`:** Information Bottleneck efficiency mapped against cosmic web structures.

## 🧑‍💻 Author

**LiranOG** [GitHub Profile](https://www.google.com/search?q=https://github.com/LiranOG)

