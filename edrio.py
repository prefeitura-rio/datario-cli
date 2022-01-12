from typer import Typer

app = Typer()

@app.command()
def edrio():
    print("Edrio")

if __name__ == "__main__":
    app()