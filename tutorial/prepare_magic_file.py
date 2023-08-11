import random


def prepare_secret_file(
    file_path, secret_message, encoding="utf-8", random_data_length=10
):
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
    random_data = bytes(random.sample(range(256), random_data_length))

    # Generate the binary data for the file
    start_marker = b"\xff\xee\xdd\xcc\xbb\xaa"
    end_marker = b"\xaa\xbb\xcc\xdd\xee\xff"
    binary_data = (
        random_data + start_marker + encoded_message + end_marker + random_data
    )

    # Write the binary data to the file
    with open(file_path, "wb") as f:
        f.write(binary_data)


def decode_secret_message(
    file_path,
    encoding="utf-8",
    start_marker=b"\xff\xee\xdd\xcc\xbb\xaa",
    end_marker=b"\xaa\xbb\xcc\xdd\xee\xff",
):
    """
    Decode the secret message from a binary file.

    Parameters:
    file_path (str): The path to the binary file to read.
    encoding (str): The encoding to use for the decoded message (default is 'utf-8').
    start_marker (bytes): The byte sequence that marks the beginning of the secret message (default is b'\xff\xee\xdd\xcc\xbb\xaa').
    end_marker (bytes): The byte sequence that marks the end of the secret message (default is b'\xaa\xbb\xcc\xdd\xee\xff').

    Returns:
    str: The decoded secret message.
    """
    # Read the binary data from the file
    with open(file_path, "rb") as f:
        binary_data = f.read()

    # Find the start and end positions of the secret message
    start_pos = binary_data.find(start_marker) + len(start_marker)
    end_pos = binary_data.find(end_marker, start_pos)

    # Decode the secret message
    decoded_message = binary_data[start_pos:end_pos].decode(encoding)

    return decoded_message
