# Use the jupyter/minimal-notebook as the base image
FROM quay.io/jupyter/minimal-notebook:latest

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

# Copy the script to setup the environment
COPY docker/setup_custom_env.py /opt/setup-scripts/
# Make the script executable
RUN chmod +x /opt/setup-scripts/setup_custom_env.py

# Copy the script to activate the Conda environment
COPY docker/activate-custom-env.sh /usr/local/bin/before-notebook.d/

# Switch back to the default notebook user
USER ${NB_UID}

# Set a shortcut to the tutorial name
ENV BASENAME="python-tutorial"

# Set the working directory to the home directory of the notebook user
WORKDIR ${HOME}

# Clone the tutorial repository
RUN git clone \
    --branch main \
    --depth 1 \
    https://github.com/empa-scientific-it/${BASENAME}

WORKDIR ${HOME}/${BASENAME}

# Create the Conda environment defined in environment.yml
RUN mamba env create -f binder/environment.yml && \
    mamba clean --all -f -y && \
    fix-permissions "${CONDA_DIR}" && \
    fix-permissions "/home/${NB_USER}"

# Register the Jupyter kernel from the custom environment
RUN /opt/setup-scripts/setup_custom_env.py ${BASENAME}

# Copy the IPython configuration file
RUN mkdir -p ${HOME}/.ipython/profile_default
COPY binder/ipython_config.py ${HOME}/.ipython/profile_default/

# Set the environment variable IPYTHONDIR
ENV IPYTHONDIR="${HOME}/.ipython"

# Use the default ENTRYPOINT from the base image to start Jupyter Lab
ENTRYPOINT ["tini", "-g", "--", "start.sh"]
