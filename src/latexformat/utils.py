import filecmp
import typing
from pathlib import Path
import sys


def search_parents_for_file(
    file_name: str, directory: Path
) -> typing.Optional[Path]:
    while True:
        guess = directory / file_name
        if guess.is_file():
            return guess
        if directory.parent == directory:
            return None
        directory = directory.parent


def is_empty_generator(generator: typing.Generator) -> bool:
    dummy = object()
    return next(generator, dummy) is dummy


def files_have_same_contents(file: Path, base_file: Path) -> bool:
    return filecmp.cmp(str(file), str(base_file))


def path_to_null_device() -> str:
    return "/dev/null" if sys.platform != "win32" else "NUL"


def construct_path_or_none(optional_path: str) -> typing.Optional[Path]:
    if optional_path is None:
        return None
    return Path(optional_path)
