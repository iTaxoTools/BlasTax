import os
import platform
import shutil
from pathlib import Path

from itaxotools.blastax.utils import make_str_blast_safe


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


class StagingArea:
    """Stage files with unsafe paths for BLAST+ subprocess calls.

    Builds a mapping from original paths to safe staged paths. Files are
    only copied when stage() is called, so the mapping can be inspected
    beforehand (e.g. to compute output names or check if staging is needed).

    Supports incremental use: call add() and stage() multiple times to
    stage additional paths without affecting previously staged ones.
    Call unstage_outputs() between iterations to copy results back without
    removing the staging directories (useful for batch processing where
    databases are staged once and reused across multiple queries).

    Use as a context manager for automatic cleanup::

        staging = StagingArea(work_dir)
        staging.add(input_paths=[query], output_paths=[result])
        staging.stage()
        with staging:
            run_blast(query=staging[query], output=staging[result])
    """

    # Symlinks require elevated privileges or Developer Mode on Windows,
    # which most regular users don't have. We fall back to copying there.
    _can_symlink = platform.system() != "Windows"

    def __init__(self, work_dir: Path):
        self._work_dir = work_dir
        self._input_dir = work_dir / "input"
        self._output_dir = work_dir / "output"
        self._map: dict[Path, Path] = {}
        self._taken: set[str] = set()
        self._pending_copies: list[tuple[Path, Path]] = []
        self._pending_output_dirs: bool = False
        self._output_originals: list[Path] = []

    def __getitem__(self, path: Path | None) -> Path | None:
        return self._map.get(path, path)

    def requires_copy(self) -> bool:
        """True if staging will copy files to disk.

        On Linux/macOS, inputs are symlinked (instant, no extra disk use)
        so no warning is needed. On Windows, files must be copied.
        """
        return bool(self._pending_copies) and not self._can_symlink

    def items(self):
        return self._map.items()

    def _safe_name(self, name: str) -> str:
        safe = make_str_blast_safe(name)
        if safe not in self._taken:
            self._taken.add(safe)
            return safe
        base = Path(safe)
        stem, suffix = base.stem, base.suffix
        for i in range(1, 10000):
            candidate = f"{stem}_{i}{suffix}"
            if candidate not in self._taken:
                self._taken.add(candidate)
                return candidate
        raise RuntimeError("Could not resolve staging name collision")

    def add(
        self,
        input_paths: list[Path] = (),
        output_paths: list[Path] = (),
        db_paths: list[Path] = (),
        taxdb_path: Path | None = None,
    ) -> None:
        for path in input_paths:
            if not path or _is_str_safe(str(path)):
                continue
            staged = self._input_dir / self._safe_name(path.name)
            self._map[path] = staged
            self._pending_copies.append((path, staged))

        for path in output_paths:
            if not path or _is_str_safe(str(path)):
                continue
            self._output_originals.append(path)
            self._pending_output_dirs = True
            if path.exists() and path.is_dir():
                self._map[path] = self._output_dir
            else:
                staged = self._output_dir / self._safe_name(path.name)
                self._map[path] = staged

        for db_path in db_paths:
            if not db_path or _is_str_safe(str(db_path)):
                continue
            staged_db = self._input_dir / self._safe_name(db_path.name)
            self._map[db_path] = staged_db
            for sidecar in _get_database_paths(db_path):
                staged_sidecar = (self._input_dir / staged_db.name).with_suffix(sidecar.suffix)
                self._map[sidecar] = staged_sidecar
                self._pending_copies.append((sidecar, staged_sidecar))

        if taxdb_path and not _is_str_safe(str(taxdb_path)):
            taxdb_dir = self._input_dir / "taxdb"
            self._map[taxdb_path] = taxdb_dir
            for name in ("taxdb.btd", "taxdb.bti"):
                src = taxdb_path / name
                if src.exists():
                    self._pending_copies.append((src, taxdb_dir / name))

    def stage(self, verbose: bool = False) -> None:
        """Stage pending files. Uses symlinks where available, copies otherwise."""
        if self._pending_copies:
            self._input_dir.mkdir(exist_ok=True)
            for src, dst in self._pending_copies:
                dst.parent.mkdir(exist_ok=True)
                if self._can_symlink:
                    os.symlink(src.resolve(), dst)
                    if verbose:
                        print(f"Symlinked {src} -> {dst}")
                else:
                    shutil.copy(src, dst)
                    if verbose:
                        print(f"Copied {src} -> {dst}")
            self._pending_copies.clear()
        if self._pending_output_dirs:
            self._output_dir.mkdir(exist_ok=True)
            self._pending_output_dirs = False

    def unstage_outputs(self) -> None:
        """Copy staged outputs back to their original locations.

        Clears the output tracking so that new outputs can be added
        and unstaged independently in subsequent iterations.
        """
        for path in self._output_originals:
            staged = self._map.get(path)
            if staged and staged != path:
                if staged.is_file():
                    shutil.copy(staged, path)
                elif staged == self._output_dir:
                    shutil.copytree(self._output_dir, path, dirs_exist_ok=True)
        self._output_originals.clear()

    def cleanup(self) -> None:
        """Remove staging directories."""
        if self._input_dir.exists():
            shutil.rmtree(self._input_dir)
        if self._output_dir.exists():
            shutil.rmtree(self._output_dir)

    def __enter__(self):
        return self

    def __exit__(self, *exc):
        self.unstage_outputs()
        self.cleanup()
