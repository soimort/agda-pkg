'''
  agda-pkg
  ~~~~~~~~~~~~~~~~~~~~~~~~~~
'''

import click

from pathlib import *

from ..config import ( AGDA_DEFAULTS_PATH
                     , AGDA_DIR_PATH
                     , AGDA_LIBRARIES_PATH
                     , AGDA_PKG_PATH
                     , AGDA_VERSION
                     , DATABASE_FILE_NAME
                     , DATABASE_FILE_PATH
                     , DATABASE_SEARCH_INDEXES_PATH
                     , GITHUB_USER
                     , INDEX_REPOSITORY_BRANCH
                     , INDEX_REPOSITORY_NAME
                     , INDEX_REPOSITORY_PATH
                     , INDEX_REPOSITORY_URL
                     , REPO
                     )

from ..service.readLibFile import readLibFile
from ..service.database import db, pw
from ..service.database import ( Library
                               , LibraryVersion
                               , Keyword
                               , TestedWith
                               , Dependency
                               )
from pprint   import pprint
from pony.orm import *

@click.group()
def init():
	pass

def create_index():
  db.drop_all_tables(with_all_data=True)
  db.create_tables()

  f = INDEX_REPOSITORY_PATH
  src = f.joinpath("src")

  with db_session:
    for lib in src.glob("*"):
      name = lib.name
      url  = Path(lib).joinpath("url").read_text()
      library = Library(name = name)
      library.url = url
      library.localpath = lib.as_posix()

      print(name)
      print("="*len(name))
      print("- URL: " + url)
      print("- Versions:")
      for version in lib.joinpath("versions").glob("*"):
        libVersion = LibraryVersion(library = library, name = version.name)

        if version.joinpath("sha1").exists():
          libVersion.sha = version.joinpath("sha1").read_text()
          valid = False
          print( "  " + ("- [x]" if valid else "- [ ]") + " v"+(version.name))
        else:
          print("ERROR: "+ version.name + " no valid")

        agdaLibFile = version.joinpath(name + ".agda-lib")
        agdaPkgFile = version.joinpath(name + ".agda-pkg")

        if agdaLibFile.exists():
          libVersion.info_path = agdaLibFile.as_posix()
        if agdaPkgFile.exists():
          libVersion.info_path = agdaPkgFile.as_posix()

    # With all libraries indexed, we proceed to create the dependencies
    # as objects for the index.

    for lib in src.glob("*"):
      library = Library.get(name = lib.name)
      for version in library.versions:
        info = readLibFile(version.info_path)
        keywords = info.get("keywords", [])
        if keywords == []:
          keywords = info.get("category", [])

        for word in keywords:
          keyword =  Keyword.get(word = word)
          if keyword is None:
            keyword = Keyword(word = word)
          keyword.libraries.add(library)
          keyword.libversions.add(version)

        for depend in info["depend"]:
          if type(depend) == list:
            print("no supported yet but the format is X.X <= name <= Y.Y")
          else:
            dependency = Library.get(name = depend)
            if dependency is not None:
              version.requires.add(Dependency(library = dependency))
            else:
              print("Warning!!" + depend + " is not in the index")
              print("this may cause errors in the future.")
    commit()

@init.command()
def init():
  create_index()