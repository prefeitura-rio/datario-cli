from typer import Typer

from datario_cli.sub import (
    config,
    gke,
    prefect,
)

app = Typer()

app.add_typer(
    gke.app,
    name="gke",
    help="Setup Google Kubernetes Engine",
)

app.add_typer(
    prefect.app,
    name="prefect",
    help="Setup Prefect Agent",
)

app.add_typer(
    config.app,
    name="config",
    help="Configurations management",
)


@app.command()
def version():
    """Prints the version number"""
    from datario_cli import __version__
    print(f"datario-cli version {__version__}")


@app.command()
def upgrade():
    """Upgrade datario-cli"""
    from datario_cli.utils import upgrade
    upgrade()


if __name__ == "__main__":
    app()
