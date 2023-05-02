# python-tutorial

[![Binder](https://mybinder.org/badge_logo.svg)](https://mybinder.org/v2/gh/empa-scientific-it/python-tutorial.git/main?labpath=index.ipynb)


## Run the tutorial on your computer

### 0. Prerequisites

To run the tutorial locally, you should first install [conda](https://docs.conda.io/en/latest/miniconda.html) (or [mamba](https://mamba.readthedocs.io/en/latest/installation.html)).

It is also suggested that you have a recent version of `git`. Check out [how to install `git`](https://git-scm.com/book/en/v2/Getting-Started-Installing-Git) on your operating system.

### 1. Download the material

Go to the directory on your machine where you want to download the material and clone the repository:

```console
git clone https://github.com/empa-scientific-it/python-tutorial
```

Alternatively, you can manually download a ZIP archive with the latest version of the material:

[Download ZIP archive](https://github.com/empa-scientific-it/python-tutorial/archive/refs/heads/main.zip)

Extract the archive in a directory of your choice.

### 2. Create a dedicated environment

Enter the tutorial folder with

```console
cd /path/to/python-tutorial

```

You should now create a new environment with `conda`:

```console
conda env create -f binder/environment.yml
```

> **Warning**
>
> If you are on Windows and using Command Prompt or the PowerShell, please make sure to adjust the paths in the commands above accordingly.

Then activate the environment with
```console
conda activate python-tutorial
```

You can update the existing environment (that is, downloading the latest version of the packages) with:

```console
conda env update -f binder/environment.yml
```

### 3. Launch the tutorial via Jupyter

Finally, launch JupyterLab with
```console
jupyter lab
```
