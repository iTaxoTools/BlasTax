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


def _get_database_paths(db_path: Path) -> list[Path]:
    # Assume the suffix is missing
    if not any(
        (
            db_path.with_name(db_path.name + ".nin").exists(),
            db_path.with_name(db_path.name + ".pin").exists(),
        )
    ):
        return []
    return [path for path in db_path.parent.glob(f"{db_path.name}.*")]


def stage_paths(
    work_dir: Path,
    input_paths: list[Path],
    output_paths: list[Path],
    db_path: Path = None,
) -> dict[Path, Path]:
    staged_paths: dict[Path, Path] = IdentityDict()
    input_dir = work_dir / "input"
    output_dir = work_dir / "output"
    input_dir.mkdir()
    output_dir.mkdir()
    for path in input_paths:
        if not _is_str_safe(str(path)):
            staged_paths[path] = input_dir / make_str_blast_safe(path.name)
            shutil.copy(path, staged_paths[path])
    for path in output_paths:
        if not _is_str_safe(str(path)):
            if path.exists() and path.is_dir():
                staged_paths[path] = output_dir
            else:
                staged_paths[path] = output_dir / make_str_blast_safe(path.name)
    if db_path is not None:
        if not _is_str_safe(str(db_path)):
            staged_paths[db_path] = input_dir / make_str_blast_safe(db_path.name)
            for path in _get_database_paths(db_path):
                staged_paths[path] = input_dir / make_str_blast_safe(path.name)
                shutil.copy(path, staged_paths[path])

    return staged_paths


def unstage_paths(work_dir: Path, staged_paths: dict[Path, Path], output_path: Path):
    input_dir = work_dir / "input"
    output_dir = work_dir / "output"
    if staged_paths[output_path].is_file():
        shutil.copy(staged_paths[output_path], output_path)
    else:
        shutil.copytree(output_dir, output_path, dirs_exist_ok=True)
    shutil.rmtree(output_dir)
    shutil.rmtree(input_dir)
