# musquery

A new-age music metadata management system powered by [Mutagen](https://mutagen.readthedocs.io/en/latest/),
[SQLite](https://sqlite.org), and [apsw](https://rogerbinns.github.io/apsw/index.html).

Query and modify your music data with the power of SQL inside a shell with `python -m musquery repl`.

## TODOs
- write commands for various common "migrations" one might have for their music collection, all implemented in SQL
    - similar to Alexandro Sanchez' [Curator](https://github.com/AlexAltea/curator)
- optimize filtering
- implement transactions so one can roll back changes to their music collection before writing to disk
- add full text search support to queries

## Demos

### Adding Title Metadata from FIle Names
```
sqlite> select title, path, path_stem(path) from music where path like "%Adultswim%";
|/home/kwilliams/Music/Listening/Adultswim Bumpworthy Album/00-Intro-Elavator music part 1.mp3|00-Intro-Elavator music part 1
|/home/kwilliams/Music/Listening/Adultswim Bumpworthy Album/01-Yesterdays New Quintet influnced pt1.mp3|01-Yesterdays New Quintet influnced pt1
|/home/kwilliams/Music/Listening/Adultswim Bumpworthy Album/02-Move too japan.mp3|02-Move too japan
sqlite> WITH m as (select *, rowid, path_stem(path) as stem from music)
    ..> select substr(m.stem, 4, length(m.stem)) from m where path like "%Adultswim%";
Intro-Elavator music part 1
Yesterdays New Quintet influnced pt1
Move too japan
sqlite> WITH m as (select *, rowid, path_stem(path) as stem from music)
    ..> UPDATE music SET title=(SELECT substr(stem, 4, length(stem)) FROM m WHERE m.rowid = music.rowid) WHERE path LIKE "%Adultswim%";
sqlite> select title, path_stem(path) from music where path like "%Adultswim%";
Intro-Elavator music part 1|00-Intro-Elavator music part 1
Yesterdays New Quintet influnced pt1|01-Yesterdays New Quintet influnced pt1
Move too japan|02-Move too japan
```

### Removing all references to Dread Collective from *WLFGRL*.
```
sqlite> select album, title, artist  from music where title like "%Machine Girl - %";
album|title|artist
Machine Girl - WLFGRL|Machine Girl - MG1|DREDCOL.
Machine Girl - WLFGRL|Machine Girl - Ionic Funk (20XXX Battle Music)|DREDCOL.
Machine Girl - WLFGRL|Machine Girl - Krystle (URL Cyber Palace Mix)|DREDCOL.
Machine Girl - WLFGRL|Machine Girl - Ginger Claps|DREDCOL.
Machine Girl - WLFGRL|Machine Girl - Ghost|DREDCOL.
Machine Girl - WLFGRL|Machine Girl - 覆面調査員 (GabberTrap Mix) [Frenesi remix]|DREDCOL.
Machine Girl - WLFGRL|Machine Girl - Out By 16, Dead on the Scene|DREDCOL.
Machine Girl - WLFGRL|Machine Girl - かわいい Post Rave Maximalist|DREDCOL.
Machine Girl - WLFGRL|Machine Girl - Phase α|DREDCOL.
Machine Girl - WLFGRL|Machine Girl - Freewill (Phase β)|DREDCOL.
Machine Girl - WLFGRL|Machine Girl - Excruciating Deth (Phase γ)|DREDCOL.
Machine Girl - WLFGRL|Machine Girl - Hidden Power (Phase δ)|DREDCOL.
Machine Girl - WLFGRL|Machine Girl - MG2|DREDCOL.
sqlite> select album, substr(album, 16, length(album)), title, substr(title, 16, length(title)), artist, "Machine Girl" from music where title like "%Machine Girl - %";
album|substr(album, 16, length(album))|title|substr(title, 16, length(title))|artist|"Machine Girl"
Machine Girl - WLFGRL|WLFGRL|Machine Girl - MG1|MG1|DREDCOL.|Machine Girl
Machine Girl - WLFGRL|WLFGRL|Machine Girl - Ionic Funk (20XXX Battle Music)|Ionic Funk (20XXX Battle Music)|DREDCOL.|Machine Girl
Machine Girl - WLFGRL|WLFGRL|Machine Girl - Krystle (URL Cyber Palace Mix)|Krystle (URL Cyber Palace Mix)|DREDCOL.|Machine Girl
Machine Girl - WLFGRL|WLFGRL|Machine Girl - Ginger Claps|Ginger Claps|DREDCOL.|Machine Girl
Machine Girl - WLFGRL|WLFGRL|Machine Girl - Ghost|Ghost|DREDCOL.|Machine Girl
Machine Girl - WLFGRL|WLFGRL|Machine Girl - 覆面調査員 (GabberTrap Mix) [Frenesi remix]|覆面調査員 (GabberTrap Mix) [Frenesi remix]|DREDCOL.|Machine Girl
Machine Girl - WLFGRL|WLFGRL|Machine Girl - Out By 16, Dead on the Scene|Out By 16, Dead on the Scene|DREDCOL.|Machine Girl
Machine Girl - WLFGRL|WLFGRL|Machine Girl - かわいい Post Rave Maximalist|かわいい Post Rave Maximalist|DREDCOL.|Machine Girl
Machine Girl - WLFGRL|WLFGRL|Machine Girl - Phase α|Phase α|DREDCOL.|Machine Girl
Machine Girl - WLFGRL|WLFGRL|Machine Girl - Freewill (Phase β)|Freewill (Phase β)|DREDCOL.|Machine Girl
Machine Girl - WLFGRL|WLFGRL|Machine Girl - Excruciating Deth (Phase γ)|Excruciating Deth (Phase γ)|DREDCOL.|Machine Girl
Machine Girl - WLFGRL|WLFGRL|Machine Girl - Hidden Power (Phase δ)|Hidden Power (Phase δ)|DREDCOL.|Machine Girl
Machine Girl - WLFGRL|WLFGRL|Machine Girl - MG2|MG2|DREDCOL.|Machine Girl
sqlite> update music set album=substr(album, 16, length(album)), title=substr(title, 16, length(title)), artist="Machine Girl" where title like "%Machine Girl - %";
sqlite> select album, title, artist from music where title like "%Machine Girl - %";
sqlite> select album, title, artist from music where artist like "Machine Girl";
album|title|artist
WLFGRL|MG1|Machine Girl
WLFGRL|Ionic Funk (20XXX Battle Music)|Machine Girl
WLFGRL|Krystle (URL Cyber Palace Mix)|Machine Girl
WLFGRL|Ginger Claps|Machine Girl
WLFGRL|Ghost|Machine Girl
WLFGRL|覆面調査員 (GabberTrap Mix) [Frenesi remix]|Machine Girl
WLFGRL|Out By 16, Dead on the Scene|Machine Girl
WLFGRL|かわいい Post Rave Maximalist|Machine Girl
WLFGRL|Phase α|Machine Girl
WLFGRL|Freewill (Phase β)|Machine Girl
WLFGRL|Excruciating Deth (Phase γ)|Machine Girl
WLFGRL|Hidden Power (Phase δ)|Machine Girl
WLFGRL|MG2|Machine Girl
```
