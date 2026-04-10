import typer

from b2t import __version__


app = typer.Typer(add_completion=False, no_args_is_help=True)


@app.callback(invoke_without_command=True)
def version_callback(
    version: bool = typer.Option(
        False,
        "--version",
        help="Show the current version and exit.",
        is_eager=True,
    ),
) -> None:
    if version:
        typer.echo(__version__)
        raise typer.Exit()


def main() -> None:
    app(prog_name="bili2text")
