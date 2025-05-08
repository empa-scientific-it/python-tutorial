# Stage 1: Build environment
FROM quay.io/jupyter/minimal-notebook:latest AS builder

# Define build argument for PyTorch variant (cpu or cuda)
ARG PYTORCH_VARIANT=cpu

# Switch to root user to install additional dependencies
USER root
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    build-essential \
    gcc \
    g++ \
    libffi-dev \
    libgl1 && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Switch back to the default notebook user
USER ${NB_UID}

# Set up the Conda environment
COPY docker/environment.yml /tmp/environment.yml
RUN mamba env update -n base -f /tmp/environment.yml && \
    # Force remove any existing PyTorch installations first
    pip uninstall -y torch torchvision && \
    # Install PyTorch packages without cache - conditionally based on variant
    if [ "$PYTORCH_VARIANT" = "cpu" ]; then \
    echo "Installing CPU-only PyTorch" && \
    pip install --no-cache-dir --force-reinstall torch torchvision --index-url https://download.pytorch.org/whl/cpu; \
    else \
    echo "Installing CUDA-enabled PyTorch" && \
    pip install --no-cache-dir --force-reinstall torch torchvision; \
    fi && \
    # Clean up all package caches to reduce image size
    mamba clean --all -f -y && \
    # Remove pip cache
    rm -rf ~/.cache/pip && \
    fix-permissions "${CONDA_DIR}" && \
    fix-permissions "/home/${NB_USER}"

# Stage 2: Runtime environment - creates a lighter final image
FROM quay.io/jupyter/minimal-notebook:latest

# Inherit build argument for image labeling
ARG PYTORCH_VARIANT=cpu

# Metadata labels
LABEL org.opencontainers.image.title="Python Tutorial"
LABEL org.opencontainers.image.description="A containerized Python tutorial environment with Jupyter Lab."
LABEL org.opencontainers.image.authors="Empa Scientific IT <scientificit@empa.ch>"
LABEL org.opencontainers.image.url="https://github.com/empa-scientific-it/python-tutorial"
LABEL org.opencontainers.image.source="https://github.com/empa-scientific-it/python-tutorial"
LABEL org.opencontainers.image.version="1.0.0"
LABEL org.opencontainers.image.licenses="MIT"
LABEL org.opencontainers.image.variant="pytorch-${PYTORCH_VARIANT}"

# Switch to root user to install minimal dependencies
USER root
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    libgl1 && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# System-wide Jupyter Server config
COPY docker/jupyter_server_config.py /etc/jupyter/

# Jupyter Lab settings
RUN mkdir -p /opt/conda/share/jupyter/lab/settings
COPY docker/overrides.json /opt/conda/share/jupyter/lab/settings/

# System-wide IPython profile config
RUN mkdir -p /etc/ipython/profile_default
COPY docker/ipython_config.py /etc/ipython/profile_default/

# Switch back to the default notebook user
USER ${NB_UID}

# Copy the conda environment from the builder stage
COPY --from=builder ${CONDA_DIR} ${CONDA_DIR}

# Copy home directory with configurations
COPY --from=builder --chown=${NB_UID}:${NB_GID} /home/${NB_USER} /home/${NB_USER}

# Set the working directory to user's home (repository will be cloned here by Renku)
WORKDIR /home/${NB_USER}

# Use the default ENTRYPOINT from the base image to start Jupyter Lab
ENTRYPOINT ["tini", "-g", "--", "start.sh"]
