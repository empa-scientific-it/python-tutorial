# Use the jupyter/minimal-notebook as the base image
FROM quay.io/jupyter/minimal-notebook:latest

# Set environment variables for the tutorial and repository
ENV BASENAME="python-tutorial"
ENV REPO=${HOME}/${BASENAME}
ENV IPYTHONDIR="${HOME}/.ipython"

# Switch to root user to install additional dependencies
USER root
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    build-essential \
    gcc \
    g++ \
    libffi-dev && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Switch back to the default notebook user
USER ${NB_UID}

# Set up the Conda environment
COPY docker/environment.yml /tmp/environment.yml
RUN mamba env update -n base -f /tmp/environment.yml && \
    mamba clean --all -f -y && \
    fix-permissions "${CONDA_DIR}" && \
    fix-permissions "/home/${NB_USER}"

# Prepare IPython configuration (move earlier in the build)
RUN mkdir -p ${HOME}/.ipython/profile_default
COPY --chown=${NB_UID}:${NB_GID} binder/ipython_config.py ${HOME}/.ipython/profile_default/

# Copy the repository late in the build process
RUN mkdir -p ${REPO}
COPY --chown=${NB_UID}:${NB_GID} . ${REPO}/

# Set the working directory to the repository
WORKDIR ${REPO}

# Use the default ENTRYPOINT from the base image to start Jupyter Lab
ENTRYPOINT ["tini", "-g", "--", "start.sh"]
