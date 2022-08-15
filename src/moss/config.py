from abc import ABC, abstractmethod
from datetime import datetime
from enum import Enum
from glob import iglob
from pathlib import Path
from typing import Iterator
from itertools import chain
from dataclasses import dataclass, field

from os import path, PathLike

# ! Unnecessary once Python 3.11 is released
# ? `pip install typing-extensions` for now
from typing_extensions import Self


PathType = str | PathLike


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
class MossParams( ABC ):

    '''Class representing configuration options used by the moss'''
    user_id: str = field( init=True )
    server: str = field( init=True, default='moss.stanford.edu' )
    port: str = field( init=True, default='7690' )

    comment: str = field( init=True, default_factory=lambda: str( datetime.today() ) )
    language: MossLanguage = field( init=True, default=MossLanguage.C )

    use_experimental_mode: bool = field( init=True, kw_only=True, default=False )
    max_matches_displayed: int = field( init=True, kw_only=True, default=250 )
    max_ignore_threshold: int = field( init=True, kw_only=True, default=10 )

    def set_language( self, language: MossLanguage ) -> Self:
        '''Set the language (-l) parameter to be used in the MOSS query'''
        self.language = language
        return self

    def set_experimental( self, experimental_flag: bool ) -> Self:
        '''Set the experimental flag (-x)'''
        self.use_experimental_mode = experimental_flag
        return self

    def set_comment( self, comment: str ) -> Self:
        '''Set the comment (-c) string to be used in the MOSS query'''
        self.comment = comment
        return self

    def __str__( self ):
        return f'moss -c "{self.comment}" -l {self.language}'                 \
               f' -m {self.max_ignore_threshold} -n {self.max_matches_displayed}'    \
               f'{" -x" if self.use_experimental_mode else ""}'                                    \
               f''' {" ".join(("-b " + f'"{file}"' for file in self.base_files()))}'''        \
               f''' {" ".join((f'"{file}"' for file in self.submission_files()))}'''

    def _expand_file( self, file: PathType ) -> str:
        return path.expanduser( path.expandvars( file ) )

    def _resolve_file( self, file: PathType ) -> str:
        return path.abspath( self._expand_file( file ) )

    @abstractmethod
    def base_files( self ) -> Iterator[ Path ]:
        pass

    @abstractmethod
    def submission_files( self ) -> Iterator[ Path ]:
        pass


class PathBasedParams( MossParams ):

    ''' Implementation of moss parameters that uses file paths
        This implementation tries to ensure the validity
        of file paths passed
    '''

    def __init__( self, user_id ) -> None:
        super().__init__( user_id )
        self.__base_files: list[ PathType ] = []
        self.__submission_files: list[ PathType ] = []

    def add_base_file( self, base_file: PathType ):
        ''' Add a base file to the class
            Ensures file is a valid file before adding.
            Raises FileNotFoundError if base_file is non-existent,
            and ValueError if file is base_file a file'''
        if not path.exists( base_path := self._resolve_file( base_file ) ):
            raise FileNotFoundError( base_file )
        if not path.isfile( base_path ):
            raise ValueError( f'{base_file} is not a file' )

        self.__base_files.append( base_path )
        return self

    def add_submission_file( self, submission_file: PathType ):
        ''' Add a submission file to the class
            Ensures file is a valid file before adding.
            Raises FileNotFoundError if base_file is non-existent,
            and ValueError if file is base_file a file'''
        if not path.exists( submission_path := self._resolve_file( submission_file ) ):
            raise FileNotFoundError( submission_file )
        if not path.isfile( submission_path ):
            raise ValueError( f'{submission_file} is not a file' )

        self.__base_files.append( submission_path )
        return self

    def base_files( self ) -> Iterator[ PathType ]:
        return iter( self.__base_files )

    def submission_files( self ) -> Iterator[ PathType ]:
        return iter( self.__submission_files )


class GlobBasedParams( MossParams ):

    def __init__( self, user_id ) -> None:
        super().__init__( user_id )
        self.__base_files: list[ str ] = []
        self.__submission_files: list[ str ] = []

    def add_base_file( self, base_file: str ):
        self.__base_files.append( self._expand_file( base_file ) )
        return self

    def add_submission_file( self, submission_file: str ):
        self.__submission_files.append( self._expand_file( submission_file ) )
        return self

    def base_files( self ) -> Iterator[ PathType ]:
        return filter(
            path.isfile, chain( *( ( iglob( sub_glob, recursive=True ) for sub_glob in self.__base_files ) ) )
        )

    def submission_files( self ) -> Iterator[ PathType ]:
        return filter(
            path.isfile, chain( *( ( iglob( sub_glob, recursive=True ) for sub_glob in self.__submission_files ) ) )
        )


if __name__ == '__main__':
    test_params_full = PathBasedParams(12345)           \
        .set_comment('test sample')                     \
        .set_language(MossLanguage.PYTHON)              \
        .set_experimental(True)                         \
        .add_base_file( '../../README.md' )             \
        .add_base_file( '../../LICENSE' )               \
        .add_submission_file('./config.py')             \
        .add_submission_file('~/.bash_history')

    print( test_params_full )


    test_params_glob = GlobBasedParams(12345)            \
        .set_comment('test sample glob')            \
        .set_language(MossLanguage.JAVA)            \
        .set_experimental(True)                     \
        .add_base_file( '~/../ian/Desktop/*.pdf' )            \
        .add_submission_file('~/Desktop/*.pdf')

    print( repr( test_params_glob ) )
