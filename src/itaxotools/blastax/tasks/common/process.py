import shutil
from pathlib import Path
from random import choice
from string import ascii_letters

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
    db_paths: list[Path] = None,
    dry: bool = False,
) -> dict[Path, Path]:
    staged_paths: dict[Path, Path] = IdentityDict()
    input_dir = work_dir / "input"
    output_dir = work_dir / "output"
    input_dir.mkdir(exist_ok=True)
    output_dir.mkdir(exist_ok=True)
    for path in input_paths:
        if not _is_str_safe(str(path)):
            staged_path = input_dir / make_str_blast_safe(path.name)
            while staged_path in staged_paths.values():
                staged_path = staged_path.with_stem(staged_path.stem + choice(ascii_letters))
            staged_paths[path] = staged_path
            if not dry:
                shutil.copy(path, staged_paths[path])
    for path in output_paths:
        if not _is_str_safe(str(path)):
            if path.exists() and path.is_dir():
                staged_paths[path] = output_dir
            else:
                staged_path = output_dir / make_str_blast_safe(path.name)
                while staged_path in staged_paths.values():
                    staged_path = staged_path.with_stem(staged_path.stem + choice(ascii_letters))
                staged_paths[path] = staged_path
    if db_paths is not None:
        for db_path in db_paths:
            if not _is_str_safe(str(db_path)):
                staged_path = input_dir / make_str_blast_safe(db_path.name)
                while staged_path in staged_paths.values():
                    staged_path = staged_path.with_stem(staged_path.stem + choice(ascii_letters))
                staged_paths[db_path] = staged_path
                for path in _get_database_paths(db_path):
                    staged_paths[path] = Path(input_dir / staged_path.name).with_suffix(path.suffix)
                    if not dry:
                        shutil.copy(path, staged_paths[path])

    return staged_paths


def unstage_paths(work_dir: Path, staged_paths: dict[Path, Path], output_paths: list[Path] = None, clear: bool = True):
    input_dir = work_dir / "input"
    output_dir = work_dir / "output"
    if output_paths is not None:
        for output_path in output_paths:
            if staged_paths[output_path].is_file():
                shutil.copy(staged_paths[output_path], output_path)
            else:
                shutil.copytree(output_dir, output_path, dirs_exist_ok=True)
    if clear:
        shutil.rmtree(output_dir)
        shutil.rmtree(input_dir)
