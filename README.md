# python-tutorial

[![Binder](https://mybinder.org/badge_logo.svg)](https://mybinder.org/v2/gh/empa-scientific-it/python-tutorial.git/main?labpath=index.ipynb)


## Run the tutorial on your computer

You have two ways in which you can run the tutorial **locally**.

### 1. With a `conda` environment

To run the tutorial locally, setup the environment with [conda](https://docs.conda.io/en/latest/miniconda.html) (or [mamba](https://mamba.readthedocs.io/en/latest/installation.html)):

```console
conda env create -f environment.yml
```

Then activate the environment with
```console
conda activate python-tutorial
```

Finally, launch JupyterLab with
```console
jupyter lab
```

To update the existing environment, run
```console
conda env update -f environment.yml
```

### 2. With Docker

1. Install Docker Desktop: First, you need to install Docker Desktop on your Windows machine. You can download it from the official Docker website: https://www.docker.com/products/docker-desktop.

2. Create a folder: Open File Explorer and create a new folder where you want to save the tutorial's materials. For example, you could create a folder called "python-tutorial" on your Desktop.

3. Open PowerShell: Once Docker Desktop is installed, open PowerShell on your Windows machine. You can do this by pressing the "Windows" key and typing "PowerShell" in the search bar.

4. Pull the Docker image: In PowerShell, run the following command to pull the "empascientificit/python-tutorial" Docker image:

```console
docker pull empascientificit/python-tutorial
```

5. Run the Docker container: Once the image is downloaded, run the following command to start a Docker container from the image:

```console
docker run -p 8888:8888 -v /path/to/python-tutorial:/home/jovyan/work empascientificit/python-tutorial
```

Replace `/path/to/python-tutorial` with the path to the folder you created in step 2, for example `C:/Users/yourusername/Desktop/python-tutorial`.

> **Note**
>
> The above command will **mirror** the content of your local folder (e.g., `C:/Users/yourusername/Desktop/python-tutorial`) to the `work/` folder **inside the container**. In this way, every file or folder you copy or create into `work/` will be saved on your machine, and will remain there **even if you stop Docker**.

6. Access the Jupyter Notebook: Open a web browser and navigate to `http://localhost:8888/lab`. You should see the Jupyter Notebook interface. Enter the token provided in the PowerShell console to access the notebook. Alternatively, you can directly click on the link that appears in the PowerShell after the container has started.

You can now use the Jupyter in the Docker container to run the python-tutorial. When you're done, you can stop the container by pressing `Ctrl+C` in the PowerShell console. If you want to start the container again, just run the "docker run" command again.
