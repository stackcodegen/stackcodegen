# StackCodeGen Reproducibility Package

This repository provides the necessary pipeline to run and validate the motivating example. It includes a setup script for environment management and dependencies, as well as integration support for Docker and Ollama.

## Setup Instructions

### 1. Run the Installation Script

Ensure the `install.sh` script is executable. If not, set the permissions:

```bash
chmod +x install.sh
```

Then run the script to create a virtual environment and install dependencies:

```bash
./install.sh
```

This will create a ```.venv``` directory using ```Python 3.12.8``` (via pyenv) and install all required packages from ```requirements.txt```.

### 2. Activate the Virtual Environment

After installation, activate the environment:

```bash
source .venv/bin/activate
```

### 3. Update the ```.env``` file

Update the ```.env``` file to use your OpenAI API key and Anthropic API key.

### 4. Run the Motivating Example

To run the motivating example:

```bash
python main.py
```

### 4. Check Output and Logs

All generated output and logs will be available in the ```output/``` directory. Review this directory to inspect model outputs, validation traces, and error logs.

## Validation Requirements

To validate the generated Python scripts in isolated environments, ```Docker``` is required. Ensure the ```Docker``` daemon is running before validation.

- Install Docker: <https://docs.docker.com/get-docker/>
- Check if Docker is running:

    ```bash
    docker info
    ```

    If Docker is not running, launch Docker Desktop or start the daemon manually.

## Optional: Using Ollama

If you wish to run local models using Ollama:

1. Install Ollama: <https://ollama.com/download>
2. Start the Ollama daemon:

   ```bash
   ollama serve
   ```

3. Ensure ```OLLAMA_API_BASE``` is set (default is fine):

    ```bash
    export OLLAMA_API_BASE=http://localhost:11434
    ```

   Make sure your model is pulled and running through Ollama. The pipeline will use this endpoint to interact with local models.

## Notes

- Ensure ```Python 3.12.8``` is installed via ```pyenv```.
- This project assumes a Unix-like environment (macOS or Linux).
