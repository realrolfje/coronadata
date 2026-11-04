#!/usr/bin/env python3

from pathlib import PurePosixPath
import subprocess
import sys


ALLOWED_DIRECTORIES = {"data", "docs"}


def git_paths(*arguments):
    output = subprocess.check_output(["git", *arguments])
    return [path.decode() for path in output.split(b"\0") if path]


def is_generated_path(path):
    parts = PurePosixPath(path).parts
    return bool(parts) and parts[0] in ALLOWED_DIRECTORIES


def main():
    staged = git_paths("diff", "--cached", "--name-only", "-z")
    if staged:
        print("Refusing to publish: the Git index already contains staged changes.", file=sys.stderr)
        return 1

    changed = git_paths("diff", "--name-only", "-z")
    untracked = git_paths("ls-files", "--others", "--exclude-standard", "-z")
    unrelated = [path for path in changed + untracked if not is_generated_path(path)]
    if unrelated:
        print("Refusing to publish: unrelated working-tree changes exist:", file=sys.stderr)
        for path in unrelated:
            print(f"  {path}", file=sys.stderr)
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
