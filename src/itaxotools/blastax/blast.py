import os
import platform
import re
import shlex
import shutil
import subprocess
import sys
from hashlib import sha256
from pathlib import Path

from platformdirs import user_config_dir, user_data_dir

from .download import REQUIRED_BLAST_BINARIES


def get_user_config_path() -> Path:
    # Different config per user & virtual environment
    dir = user_config_dir(appname="BlasTax", appauthor="iTaxoTools")
    filename = sha256(sys.prefix.encode()).hexdigest()[:8] + ".txt"
    return Path(dir) / filename


def dump_user_blast_path(path: Path):
    config_path = get_user_config_path()
    if not config_path.exists():
        config_path.parent.mkdir(parents=True, exist_ok=True)
    with open(config_path, "w") as file:
        print(str(path), file=file)


def load_user_blast_path() -> Path | None:
    config_path = get_user_config_path()
    if not config_path.exists():
        return None
    with open(config_path) as file:
        return Path(file.readline().strip())


def suggest_user_blast_path() -> Path:
    return Path(user_data_dir(appname="BlasTax", appauthor="iTaxoTools")) / "bin"


def get_blast_env() -> dict:
    env = os.environ.copy()
    blast_path = load_user_blast_path()
    if blast_path is not None:
        env["PATH"] += f"{os.pathsep}{blast_path}"
    return env


def check_binaries_in_path() -> bool:
    blast_env = get_blast_env()
    path = blast_env["PATH"]
    for binary in REQUIRED_BLAST_BINARIES:
        if not shutil.which(binary, path=path):
            return False
    return True


def get_blast_binary(name: str) -> str | None:
    if platform.system() == "Windows":
        name += ".exe"

    blast_path = load_user_blast_path()
    if blast_path is not None:
        bin_path = blast_path / name
        if bin_path.exists():
            return str(bin_path)

    blast_env = get_blast_env()
    path = blast_env["PATH"]
    return shutil.which(name, path=path)


def remove_single_quotes(text: str) -> str:
    if len(text) > 1 and text[0] == text[-1] == "'":
        return text[1:-1]
    return text


def command_to_args(command: str) -> list[str]:
    if platform.system() == "Windows":
        args = shlex.split(command, posix=False)
        args = [remove_single_quotes(arg) for arg in args]
        return args
    return shlex.split(command)


def get_blast_version() -> str | None:
    try:
        binary = get_blast_binary("makeblastdb")
        if binary is None:
            return None
        args = [binary, "-version"]
        kwargs = {}
        blast_env = get_blast_env()
        if platform.system() == "Windows":
            kwargs = dict(creationflags=subprocess.CREATE_NO_WINDOW)
        result = subprocess.run(
            args,
            capture_output=True,
            text=True,
            check=True,
            env=blast_env,
            **kwargs,
        )
        output = result.stdout
    except subprocess.CalledProcessError as e:
        print(f"Error occurred while fetching version: {e}")
    except FileNotFoundError:
        raise Exception("Could not find blast executables.")

    version_match = re.search(r"blast (\d+\.\d+\.\d+)", output)

    if version_match:
        return version_match.group(1)
    else:
        raise Exception("Version number not found in output!")


def execute_blast_command(args: list[str], debug=False):
    if debug:
        print("Executing BLAST+ with args: ", args)
    kwargs = {}
    blast_env = get_blast_env()
    if platform.system() == "Windows":
        kwargs = dict(creationflags=subprocess.CREATE_NO_WINDOW)
    p = subprocess.Popen(
        args,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        env=blast_env,
        **kwargs,
    )
    p.wait()
    stdout, stderr = p.communicate()
    if p.returncode != 0:
        binary = Path(args[0]).stem
        lines = stderr.decode("utf-8").strip().splitlines()
        error = lines[-1] if lines else "silently"
        raise Exception(f"{binary} failed: {error}")
    return stdout
