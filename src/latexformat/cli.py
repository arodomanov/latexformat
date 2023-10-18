import argparse
from pathlib import Path
import typing

from .formatting import (
    format_file_and_override,
    format_file_and_save_to,
    format_files_given_by_pattern_and_override,
    format_files_given_by_pattern_and_save_to,
)
from .utils import construct_path_or_none


def run_format_file(
    source_path: Path,
    output_path: typing.Optional[Path],
    settings_path: typing.Optional[Path],
):
    if output_path is None:
        format_file_and_override(source_path, settings_path=settings_path)
    else:
        format_file_and_save_to(
            source_path, output_path, settings_path=settings_path
        )


def run_format_files_given_by_pattern(
    source_path: Path,
    pattern: str,
    output_path: typing.Optional[Path],
    save_only_if_different: bool,
    settings_path: typing.Optional[Path],
):
    if output_path is None:
        format_files_given_by_pattern_and_override(
            source_path,
            pattern,
            settings_path=settings_path,
        )
    else:
        format_files_given_by_pattern_and_save_to(
            source_path,
            pattern,
            output_path,
            save_only_if_different=save_only_if_different,
            settings_path=settings_path,
        )


def run_format(
    source_path: Path,
    pattern: str,
    output_path: typing.Optional[Path],
    save_only_if_different: bool,
    settings_path: typing.Optional[Path],
):
    if source_path.is_file():
        run_format_file(source_path, output_path, settings_path=settings_path)
    elif source_path.is_dir():
        run_format_files_given_by_pattern(
            source_path,
            pattern,
            output_path,
            save_only_if_different=save_only_if_different,
            settings_path=settings_path,
        )
    else:
        raise ValueError(f"Invalid source specified: {source_path}")


def parse_arguments():
    parser = argparse.ArgumentParser(
        prog="latexformat",
        description="This program is a wrapper around `latexindent`, "
        "that provides a convenient CLI for formatting latex source files.",
    )

    parser.add_argument(
        "source",
        help="latex source file or directory containing latex source files to "
        "be formatted",
    )

    parser.add_argument("--version", action="version", version="%(prog)s 0.1.2")

    default_pattern = "**/*.tex"
    parser.add_argument(
        "-p",
        "--pattern",
        default=default_pattern,
        help="glob pattern specifying source files "
        "(relative to the `source` directory) "
        f'to be formatted, defaults to "{default_pattern}"',
    )

    parser.add_argument(
        "-o",
        "--output",
        help="path specifying either a file (if `source` is a file), "
        "or a directory (if `source` is a directory) where you wish to save "
        "the formatted file(s); "
        "if not specified, the formatted file(s) will overwrite the original "
        "source file(s)",
    )

    parser.add_argument(
        "--only_different",
        action="store_true",
        help="if this flag is activated, save each formatted file to the "
        "corresponding location under the `OUTPUT` directory only if the "
        "resulting file is different from the original; "
        "this flag takes effect only when `OUTPUT` is a directory",
    )

    parser.add_argument(
        "-s",
        "--settings_file",
        help="optional path to a yaml file containing settings for "
        "`latexindent`; if not specified, `latexformat` attempts to "
        "find this file automatically for each source by looking for "
        "`latexindent.yaml` first in the directory of the source file, "
        "then in its parent directory, then in the parent of the parent, etc.",
    )

    return parser.parse_args()


def main():
    args = parse_arguments()

    run_format(
        Path(args.source),
        args.pattern,
        construct_path_or_none(args.output),
        args.only_different,
        construct_path_or_none(args.settings_file),
    )
