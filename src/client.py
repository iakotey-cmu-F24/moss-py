
from dataclasses import InitVar, dataclass, field
from socket import socket, AF_INET, SOCK_STREAM
from config import MossConfig
from os import path


@dataclass( init=True )
class MossClient:

    config: MossConfig = field( init=False, repr=True )
    _user_id: InitVar[ str ] = field( init=True, repr=False )
    _socket: socket = field(
        init=False, repr=False, default_factory=lambda: socket( family=AF_INET, type=SOCK_STREAM )
    )

    # A variable that is only used in the `__post_init__` method.

    def __post_init__( self, _user_id ):
        """
        The function takes a user_id as an argument, and then creates a MossConfig object with that
        user_id.
        It also attempts to connect to the server.
        
        Args:
          _user_id: The user ID of the user who is submitting the files.
        """
        self.config = MossConfig( _user_id )
        self._socket.connect( (self.config.server, self.config.port) )

    def _send_file( self, filename: str, file_index: int ):
        with open( filename, mode="rb" ) as f:
            contents = f.read()
            self._socket.sendall( f"file {file_index} {self.config.language} {len(contents)} {filename}".encode() )

            self._socket.sendall( contents )

    def _send_headers( self ):
        self._socket.sendall( f"moss {self.config.user_id}\n".encode() )
        self._socket.sendall( f"directory {1 if self.config.use_directory_mode else 0}\n".encode() )
        self._socket.sendall( f"X {1 if self.config.use_experimental_mode else 0}\n".encode() )
        self._socket.sendall( f"maxmatches {self.config.max_ignore_threshold}\n".encode() )
        self._socket.sendall( f"show {self.config.max_matches_displayed}\n".encode() )

        self._socket.sendall( f"language {self.config.language}\n".encode() )

        response = self._socket.recv(512) # * 512 bytes chosen arbitrarily
        
        if response.decode().strip().lower() == "no":
            raise ValueError(f"Unsupported language: {self.config.language}")

    def __enter__( self ):
        return self

    def __exit__( self, exc_type, exc_value, exc_traceback ):
        self._socket.close()


if __name__ == '__main__':
    test_client = MossClient( '12345' )
    print( test_client )
