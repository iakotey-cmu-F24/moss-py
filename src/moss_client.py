from abc import ABC, abstractmethod
from datetime import datetime
from doctest import testfile
from enum import Enum
from pathlib import Path
from typing import Iterator


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
