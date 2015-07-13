# FRISC - Filesystem Realtime Indexer and Search Client

this will be a fulltext and metadata indexer for linux filesystems

Requirements:
  * elasticsearch [ https://github.com/elastic/elasticsearch ]
  * tikaJaxRS [ https://wiki.apache.org/tika/TikaJAXRS ]
  
Install both requirements and run them as local services 


## State and Todo

For now it can parse PDF, plaintext, ODS and ODT Documents. It might work for other files, but I only tested those so far.

Images expose their EXIF-Data, but we probably want some more information of the actual content, to do similarity searches and index the dominant color scheme. So next on the list is an image parser.

It is possible to create and update mappings for indexes. The index versions are then aliased to a name used per type (so the reindexing and updateing happens behind the scenes).

Need to provide a read and a write alias per index, so we can switch write alias first, and switch read alias after reindexing - thus all new docs get indexed in the new index version, but are available only after switching the read alias - but that should be ok. 
Alternatively have the write alias temporarely set to both index versions - reindexing will index the new docs twice then)

We will have some file that specifies, which mime-types are mapped to which index, and what parsers should be used on them. That way we can update the mapping independently per type (images, docs, audio, movies, etc).

We probably want to use systemd path observers to set up indexing on file changes, seems superiour over hooking into inotify with python.



