__all__ = (
    "__version__",
    "Registry",
)

__version__ = "0.0.2"


import json
import lzma
import shutil
from collections.abc import MutableMapping
from pathlib import Path
from typing import Any, Optional

DATA_DIR = Path(__file__).parent.resolve() / "data"
DATA_LABELS = {"create", "replace", "update", "delete", "disaggregate"}


class Registry(MutableMapping):
    def __init__(self, filepath: Optional[Path] = None):
        self.registry_fp = filepath or DATA_DIR / "registry.json"

    def __load(self) -> dict:
        try:
            return json.load(open(self.registry_fp))
        except IOError:
            # Create if not present
            self.__save({})
            return {}

    def __save(self, data: dict) -> None:
        with open(self.registry_fp, "w") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

    def __getitem__(self, key) -> Any:
        return self.__load()[key]

    def __setitem__(self, key, value) -> None:
        data = self.__load()
        data[key] = value
        self.__save(data)

    def __contains__(self, key) -> bool:
        return key in self.__load()

    def __str__(self) -> str:
        s = "\n\t".join(sorted(self))
        return f"`randonneur_data` registry with {len(self)} files:\n\t{s}"

    __repr__ = lambda x: str(x)

    def __delitem__(self, name) -> None:
        data = self.__load()
        del data[name]
        self.__save(data)

    def __len__(self) -> int:
        return len(self.__load())

    def __iter__(self) -> Any:
        return iter(self.__load())

    def __hash__(self) -> int:
        return hash(self.__load())

    def add_file(self, filepath: Path, replace: bool = False) -> Path:
        """Add existing file to data repo."""
        if not isinstance(filepath, Path):
            filepath = Path(filepath)

        new_path = DATA_DIR / filepath.name
        if new_path.exists() and not replace:
            raise ValueError(f"File {new_path} already exists and `replace` is `False`")

        data = {
            k: v for k, v in json.load(open(filepath)).items() if k not in DATA_LABELS
        }

        size = filepath.stat().st_size
        if size > 2e5:
            data["filename"] = f"{new_path.stem}.xz"
            data["compression"] = "lzma"
            new_path = new_path.parent / data["filename"]
            with lzma.LZMAFile(
                new_path, mode="w", check=lzma.CHECK_SHA256, preset=9
            ) as lzma_file:
                lzma_file.write(open(filepath, "rb").read())
        else:
            data["filename"] = filepath.name
            data["compression"] = False
            shutil.copyfile(filepath, new_path)

        self[data["name"]] = data
        return new_path

    def get_file(self, label: str) -> dict:
        metadata = self.__load()[label]
        if metadata.get("compression") == "lzma":
            return json.load(
                lzma.LZMAFile(
                    filename=DATA_DIR / metadata["filename"],
                    mode="rb",
                )
            )
        else:
            return json.load(open(DATA_DIR / metadata["filename"]))
