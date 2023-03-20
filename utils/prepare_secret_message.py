import random
import pathlib as pl


def prepare_secret_file(file_path: pl.Path, secret_message: str, encoding: str ='utf-8', random_data_length:int=10):
    """
    Prepare a binary file with a secret message encoded in it.
    
    Parameters:
    file_path (str): The path to the binary file to create.
    secret_message (str): The secret message to encode in the file.
    encoding (str): The encoding to use for the secret message (default is 'utf-8').
    random_data_length (int): The length of the random data to intersperse with the secret message (default is 10).
    """
    # Encode the secret message
    encoded_message = secret_message.encode(encoding)
    
    # Generate some random data to intersperse with the secret message
    random_data = bytes(random.choices(range(256), k=random_data_length))
    
    # Generate the binary data for the file
    start_marker = b'\xff\xee\xdd\xcc\xbb\xaa'
    end_marker = b'\xaa\xbb\xcc\xdd\xee\xff'
    binary_data = random_data + start_marker + encoded_message + end_marker + random_data
    
    # Write the binary data to the file
    with open(file_path, 'wb') as f:
        f.write(binary_data)


prepare_secret_file("./data/secret_message.dat", "Congratulations, you found the secret message!", random_data_length=1000)