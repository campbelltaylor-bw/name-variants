"""CLI entry point: name-variants <name> [options]"""

from __future__ import annotations

import argparse
import json
import sys

from .lookup import lookup_batch


def _main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(
        prog="name-variants",
        description="Look up name variants from the namedb database.",
    )
    parser.add_argument("names", nargs="*", help="Names to look up")
    parser.add_argument(
        "--language",
        action="store_true",
        help="Include language/origin annotations in output",
    )
    parser.add_argument(
        "--fuzzy",
        action="store_true",
        help="Enable fuzzy matching for near-miss names",
    )
    parser.add_argument(
        "--format",
        choices=["text", "json"],
        default="text",
        help="Output format (default: text)",
    )
    parser.add_argument(
        "--stdin",
        action="store_true",
        help="Read names from stdin (one per line)",
    )
    args = parser.parse_args(argv)

    names = list(args.names)
    if args.stdin:
        names.extend(line.strip() for line in sys.stdin if line.strip())

    if not names:
        parser.print_help()
        sys.exit(1)

    results = lookup_batch(
        names,
        strip_language=not args.language,
        fuzzy=args.fuzzy,
    )

    if args.format == "json":
        output = [
            {
                "query": r.query,
                "first_name": r.first_name,
                "canonical": r.canonical,
                "variants": r.variant_names(include_language=args.language),
                "found": r.found,
                "is_canonical": r.is_canonical,
                "matched_as_variant_of": r.matched_as_variant_of,
            }
            for r in results
        ]
        print(json.dumps(output, indent=2))
    else:
        for r in results:
            if r.found:
                variants_str = ", ".join(r.variant_names(include_language=args.language))
                tag = "" if r.is_canonical else f" [variant of {r.matched_as_variant_of}]"
                print(f"{r.first_name}{tag} → {variants_str or '(no variants)'}")
            else:
                print(f"{r.first_name} → (not found)")
