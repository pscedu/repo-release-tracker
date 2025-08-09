Bootstrap: docker
From: continuumio/miniconda3

%files
    TSVreader.py /opt/TSVreader.py

%post
    # Ensure conda commands are available
    . /opt/conda/etc/profile.d/conda.sh

    # Create the conda environment 'psc'
    conda create -y -n psc python=3.11

    # Activate and install required packages
    conda activate psc
    pip install --no-cache-dir rich-cli pandas tqdm pygithub

    # Make the script executable
    chmod +x /opt/singularity-report.py

    # Ensure 'psc' is activated automatically in container
    echo '. /opt/conda/etc/profile.d/conda.sh' >> /environment
    echo 'conda activate psc' >> /environment

%environment
    # Activate 'psc' env automatically for interactive shells
    . /opt/conda/etc/profile.d/conda.sh
    conda activate psc

%runscript
    # Activate env and run the script
    . /opt/conda/etc/profile.d/conda.sh
    conda activate psc
    exec python /opt/TSVreader.py "$@"
