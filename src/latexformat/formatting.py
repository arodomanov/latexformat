import subprocess
from pathlib import Path
import typing

from .utils import (
    search_parents_for_file,
    files_have_same_contents,
    is_empty_directory,
    path_to_null_device,
)


def search_for_latexindent_settings_file(
    directory: Path,
) -> typing.Optional[Path]:
    return search_parents_for_file("latexindent.yaml", directory)


def run_latexindent(
    source_path: Path,
    output_path: typing.Optional[Path] = None,
    settings_path: typing.Optional[Path] = None,
):
    base_command = [
        "latexindent",
        "-g",
        path_to_null_device(),
        "-m",
    ]

    if settings_path is None:
        # Try to find it automatically
        settings_path = search_for_latexindent_settings_file(source_path.parent)

    if settings_path is not None:
        base_command += ["-l", str(settings_path)]

    if output_path is not None:
        with open(output_path, "w") as output_file:
            subprocess.run(
                base_command + [str(source_path)],
                stdout=output_file,
                check=True,
            )
    else:
        subprocess.run(
            base_command + ["-wd", "-s"] + [str(source_path)],
            check=True,
        )


def format_file_and_override(
    source_path: Path, settings_path: typing.Optional[Path] = None
):
    run_latexindent(source_path, settings_path=settings_path)


def format_file_and_save_to(
    source_path: Path,
    output_path: Path,
    create_parent_directories: bool = False,
    save_only_if_different: bool = False,
    settings_path: typing.Optional[Path] = None,
):
    if create_parent_directories:
        output_path_directory = output_path.parent
        output_path_directory.mkdir(parents=True, exist_ok=True)

    run_latexindent(
        source_path, output_path=output_path, settings_path=settings_path
    )

    if save_only_if_different:
        if files_have_same_contents(output_path, source_path):
            output_path.unlink()
        if is_empty_directory(output_path_directory):
            output_path_directory.rmdir()


def format_files_and_override(
    paths: typing.Iterable[Path], settings_path: typing.Optional[Path] = None
):
    for path in paths:
        format_file_and_override(path, settings_path=settings_path)


def format_files_given_by_pattern_and_override(
    root_directory: Path,
    pattern: str,
    settings_path: typing.Optional[Path] = None,
):
    paths = root_directory.glob(pattern)
    format_files_and_override(paths, settings_path=settings_path)


def format_files_and_save_to_preserving_relative_paths(
    paths: typing.Iterable[Path],
    save_directory: Path,
    reference_directory: Path,
    save_only_if_different: bool = False,
    settings_path: typing.Optional[Path] = None,
):
    for path in paths:
        output_path = save_directory / path.relative_to(reference_directory)
        format_file_and_save_to(
            path,
            output_path,
            create_parent_directories=True,
            save_only_if_different=save_only_if_different,
            settings_path=settings_path,
        )


def format_files_given_by_pattern_and_save_to(
    source_directory: Path,
    pattern: str,
    save_directory: Path,
    save_only_if_different: bool = False,
    settings_path: typing.Optional[Path] = None,
):
    paths = source_directory.glob(pattern)
    format_files_and_save_to_preserving_relative_paths(
        paths,
        save_directory,
        reference_directory=source_directory,
        save_only_if_different=save_only_if_different,
        settings_path=settings_path,
    )
