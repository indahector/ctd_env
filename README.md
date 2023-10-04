# ctd_env
Simple and light python environment to analyze miniCTD valeport

## Conda environment for climate science in Eagle Rock Analytics hist-obs-platform

This repository contains resources to facilitate installing a ctd-env conda environment from scratch on several machine environments (Linux and MacOS).  
It uses mamba to deal with the dependencies (only xarray, matplotlib, and pandas).

* `requirements.yml` - contains a list of packages needed, intended to be installed via `mamba env update -f requirements.yml`
* `install_local.sh` - a bash script that automatically creates an environment named `ctd-env` on the local machine. The anaconda base environment needs to be loaded for it to work.
