from typer import Typer

from edrio.sub import (
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

if __name__ == "__main__":
    app()
