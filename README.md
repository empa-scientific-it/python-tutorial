# python-tutorial

[![Renku](https://renkulab.io/renku-badge.svg)](https://renkulab.io/v2/projects/empa-scientific-it/empa-it-python-tutorial/sessions/01JRT57GABCS15JB5NGNTQVTRB/start)
[![Binder](https://mybinder.org/badge_logo.svg)](https://mybinder.org/v2/gh/empa-scientific-it/python-tutorial.git/main?labpath=00_index.ipynb)

[![Build Docker container](https://github.com/empa-scientific-it/python-tutorial/actions/workflows/docker-build.yml/badge.svg)](https://github.com/empa-scientific-it/python-tutorial/actions/workflows/docker-build.yml)

[![Open in GitHub Codespaces](https://github.com/codespaces/badge.svg)](https://github.com/codespaces/new?hide_repo_select=true&ref=main&repo=593234387)

## Run the tutorial on your computer

You have two ways in which you can run the tutorial **locally**.

### 1. With a `conda` environment

#### 0. Prerequisites

To run the tutorial locally, you should first install [conda](https://docs.conda.io/en/latest/miniconda.html) (or [mamba](https://mamba.readthedocs.io/en/latest/installation/mamba-installation.html)).

It is also suggested that you have a recent version of `git`. Check out [how to install `git`](https://git-scm.com/book/en/v2/Getting-Started-Installing-Git) on your operating system.

#### 1. Download the material

Go to the directory on your machine where you want to download the material and clone the repository:

```console
git clone https://github.com/empa-scientific-it/python-tutorial
```

Alternatively, you can manually download a ZIP archive with the latest version of the material:

[Download ZIP archive](https://github.com/empa-scientific-it/python-tutorial/archive/refs/heads/main.zip)

Extract the archive in a directory of your choice.

#### 2. Create a dedicated environment

Enter the tutorial folder with

```console
cd /path/to/python-tutorial

```

> If you have installed Anaconda, then you can use Anaconda Prompt to run the following commands.

You should now create a new environment with `conda`:

```console
conda env create -f binder/environment.yml
```

> [!WARNING]
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

#### 3. Launch the tutorial via Jupyter

Finally, launch JupyterLab with

```console
jupyter lab
```

### 2. With Docker

> [!NOTE]
>
> The following instructions are for Windows. With minor changes, the steps work on macOS or Linux as well.

1. Install Docker Desktop: First, you need to install Docker Desktop on your Windows machine. You can download it from the official Docker website: https://www.docker.com/products/docker-desktop.

2. Create a folder: Open File Explorer and create a new folder where you want to save the tutorial's materials. For example, you could create a folder called "python-tutorial" on your Desktop.

3. Open PowerShell: Once Docker Desktop is installed, open PowerShell on your Windows machine. You can do this by pressing the "Windows" key and typing "PowerShell" in the search bar.

4. Pull the Docker image: In PowerShell, run the following command to pull the Docker image:

```console
docker pull ghcr.io/empa-scientific-it/python-tutorial:latest
```

> [!NOTE]
>
> The `latest` tag points to the CPU-only variant of the image, which is optimized for size and compatibility. If you have a CUDA-compatible GPU and want to use GPU acceleration for PyTorch operations, you can use the CUDA-enabled variant by replacing `latest` with `cuda`:
>
> ```console
> docker pull ghcr.io/empa-scientific-it/python-tutorial:cuda
> ```

> [!IMPORTANT]
>
> Using the CUDA variant requires a NVIDIA GPU with compatible drivers properly installed and configured for Docker. See [NVIDIA Container Toolkit](https://docs.nvidia.com/datacenter/cloud-native/container-toolkit/install-guide.html) for setup instructions.

5. Run the Docker container: Once the image is downloaded, run the following command to start a Docker container from the image:

```console
docker run -p 8888:8888 --name python_tutorial -v /path/to/python-tutorial:/home/jovyan/python-tutorial ghcr.io/empa-scientific-it/python-tutorial:latest jupyter lab --ip 0.0.0.0 --no-browser
```

> [!NOTE]
>
> If you pulled the CUDA variant, replace `:latest` with `:cuda` in the command above.

Replace `/path/to/python-tutorial` with the path to the folder you created in step 2, for example `C:/Users/yourusername/Desktop/python-tutorial`.

> [!NOTE]
>
> The above command will **mirror** the content of your local folder (e.g., `C:/Users/yourusername/Desktop/python-tutorial`) to the `~/python-tutorial` folder **inside the container**. In this way, every file or folder you copy or create into `~/python-tutorial` will be saved on your machine, and will remain there **even if you stop Docker**.

6. Access the Jupyter Notebook: Open a web browser and navigate to `http://localhost:8888/lab`. You should see the Jupyter Notebook interface. Enter the token provided in the PowerShell console to access the notebook. Alternatively, you can directly click on the link that appears in the PowerShell after the container has started.

You can now use the Jupyter in the Docker container to run the python-tutorial. When you're done, you can stop the container by pressing `Ctrl+C` in the PowerShell console.

> [!NOTE]
>
> If you want to restart the container, you can simply run the command `docker container start python_tutorial`.
