from datetime import datetime
from enum import Enum
from glob import iglob
from typing import Iterator
from itertools import chain
from dataclasses import dataclass, field

from os import path

# ! Unnecessary once Python 3.11 is released
# ? `pip install typing-extensions` for now
from typing_extensions import Self


PathType = str


class MossLanguage( str, Enum ):

    '''Enum representing all languages moss currently supports'''
    C = 'c'
    CC = 'cc'
    JAVA = 'java'
    ML = 'ml'
    PASCAL = 'pascal'
    ADA = 'ada'
    LISP = 'lisp'
    SCHEME = 'scheme'
    HASKELL = 'haskell'
    FORTRAN = 'fortran'
    ASCII = 'ascii'
    VHDL = 'vhdl'
    PERL = 'perl'
    MATLAB = 'matlab'
    PYTHON = 'python'
    MIPS = 'mips'
    PROLOG = 'prolog'
    SPICE = 'spice'
    VB = 'vb'
    CSHARP = 'csharp'
    MODULA2 = 'modula2'
    A8086 = 'a8086'
    JAVASCRIPT = 'javascript'
    PLSQL = 'plsql'


@dataclass( init=True, repr=True )
class MossConfig():

    '''Class representing configuration options used by the moss'''
    user_id: str = field( init=True )
    server: str = field( init=True, default='moss.stanford.edu' )
    port: str = field( init=True, default='7690' )

    comment: str = field( init=True, default_factory=lambda: str( datetime.today() ) )
    language: MossLanguage = field( init=True, default=MossLanguage.C )
    use_directory_mode: bool = field( init=True, default=False )

    use_experimental_mode: bool = field( init=True, kw_only=True, default=False )
    max_matches_displayed: int = field( init=True, kw_only=True, default=250 )
    max_ignore_threshold: int = field( init=True, kw_only=True, default=10 )

    __base_files: list[ PathType ] = field( init=False, repr=False, default_factory=list )
    __base_globs: list[ PathType ] = field( init=False, repr=False, default_factory=list )

    __submission_files: list[ PathType ] = field( init=False, repr=False, default_factory=list )
    __submission_globs: list[ PathType ] = field( init=False, repr=False, default_factory=list )

    def set_language( self, language: MossLanguage ) -> Self:
        """
        `set_language` sets the language (-l) parameter to be used in the MOSS query
        
        Args:
          language (MossLanguage): The language of the code you're submitting.
        
        Returns:
          The object itself.
        """
        self.language = language
        return self

    def set_experimental( self, experimental_flag: bool ) -> Self:
        """
        `set_experimental` sets the experimental flag (-x)

        Args:
          experimental_flag (bool): If set to True, the experimental mode will be used.

        Returns:
          The object itself.
        # """
        self.use_experimental_mode = experimental_flag
        return self

    def set_directory_mode( self, directory_flag: bool ) -> Self:
        """
        `set_directory` sets the directory flag (-d)

        Args:
          directory_flag (bool): If set to True, the directory mode will be used.

        Returns:
          The object itself.
        # """
        self.use_directory_mode = directory_flag
        return self

    def set_comment( self, comment: str ) -> Self:
        """
        This function sets the comment string to be used in the MOSS query
        `set_comment` sets the experimental flag (-c)

        Args:
          comment (str): A string that will be included in the MOSS query.

        Returns:
          The object itself.
        """
        self.comment = comment
        return self

    def add_base_file( self, base_file: PathType, *, glob: bool = False ):
        """
        This function adds a file to the list of base files,
            or a glob to the list of base globs.

        In the case of a file, it ensures file is a valid file before adding.
        Args:
          base_file (PathType): PathType
          glob (bool): bool = False. Defaults to False
          Indicates whether the argument passed is a file or glob

        Raises:
        FileNotFoundError: base_file is non-existent
        ValueError: base_file is not a file

        Returns:
          The object itself.
        """
        if not glob:

            if not path.exists( base_path := self._resolve_file( base_file ) ):
                raise FileNotFoundError( base_file )
            if not path.isfile( base_path ):
                raise ValueError( f'{base_file} is not a file' )

            self.__base_files.append( base_path )
        else:
            self.__base_globs.append( self._expand_file( base_file ) )

        return self

    def add_submission_file( self, submission_file: PathType, *, glob: bool = False ):
        """
        This function adds a file to the list of files to be submitted to moss for evaluation,
            or a glob to the list of globs to submit.

        In the case of a file, it ensures file is a valid file before adding.
        Args:
          submission_file (PathType): PathType
          glob (bool): bool = False. Defaults to False
          Indicates whether the argument passed is a file or glob

        Raises:
        FileNotFoundError: submission_file is non-existent
        ValueError: submission_file is not a file

        Returns:
          The object itself.
        """

        if not glob:
            if not path.exists( submission_path := self._resolve_file( submission_file ) ):
                raise FileNotFoundError( submission_file )
            if not path.isfile( submission_path ):
                raise ValueError( f'{submission_file} is not a file' )

            self.__submission_files.append( submission_path )
        else:
            self.__submission_globs.append( self._expand_file( submission_file ) )
        return self

    def __str__( self ):
        """
        It returns a string that is the command line arguments for the moss program
        
        Returns:
          The string representation of the object.
        """
        return f'moss -c "{self.comment}" -l {self.language}'                 \
               f' -m {self.max_ignore_threshold} -n {self.max_matches_displayed}'    \
               f'{" -x" if self.use_experimental_mode else ""}'                                    \
               f''' {" ".join(("-b " + f'"{file}"' for file in self.base_files()))}'''        \
               f''' {" ".join((f'"{file}"' for file in self.submission_files()))}'''

    def _expand_file( self, file: PathType ) -> str:
        """
        > It takes a file path and returns a file path
        
        Args:
          file (PathType): The file to be read.
        
        Returns:
          The expanded file path.
        """
        return path.expanduser( path.expandvars( file ) )

    def _resolve_file( self, file: PathType ) -> str:
        """
        > It takes a file path, expands it, and returns the absolute path
        
        Args:
          file (PathType): PathType
        
        Returns:
          The absolute path of the file.
        """
        return path.abspath( self._expand_file( file ) )

    def base_files( self ) -> Iterator[ PathType ]:
        """
        > `base_files` returns an iterator of the assignment's base files

        Returns: An iterator over all base files
        """
        return filter(
            path.isfile,
            chain(
                *( ( iglob( base_glob, recursive=True ) for base_glob in self.__base_globs ) ),
                iter( self.__base_files )
            )
        )

    def submission_files( self ) -> Iterator[ PathType ]:
        """
        > `submission_files` returns an iterator of the files that should be submitted for this assignment

        Returns: An iterator over all base files
        """
        return filter(
            path.isfile,
            chain(
                *( ( iglob( sub_glob, recursive=True ) for sub_glob in self.__submission_globs ) ),
                iter( self.__submission_files )
            )
        )


if __name__ == '__main__':
    test_params_full = MossConfig("12345")                      \
        .set_comment('test sample')                             \
        .set_language(MossLanguage.PYTHON)                      \
        .set_experimental(True)                                 \
        .add_base_file( '../../README.md' )                     \
        .add_base_file( '../../LICENSE' )                       \
        .add_submission_file('./config.py')                     \
        .add_submission_file('~/.bash_history')

    print( test_params_full )
    print( repr( test_params_full ) )


    test_params_glob = MossConfig("12345")                      \
        .set_comment('test sample glob')                        \
        .set_language(MossLanguage.JAVA)                        \
        .set_experimental(True)                                 \
        .add_base_file( '~/../ian/Desktop/*.pdf', glob=True)   \
        .add_submission_file('~/Desktop/*.pdf', glob=True)

    print( test_params_glob )
    print( repr( test_params_glob ) )
