# Dask Setup on the supercomputer

## Prerequisites

1. CustomSLURMCluster requires the pyproject.toml file to be present in the project directory. This file will be used to install the required packages in the Dask workers.

## Visual Studio Code on supercomputer

Using `setup_vscode.sh` script, you can launch a VSCode on the computing node of the supercomputer.

```bash
$ sbatch setup_vscode.sh <project-directory-path>
```

## Sample notebooks

In this repository, you will find sample notebooks to demonstrate the setup and usage of Dask on the supercomputer.

1. To start a Dask cluster on the supercomputer, use the `01-launch-dask-cluster.ipynb` notebook. You will be guided through this process by this notebook.

2. A sample Dask job can be submitted using the `02-dask-demo.ipynb` notebook.
