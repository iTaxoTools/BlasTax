import shutil
from pathlib import Path

from itaxotools.blastax.utils import make_str_blast_safe


class IdentityDict(dict):
    def __missing__(self, key):
        return key


def _is_str_safe(text: str) -> bool:
    if not text.isascii():
        return False
    if " " in text:
        return False
    return True


def stage_paths(input_paths: list[Path], output_path: Path, work_dir: Path) -> dict[Path, Path]:
    staged_paths: dict[Path, Path] = IdentityDict()
    input_dir = work_dir / "input"
    output_dir = work_dir / "output"
    input_dir.mkdir()
    output_dir.mkdir()
    for path in input_paths:
        if not _is_str_safe(str(path)):
            staged_paths[path] = input_dir / make_str_blast_safe(path.name)
            shutil.copy(path, staged_paths[path])
    if not _is_str_safe(str(output_path)):
        staged_paths[output_path] = output_dir

    return staged_paths


def unstage_paths(output_path: Path, work_dir: Path):
    input_dir = work_dir / "input"
    output_dir = work_dir / "output"
    shutil.copytree(output_dir, output_path, dirs_exist_ok=True)
    shutil.rmtree(output_dir)
    shutil.rmtree(input_dir)
