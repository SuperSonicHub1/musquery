"""
https://docs.python.org/3/library/mimetypes.html
https://docs.python.org/3/library/pathlib.html
https://github.com/betodealmeida/shillelagh/blob/main/src/shillelagh/backends/apsw/vt.py
https://rogerbinns.github.io/apsw/vtable.html
https://mutagen.readthedocs.io/en/latest/api/base.html#mutagen.File
"""

import apsw
from pathlib import Path
from mimetypes import guess_type
from typing import Sequence, Tuple, List, Optional, Union, Any, Iterator, cast, Dict
from mutagen import File, FileType

# https://github.com/betodealmeida/shillelagh/blob/main/src/shillelagh/typing.py
Constraint = Union[None, int, Tuple[int, bool]]
SQLiteConstraint = int

COLUMNS = [
	# https://github.com/quodlibet/mutagen/blob/master/mutagen/easyid3.py#L470
	"album",
	"bpm",
	"compilation",  # iTunes extension
	"composer",
	"copyright",
	"encodedby",
	"lyricist",
	"length",
	"media",
	"mood",
	"grouping",
	"title",
	"version",
	"artist",
	"albumartist",
	"conductor",
	"arranger",
	"discnumber",
	"organization",
	"tracknumber",
	"author",
	"albumartistsort",  # iTunes extension
	"albumsort",
	"composersort",  # iTunes extension
	"artistsort",
	"titlesort",
	"isrc",
	"discsubtitle",
	"language",
	# Where the song is located on the filesystem
	'path',
]

path_to_inode: Dict[Path, int] = dict()

def get_inode(path: Path) -> int:
	inode = path.stat().st_ino
	path_to_inode[path] = inode

	return inode

def get_path(inode: int) -> Path:
	return { v: k for k, v in path_to_inode.items() }[inode]

def is_music(path: Path) -> bool:
	type, encoding = guess_type(path)

	if type:
		return type.startswith("audio")
	else:
		return False

def get_tag(file: FileType, tag: str) -> Optional[str]:
	if not file.tags:
		return None

	value = file.tags.get(tag, None)
	if isinstance(value, list):
		return value[0]
	# Assumably a string
	else:
		return value

def path_stem(*args: Any) -> str:
	return Path(args[0]).stem

def init_module(connection: apsw.Connection, music_dir: Path) -> None:
	module = VTModule(music_dir)
	connection.createmodule("music", module)
	connection.execute("CREATE VIRTUAL TABLE music USING music()")
	connection.createscalarfunction(path_stem.__name__, path_stem)

class VTModule:
	music_dir: Path
	
	def __init__(self, music_dir: Path) -> None:
		self.music_dir = music_dir

	def Create(self, connection: apsw.Connection, modulename: str, databasename: str, tablename: str, *args):
		table = VTTable(self.music_dir)
		return table.get_create_table(tablename), table

	Connect=Create

class VTCursor:
	music_dir: Path
	data: Iterator[Tuple[Any, ...]]
	current_row: Tuple[Any, ...]
	eof: bool
	
	def __init__(self, music_dir: Path) -> None:
		self.music_dir = music_dir
		self.eof = False

	def generate_rows(self) -> Iterator[Tuple[Any, ...]]:
		descriptors = self.music_dir.glob("**/*")
		files = (descriptor for descriptor in descriptors if descriptor.is_file())
		music_files = (file for file in files if is_music(file))
		metadatas = ((path, file) for path in music_files if (file := File(path, easy=True)))
		metadata_rows = (
			(get_inode(path), *[get_tag(file, column) for column in COLUMNS[:-1]], str(path))
			for (path, file)
			in metadatas
		)

		return metadata_rows

	def Filter(self, indexnum: int, indexname: str, constraintargs: Optional[Tuple]) -> None:
		"""
		TODO: support BestIndex
		"""

		self.data = self.generate_rows()
		self.Next()

	def Eof(self) -> bool:
		"""
		Called to ask if we are at the end of the table.
		"""
		return self.eof

	def Rowid(self) -> int:
		"""
		Return the current rowid.
		"""
		return cast(int, self.current_row[0])

	def Column(self, col) -> Any:
		"""
		Requests the value of the specified column number of the current row.
		"""
		return self.current_row[1 + col]

	def Next(self) -> None:
		"""
		Move the cursor to the next row.
		"""
		try:
			self.current_row = next(self.data)
			self.eof = False
		except StopIteration:
			self.eof = True

	def Close(self) -> None:
		"""
		This is the destructor for the cursor.
		"""
		return None

class VTTable:
	music_dir: Path

	def __init__(self, music_dir: Path) -> None:
		self.music_dir = music_dir

	def get_create_table(self, tablename: str) -> str:
		return f"CREATE TABLE {tablename} ({', '.join(f'{column} TEXT' for column in COLUMNS)})"

	def BestIndex(
		self,
		constraints: List[Tuple[int, SQLiteConstraint]],
		orderbys: List[Tuple[int, bool]],
	) -> Optional[Tuple[List[Constraint], int, str, bool, float]]:
		"""
		TODO
		"""
		return None

	def Open(self) -> VTCursor:
		"""
		Returns a cursor object.
		"""
		return VTCursor(self.music_dir)

	def UpdateChangeRow(self, row: int, newrowid: int, fields: Tuple[Any, ...]):
		"""
		https://rogerbinns.github.io/apsw/vtable.html#apsw.VTTable.UpdateChangeRow
		We aren't going to allow users to change the ID of a file,
		so we ignore newrowid.
		
		TODO: Implement
		"""

		path = get_path(row)
		file = File(path, easy=True)

		if not file.tags:
			file.add_tags()

		for key, value in zip(COLUMNS, fields):
			if key == 'path':
				continue

			if value == None:
				if key in file:
					del file[key]
				else:
					pass
			else:
				file[key] = value

		file.save()

	def Disconnect(self) -> None:
		return None

	Destroy = Disconnect
