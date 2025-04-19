import click

from commands.ask import ask
from commands.chat import chat


@click.group()
def cli():
    """ChatGPT CLI."""
    pass


cli.add_command(chat)
cli.add_command(ask)

if __name__ == "__main__":
    cli()
