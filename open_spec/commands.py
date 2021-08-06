import click
from flask import Flask, current_app
from flask.cli import AppGroup, with_appcontext

# oas_cli = AppGroup(

oas_cli = click.Group(
    "oas",
    help="command line interface to control OAS of flask app and marshmallow schemas\n \
                    This tool can help by generating stub files, and merging them to form the OAS file",
)


@oas_cli.command(
    "init",
    help="Generate files from stubs, If file already present, It will merged with the stub data \n \
        Always consider revising the generated files. and caching the previous versions.",
)
@click.option(
    "-o",
    "--document-options",
    is_flag=True,
    default=None,
    is_eager=True,
)
@with_appcontext
def init(document_options=None):
    current_app.extensions["open_spec"].do_init(
        document_options=document_options
    )


def register(
    app: Flask,
):
    # wrapper = CliWrapper(self)

    ####################################################33
    @oas_cli.command(
        "build",
        help="Extract data from all marshmallow schemas, add them in the right place, \n \
            merge all files from .generated dir in one file and apply overrides if present in overrides file.",
    )
    @click.option("--validate", type=bool, default=True)
    @click.option("--cache", type=bool, default=True)
    def build(validate, cache):
        app.extensions["open_spec"].do_build(validate=validate, cache=cache)

    # @click.option(
    #    "-o",
    #    "--document-options",
    #    is_flag=True,
    #    default=None,
    # )  # is_eager=True,
    app.cli.add_command(oas_cli)
    # self.oas_cli = wrapper.oas_cli
