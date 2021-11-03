from logging import getLogger, INFO, basicConfig, StreamHandler, DEBUG
from argparse import ArgumentParser

basicConfig(level=INFO)
log = getLogger(__name__)
# log.addHandler(StreamHandler())

def main(parser: ArgumentParser):
    log.info(
        "\tWelcome to the API service of minibitcoin!\n"
        "In order to complete your setup, run the `genIdenti` command\n"
        "To see a list of available commands run `--help`\n"
    )
    while True:
        args = parser.parse_args(input("> ").split())
        print(args)
    
    
    


if __name__ == "__main__":
    parser = ArgumentParser(description="Controller for nodes & transactions", usage="python cli/app.py [start] [-h]")
    parser.add_argument("start", help="Start the API service")

    genidenti_parser = parser.add_argument_group("genIdenti")
    genidenti_parser.add_argument("-i", help="Number of identities to generate", type=int)
    genidenti_parser.add_argument("-n", help="Number of nodes to generate", type=int)

    args = parser.parse_args()
    if args.start == "start":
        main(parser)
    else:
        parser.print_help()
