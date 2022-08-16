from dataclasses import InitVar, dataclass, field
from socket import socket, AF_INET, SOCK_STREAM
from config import MossConfig
from os import path


@dataclass( init=True )
class MossClient:

    config: MossConfig = field( init=False, repr=True )
    _user_id: InitVar[ str ] = field(
        init=True, repr=False
    )               # A variable that is only used in the `__post_init__` method.
    _socket: socket = field(
        init=False, repr=False, default_factory=lambda: socket( family=AF_INET, type=SOCK_STREAM )
    )



    def __post_init__( self, _user_id ):
        """
        The function takes a user_id as an argument, and then creates a MossConfig object with that
        user_id.
        It also attempts to connect to the server.
        
        Args:
          _user_id: The user ID of the user who is submitting the files.
        """
        self.config = MossConfig( _user_id )
        self._socket.connect( ( self.config.server, self.config.port ) )

    def send( self ) -> str:
        """
        It sends the headers, uploads the base files,
        uploads the submission files, queries the server,
        and then reads the server response string
        
        Returns:
          The response from the server.
        """
        self._send_headers()
        self._upload_base_files()
        self._upload_submission_files()
        self._query_server()
        return self._read_server_response_str()

    @classmethod
    def from_config( cls, config: MossConfig ):
        self = cls( config.user_id )
        self.config = config
        return self

    def _send_file( self, filename: str, file_index: int ):
        """
        It sends a file to the server
        
        Args:
          filename (str): str - The name of the file to send
          file_index (int): The index of the file in the list of files to be sent.
        """
        with open( filename, mode="rb" ) as f:
            contents = f.read()
            self._socket.sendall( f"file {file_index} {self.config.language} {len(contents)} {filename}".encode() )

            self._socket.sendall( contents )

    def _send_headers( self ):
        """
        The function sends the headers to the server.
        Headers include:
        1. user id (needed for authentication),
        2. directory flag,
        3. experimental flag,
        4. number of matches to ignore,
        5. number of results to show,
        6. language,

        Raises:
            ValueError if language is unsupported
        """

        self._socket.sendall( f"moss {self.config.user_id}\n".encode() )
        self._socket.sendall( f"directory {1 if self.config.use_directory_mode else 0}\n".encode() )
        self._socket.sendall( f"X {1 if self.config.use_experimental_mode else 0}\n".encode() )
        self._socket.sendall( f"maxmatches {self.config.max_ignore_threshold}\n".encode() )
        self._socket.sendall( f"show {self.config.max_matches_displayed}\n".encode() )

        self._socket.sendall( f"language {self.config.language}\n".encode() )

        if self._read_server_response_str().lower() == "no":
            raise ValueError( f"Unsupported language: {self.config.language}" )

    def _upload_base_files( self ):
        """
        Upload the base files to the remote server.
        """
        for file in self.config.base_files():
            self._send_file( file, 0 )

    def _upload_submission_files( self ):
        """
        Upload the submission files to the server.
        """
        for index, file in enumerate( self.config.submission_files(), start=1 ):
            self._send_file( file, index )

    def _read_server_response_str(self, buf_size: int = 1024) -> str: # 1 Kb ought to be enough, right?
        """
        Reads the server's response and returns it as a string.
        
        Args:
          buf_size (int): int = 1024. Defaults to 1024
        
        Returns:
          The response from the server.
        """
        return self._socket.recv( buf_size ).decode().strip()

    def _query_server(self):
        """
        Send a query to the server.
        """
        self._socket.sendall( f"query 0 {self.config.comment}\n".encode() )


    def __enter__( self ):
        return self

    def __exit__( self, exc_type, exc_value, exc_traceback ):
        self._socket.close()

    def __del__( self ):
        self._socket.close()


if __name__ == '__main__':
    test_client = MossClient( '12345' )
    print( test_client )
