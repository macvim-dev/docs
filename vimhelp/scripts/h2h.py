#!/usr/bin/env .venv/bin/python3

# This script is meant to be run from the top-level directory of the
# repository, as 'scripts/h2h.py'. The virtualenv must already exist
# (use "inv venv" to create it).

import argparse
import os.path
import pathlib
import sys

import flask

root_path = pathlib.Path(__file__).parent.parent

sys.path.append(str(root_path))

from vimhelp.vimh2h import VimH2H  # noqa: E402


def main():
    parser = argparse.ArgumentParser(description="Convert Vim help files to HTML")
    parser.add_argument(
        "--in-dir",
        "-i",
        required=True,
        type=pathlib.Path,
        help="Directory of Vim doc files",
    )
    parser.add_argument(
        "--out-dir",
        "-o",
        type=pathlib.Path,
        help="Output directory (omit for no output)",
    )
    parser.add_argument(
        "--project",
        "-p",
        choices=("vim", "neovim", "macvim"),
        default="vim",
        help="Vim flavour (default: vim)",
    )
    parser.add_argument(
        "--web-version",
        "-w",
        action="store_true",
        help="Generate the web version of the files (default: offline version)",
    )
    parser.add_argument(
        "--theme",
        "-t",
        choices=("light", "dark"),
        help="Color theme (default: OS-native)",
    )
    parser.add_argument(
        "--version",
        help="The version of Vim this document was generated from",
    )
    parser.add_argument(
        "--commit",
        help="The commit of Vim this document was generated from",
    )
    parser.add_argument(
        "--no-tags",
        "-T",
        action="store_true",
        help="Ignore any tags file, always recreate tags from scratch",
    )
    parser.add_argument(
        "--output-tags-json",
        "-J",
        action="store_true",
        help="Output tags.json file and client-side tags redirect/search, useful for static page",
    )
    parser.add_argument(
        "--profile", "-P", action="store_true", help="Profile performance"
    )
    parser.add_argument(
        "basenames", nargs="*", help="List of files to process (default: all)"
    )
    args = parser.parse_args()

    app = flask.Flask(
        __name__,
        root_path=pathlib.Path(__file__).resolve().parent,
        static_url_path="",
        static_folder="../static",
        template_folder="../templates",
    )
    app.jinja_options["trim_blocks"] = True
    app.jinja_options["lstrip_blocks"] = True

    with app.app_context():
        if args.profile:
            import cProfile
            import pstats

            with cProfile.Profile() as pr:
                run(args)
            stats = pstats.Stats(pr).sort_stats("cumulative")
            stats.print_stats()
        else:
            run(args)


def run(args):
    if not args.in_dir.is_dir():
        raise RuntimeError(f"{args.in_dir} is not a directory")

    prelude = VimH2H.prelude(theme=args.theme)

    mode = "hybrid" if args.web_version else "offline"

    if not args.no_tags and (tags_file := args.in_dir / "tags").is_file():
        print("Processing tags file...")
        h2h = VimH2H(mode=mode, project=args.project, version=args.version, commit=args.commit, tags=tags_file.read_text())
        faq = args.in_dir / "vim_faq.txt"
        if faq.is_file():
            print("Processing FAQ tags...")
            h2h.add_tags(faq.name, faq.read_text())
    else:
        print("Initializing tags...")
        h2h = VimH2H(mode=mode, project=args.project, version=args.version, commit=args.commit)
        for infile in args.in_dir.iterdir():
            if infile.suffix == ".txt":
                h2h.add_tags(infile.name, infile.read_text())

    if args.out_dir is not None:
        args.out_dir.mkdir(exist_ok=True)

    for infile in args.in_dir.iterdir():
        if len(args.basenames) != 0 and infile.name not in args.basenames:
            continue
        if infile.suffix != ".txt" and infile.name != "tags":
            print(f"Ignoring {infile}")
            continue
        content = infile.read_text()
        print(f"Processing {infile}...")
        html = h2h.to_html(infile.name, content)
        if infile.name != "help.txt":
            out_filename = f"{infile.name}.html"
        else:
            out_filename = "index.html"
        if args.out_dir is not None:
            with (args.out_dir / out_filename).open("w") as f:
                f.write(prelude)
                f.write(html)

    if args.output_tags_json:
        print("Processing tags.json...")
        json = h2h.gen_tags_json()
        out_filename = "tags.json"
        if args.out_dir is not None:
            with (args.out_dir / out_filename).open("w") as f:
                f.write(json)
        print("Generating redirect.html...")
        redirect_html = h2h.to_redirect_html()
        out_filename = "redirect.html"
        if args.out_dir is not None:
            with (args.out_dir / out_filename).open("w") as f:
                f.write(prelude)
                f.write(redirect_html)

    if args.out_dir is not None:
        print("Symlinking static files...")
        static_dir_rel = os.path.relpath(root_path / "static", args.out_dir)
        for target in (root_path / "static").iterdir():
            target_name = target.name
            if target_name.startswith(f"favicon-{args.project}"):
                src_name = target_name.replace(f"favicon-{args.project}", "favicon")
            elif target_name.startswith("favicon-"):
                continue
            else:
                src_name = target_name
            src = pathlib.Path(args.out_dir / src_name)
            src.unlink(missing_ok=True)
            src.symlink_to(f"{static_dir_rel}/{target_name}")

    print("Done.")


main()
