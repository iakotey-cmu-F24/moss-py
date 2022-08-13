from abc import ABC, abstractmethod
from datetime import datetime
from doctest import testfile
from enum import Enum
from pathlib import Path
from typing import Iterator

# ! Unnecessary once Python 3.11 is released
# ? `pip install typing-extensions` for now
from typing_extensions import Self


PathType = Path | str


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


class MossParams( ABC ):

    ''' Abstract class representing a moss parameter. 
        Allows the user to configure Moss parameters and submit queries
        Implements most shared behavior expected of subclasses
    '''

    def __init__( self ) -> None:
        super().__init__()
        self.__comment: str = str( datetime.today() )
        self.__experimental_mode: bool = False
        self.__language: MossLanguage = MossLanguage.C
        self.__max_ignore_threshold = 10
        self.__match_number = 250

    def set_language( self, language: MossLanguage ) -> Self:
        '''Set the language (-l) parameter to be used in the MOSS query'''
        self.__language = language
        return self

    def set_experimental( self, experimental_flag: bool ) -> Self:
        '''Set the experimental flag (-x)'''
        self.__experimental_mode = experimental_flag
        return self

    def set_comment( self, comment: str ) -> Self:
        '''Set the comment (-c) string to be used in the MOSS query'''
        self.__comment = comment
        return self

    def __str__( self ):
        return f'moss -c {self.__comment} -l {self.__language}'                 \
               f' -m {self.__max_ignore_threshold} -n {self.__match_number}'    \
               f'{" -x" if self.__experimental_mode else ""}'                                    \
               f' {" ".join(("-b " + str(file) for file in self.base_files()))}'        \
               f' {" ".join((str(file) for file in self.submission_files()))}'

    @abstractmethod
    def base_files( self ) -> Iterator[ PathType ]:
        pass

    @abstractmethod
    def submission_files( self ) -> Iterator[ PathType ]:
        pass


class PathBasedParams( MossParams ):

    ''' Implementation of moss parameters that uses file paths
        This implementation tries to ensure the validity
        of file paths passed
    '''

    def __init__( self ) -> None:
        super().__init__()
        self.__base_files: list[ PathType ] = []
        self.__submission_files: list[ PathType ] = []

    def add_base_file( self, base_file: PathType ):
        if Path( base_file ).exists():
            self.__base_files.append( base_file )
        else:
            raise FileNotFoundError( base_file )
        return self

    def add_submission_file( self, submission_file: PathType ):
        if Path( submission_file ).exists():
            self.__submission_files.append( submission_file )
        else:
            raise FileNotFoundError( submission_file )
        return self

    def base_files( self ) -> Iterator[ PathType ]:
        return iter( self.__base_files )

    def submission_files( self ) -> Iterator[ PathType ]:
        return iter( self.__submission_files )


if __name__ == '__main__':
    test_params_full = PathBasedParams()            \
        .set_comment('test sample')                 \
        .set_language(MossLanguage.PYTHON)          \
        .set_experimental(True)                     \
        .add_base_file( '../README.md' )            \
        .add_submission_file('./moss_client.py')

    print( test_params_full )
