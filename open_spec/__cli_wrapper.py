import click
from flask.cli import AppGroup
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .open_spec import OpenSpec


class __CliWrapper:
    def __init__(self, open_spec: "OpenSpec") -> None:
        self.oas_cli = oas_cli = AppGroup(
            "oas",
            help="command line interface to control OAS of flask app and marshmallow schemas\n \
                    This tool can help by generating stub files, and merging them to form the OAS file",
        )

        """@oas_cli.command(
            "init",
            help="Generate files from stubs, If file already present, It will merged with the stub data \n \
        Always consider revising the generated files. and caching the previous versions.",
        )
        def init():
            open_spec.init_command()"""

        @oas_cli.command(
            "build",
            help="Extract data from all marshmallow schemas, add them in the right place, \n \
            merge all files from .generated dir in one file and apply overrides if present in overrides file.",
        )
        @click.option("--validate", type=bool, default=True)
        @click.option("--cache", type=bool, default=True)
        def build(validate, cache):
            open_spec.build(validate=validate, cache=cache)

        # @click.option(
        #    "-o",
        #    "--document-options",
        #    is_flag=True,
        #    default=None,
        # )  # is_eager=True,
        open_spec.app.cli.add_command(oas_cli)


_OpenSpec__CliWrapper = __CliWrapper
