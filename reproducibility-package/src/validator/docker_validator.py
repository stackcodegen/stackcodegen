import subprocess
import tempfile
from pathlib import Path
import uuid


class DockerValidator:
    def __init__(self, docker_template_path: Path, python_version: str = "3.8", pandas_version: str = "1.1.5"):
        self.docker_template_path = docker_template_path
        self.python_version = python_version
        self.tag = f"py{self.python_version.replace('.', '_')}_{uuid.uuid4().hex[:6]}"

    def _prepare_dockerfile(self) -> str:
        template = self.docker_template_path.read_text()
        return template.replace("__PY_VERSION__", self.python_version)

    def validate(self, script: str, requirements: str) -> dict:
        with tempfile.TemporaryDirectory() as tmpdir:
            tmp_path = Path(tmpdir)

            # Write files
            (tmp_path / "script.py").write_text(script)
            (tmp_path / "requirements.txt").write_text(requirements)
            (tmp_path / "Dockerfile").write_text(self._prepare_dockerfile())

            # Build Docker image
            print(f"[INFO] Building Docker image with tag: {self.tag}...")
            try:
                subprocess.run(
                    ["docker", "build", "--no-cache", "--progress=plain", "-t", self.tag, str(tmp_path)],
                    check=True,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True,
                    timeout=600
                )
            except subprocess.CalledProcessError as e:
                error_msg = f"[DOCKER BUILD FAILED]\nSTDOUT:\n{e.stdout}\nSTDERR:\n{e.stderr}"
                print(error_msg)
                raise RuntimeError(error_msg) from e

            result = self._run_script("script.py")
            return {
                "stdout": result.stdout,
                "stderr": result.stderr,
                "returncode": result.returncode
            }

    def _run_script(self, script_name: str) -> subprocess.CompletedProcess:
        print(f"[INFO] Running script: {script_name} in Docker...")
        try:
            result = subprocess.run(
                ["docker", "run", "--rm", self.tag, "python", script_name],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                timeout=30,
            )

            return result

        except subprocess.TimeoutExpired as e:
            error_msg = f"[TIMEOUT] Script '{script_name}' exceeded {e.timeout} seconds."
            print(error_msg)
            return subprocess.CompletedProcess(
                args=e.cmd,
                returncode=-1,
                stdout="",
                stderr=error_msg
            )
