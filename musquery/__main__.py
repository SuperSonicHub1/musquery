from argparse import ArgumentParser, Namespace
from pathlib import Path
import apsw
from apsw.shell import Shell
from .vtable import init_module

# HACK: This is for how *I* organize my music
MY_MUSIC_DIR = Path.home() / "Music" / "Listening" 

def parse_args() -> Namespace:
	parser = ArgumentParser()
	parser.add_argument("-p", "--path", type=Path, default=MY_MUSIC_DIR)
	
	subparsers = parser.add_subparsers(required=True)

	parser_repl = subparsers.add_parser('repl', help='view and edit your collection interactively')
	parser_repl.set_defaults(func=repl)

	return parser.parse_args()

def repl(args: Namespace, db: apsw.Connection) -> None:
	"""
	https://rogerbinns.github.io/apsw/shell.html
	"""
	Shell(db=db).cmdloop()

def main() -> None:
	args = parse_args()
	connection = apsw.Connection(":memory:")
	init_module(connection, args.path)
	args.func(args, connection)

main()
