#!/usr/bin/env python3
import json
import os
import sys
from pathlib import Path

# Retrieve the environment name from the command-line arguments
env_name = sys.argv[1]

# Get the Conda directory from the environment variables
CONDA_DIR = os.environ["CONDA_DIR"]

# Define the path to the kernel.json file
kernel_dir = Path.home() / f".local/share/jupyter/kernels/{env_name}"
kernel_file = kernel_dir / "kernel.json"

# Ensure the kernel directory exists
kernel_dir.mkdir(parents=True, exist_ok=True)

# Define default kernel.json content
default_content = {
    "argv": [
        f"{CONDA_DIR}/envs/{env_name}/bin/python",
        "-m",
        "ipykernel_launcher",
        "-f",
        "{connection_file}",
    ],
    "display_name": f"Python ({env_name})",
    "language": "python",
}

# If the kernel.json file doesn't exist, create it with default content
if not kernel_file.exists():
    kernel_file.write_text(json.dumps(default_content, indent=1))

# Read the existing kernel.json content
content = json.loads(kernel_file.read_text())

# Add the environment variables to the kernel configuration
content["env"] = {
    "XML_CATALOG_FILES": "",
    "PATH": f"{CONDA_DIR}/envs/{env_name}/bin:$PATH",
    "CONDA_PREFIX": f"{CONDA_DIR}/envs/{env_name}",
    "CONDA_PROMPT_MODIFIER": f"({env_name}) ",
    "CONDA_SHLVL": "2",
    "CONDA_DEFAULT_ENV": env_name,
    "CONDA_PREFIX_1": CONDA_DIR,
}

# Write the updated content back to the kernel.json file
kernel_file.write_text(json.dumps(content, indent=1))
