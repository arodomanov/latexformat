import subprocess
from pathlib import Path
import typing
import tempfile
import shutil

from .utils import (
    search_parents_for_file,
    files_have_same_contents,
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
        "-r"
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


def format_file_and_save_to_without_comparing(
    source_path: Path,
    output_path: Path,
    create_parent_directories: bool = False,
    settings_path: typing.Optional[Path] = None,
):
    if create_parent_directories:
        output_path.parent.mkdir(parents=True, exist_ok=True)

    run_latexindent(
        source_path, output_path=output_path, settings_path=settings_path
    )


def format_file_and_save_to_only_if_different(
    source_path: Path,
    output_path: Path,
    create_parent_directories: bool = False,
    settings_path: typing.Optional[Path] = None,
):
    # TODO: Get rid of creating the temporary file?
    with tempfile.NamedTemporaryFile() as temporary_file:
        temporary_output_path = Path(temporary_file.name)

        run_latexindent(
            source_path,
            output_path=temporary_output_path,
            settings_path=settings_path,
        )

        if not files_have_same_contents(temporary_output_path, source_path):
            if create_parent_directories:
                output_path.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy(temporary_output_path, output_path)


def format_file_and_save_to(
    source_path: Path,
    output_path: Path,
    create_parent_directories: bool = False,
    save_only_if_different: bool = False,
    settings_path: typing.Optional[Path] = None,
):
    if save_only_if_different:
        format_file_and_save_to_only_if_different(
            source_path,
            output_path,
            create_parent_directories=create_parent_directories,
            settings_path=settings_path,
        )
    else:
        format_file_and_save_to_without_comparing(
            source_path,
            output_path,
            create_parent_directories=create_parent_directories,
            settings_path=settings_path,
        )


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
    save_directory.mkdir(exist_ok=True)
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
