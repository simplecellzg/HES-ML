# Enhanced sampling-deep learning framework resolves adsorption energetics in thermal protection materials

[![License](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![DOI](https://img.shields.io/badge/DOI-10.5281%2Fzenodo.18158696-blue)](https://doi.org/10.5281/zenodo.18158696)
[![Framework](https://img.shields.io/badge/Framework-HES--ML-green)](README.md)
[![Model](https://img.shields.io/badge/Model-HyGSI-orange)](DP_training/HyGSI/)

This repository contains the implementation of the **HES-ML (Hybrid Enhanced Sampling-Machine Learning)** framework and the resulting **HyGSI (Hypersonic Gas-Surface Interaction)** neural network potential.

**Paper:** *Enhanced sampling-deep learning framework resolves adsorption energetics in thermal protection materials*

## 📖 Overview

The HES-ML framework integrates **On-the-fly Probability Enhanced Sampling (OPES)** with **Deep Potential Molecular Dynamics (DeePMD)** to resolve the accuracy-efficiency dilemma in modeling atomic oxygen interactions with silica ($SiO_2$) thermal protection systems.

This repository is organized to reproduce the following key results:
1.  **HyGSI Model Training:** Training the Deep Potential using active learning datasets.
2.  **Validation:** Crystal parameters, RDFs, and melting points compared against DFT, ReaxFF, and BKS.
3.  **Surface Reconstruction:** Modeling the pressure-induced surface reconstruction of $\alpha$-quartz.
4.  **Adsorption Energetics:** Calculating Oxygen adsorption energies using GCMC and Relaxation MD (RMD).
5.  **Reaction Barriers:** Benchmarking reaction pathways against DFT and classical force fields.

## 📂 Repository Structure

The code is organized into five main directories corresponding to different stages of the research:

```text
.
├── DP_training/                  # Model training and Datasets
│   ├── HyGSI/                    # Final Model (graph.pb) and Merged Dataset (I & II)
│   └── HyGSI-X/                  # Iterative datasets from active learning
│
├── Crystal_parameters_a_b_c/     # Validation of Bulk Properties
│   ├── RDF_combine/              # Radial Distribution Functions comparison
│   ├── bond_analysis/            # Bond angle/length statistical analysis
│   ├── dft_PBE/                  # Ab initio MD reference data (CP2K)
│   ├── lmp_bks/                  # BKS force field benchmarks
│   ├── lmp_2015/                 # ReaxFF (2015) benchmarks
│   └── dp_.../                   # HyGSI model benchmarks
│
├── Surface_reconstruct/          # Surface Reconstruction Simulations
│   ├── deepmd/                   # HyGSI simulations with PLUMED
│   ├── reaxff/                   # ReaxFF comparison
│   └── bks/                      # BKS comparison
│
├── Adsorption/                   # Oxygen Adsorption (GCMC + RMD)
│   ├── deepmd/                   # HyGSI calculations
│   ├── reaxff/                   # ReaxFF calculations
│   └── Combined/                 # Scripts to combine and plot results
│
└── Reaction_energy_diff/         # Reaction Energetics Benchmarking
    ├── reaction1 & 2/            # Specific reaction pathways
    └── reaction_all/             # Summary analysis comparing DFT, DP, and FF
```

## ⚙️ Prerequisites

*   **DeePMD-kit** (v2.0+): For training and running the HyGSI potential.
*   **LAMMPS**: Patched with DeePMD-kit and PLUMED.
*   **PLUMED** (v2.7+): For enhanced sampling (OPES) and collective variable analysis.
*   **CP2K** (v8.1+): For generating DFT reference data (if reproducing AIMD).
*   **Python 3.8+**: Required libraries: `numpy`, `matplotlib`, `h5py`, `dpdata`.

## 🚀 Usage Guide

### 1. Training the HyGSI Model
The training data and the frozen model graph are located in `DP_training/HyGSI`.
*   **Dataset:** `Dataset_I_and_II.hdf5` (Hosted on Zenodo, see Data Availability).
*   **Model:** `graph_compressed_20241109_clean_2.pb`

To run MD simulations using LAMMPS, ensure the `.pb` file is in your working directory and use the `pair_style deepmd` command.

### 2. Validation (Crystal Properties)
Navigate to `Crystal_parameters_a_b_c/`. This directory compares HyGSI against PBE, ReaxFF, and BKS across temperatures (100K-2000K).
*   Run `rdf_combine_plot.py` to generate RDF comparison plots.
*   Run `comprehensive_analysis_report_summary.py` to aggregate lattice parameters and bond statistics.

### 3. Surface Reconstruction
Located in `Surface_reconstruct/`. We use PLUMED to drive the reconstruction.
*   **Example:** Go to `deepmd/` and run the LAMMPS input script `input.lammps` which calls `plumed_SiO_surf_reconstruct.dat`.
*   **Analysis:** Use `combine_plt.py` to visualize the reconstruction free energy surface.

### 4. Adsorption Energetics (GCMC + RMD)
Located in `Adsorption/`. This section implements the two-stage GCMC + Relaxation MD protocol.
*   **Workflow:**
    1.  Go to `Adsorption/deepmd/Adsorption_O_SiO2_RMD_Relax_DP_bk/`.
    2.  Use scripts like `submit_gpu_lmp25_beta_long_box_abs_gcmc.sh` to submit jobs.
    3.  Post-processing: Use `gcmc_rmd_plot_combine.py` in the `Combined/` folder to generate energy distribution plots.

### 5. Reaction Energy Difference
Located in `Reaction_energy_diff/`. This compares the energy barriers of specific surface reactions.
*   The folder `reaction_all/collected_energies` contains CSV summaries.
*   Run `combine_all_energy.py` to produce the comparative parity plots between HyGSI and DFT.

## 📊 Data Availability

Due to file size limits, the large training datasets and trajectory files are hosted on Zenodo.

> **Zenodo Repository:** [https://doi.org/10.5281/zenodo.18158696](https://doi.org/10.5281/zenodo.18158696)

Please download the following files from Zenodo if they are not present in the cloned repository:
*   `Dataset_I_and_II.hdf5` (Full training dataset)
*   `graph_compressed_20241109_clean_2.pb` (Pre-trained HyGSI model)

## 📝 Citation

If you use this code, model, or dataset in your research, please cite:

```bibtex
@article{Zhang2024_HyGSI,
  title={Enhanced sampling-deep learning framework resolves adsorption energetics in thermal protection materials},
  author={Zhang, Guan and Ye, Xinbin and Hu, Shiwei and Zhang, Yonghao and Xiao, Tianbai and Sun, Quanhua and Hu, Yuan},
  journal={Nature Communications (Submitted)},
  year={2026}
}

@dataset{Zhang2024_HyGSI_Dataset,
  author={Zhang, Guan},
  title={HES-ML: Training Datasets and Deep Potentials for Silica Gas-Surface Interactions},
  year={2026},
  publisher={Zenodo},
  doi={10.5281/zenodo.18158696},
  url={https://doi.org/10.5281/zenodo.18158696}
}
```

## 📧 Contact

*   **Yuan Hu**: [yhu@imech.ac.cn](mailto:yhu@imech.ac.cn)
*   **Guan Zhang**: [zhangguan@imech.ac.cn](mailto:zhangguan@imech.ac.cn)