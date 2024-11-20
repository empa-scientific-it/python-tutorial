# Use the jupyter/minimal-notebook as the base image
FROM quay.io/jupyter/minimal-notebook:latest

# Set a shortcut to the tutorial name
ENV BASENAME="python-tutorial"
ENV REPO="https://github.com/edoardob90/${BASENAME}"

# Set the working directory to the home directory of the notebook user
WORKDIR ${HOME}

# Clone the tutorial repository
RUN git clone \
    --branch main \
    --depth 1 \
    ${REPO}

# Set the working directory to the repository directory
WORKDIR ${BASENAME}

# Switch to root user to install additional dependencies (if needed)
USER root

# Install additional dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    build-essential \
    gcc \
    g++ \
    libffi-dev \
    && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Switch back to the default notebook user
USER ${NB_UID}

# Create the Conda environment defined in environment.yml
# COPY --chown=${NB_USER}:${NB_GID} docker/environment.yml docker/environment.yml
RUN mamba env update -n base -f docker/environment.yml && \
    mamba clean --all -f -y && \
    fix-permissions "${CONDA_DIR}" && \
    fix-permissions "/home/${NB_USER}"

# Copy the IPython configuration file (binder/postBuild script)
RUN mkdir -p ${HOME}/.ipython/profile_default && \
    cp -a binder/ipython_config.py ${HOME}/.ipython/profile_default/

# Set the environment variable IPYTHONDIR
ENV IPYTHONDIR="${HOME}/.ipython"

# Use the default ENTRYPOINT from the base image to start Jupyter Lab
ENTRYPOINT ["tini", "-g", "--", "start.sh"]
