import contextlib
import csv
import itertools
import pathlib as pl
from collections import Counter
from io import StringIO
from typing import Dict, List, Tuple

import pytest

from tutorial.prepare_magic_file import decode_secret_message


def get_data(name: str, data_dir: str = "data") -> pl.Path:
    return (pl.Path.cwd() / f"tutorial/tests/{data_dir}/{name}").resolve()


def reference_print_odd(n: int) -> None:
    for i in range(n):
        if i % 2 != 0:
            print(i)


@pytest.mark.parametrize("n", [1, 2, 3, 4, 5])
def test_print_odd(function_to_test, n: int):
    with StringIO() as solution_stdout, StringIO() as reference_stdout:
        with contextlib.redirect_stdout(solution_stdout):
            function_to_test(n)
            solution_text = solution_stdout.getvalue()

        with contextlib.redirect_stdout(reference_stdout):
            reference_print_odd(n)
            reference_text = reference_stdout.getvalue()

    assert solution_text == reference_text


def reference_find_all_files(current_path: pl.Path) -> List[pl.Path]:
    return list(current_path.iterdir())


def test_find_all_files(function_to_test):
    f = pl.Path("data/")
    assert function_to_test(f) == reference_find_all_files(f)


def reference_count_dirs(path: pl.Path) -> int:
    return len([obj for obj in path.glob("*") if obj.is_dir()])


def test_count_dirs(function_to_test):
    path = pl.Path.cwd()
    assert function_to_test(path) == reference_count_dirs(path)


def reference_read_file(file: pl.Path) -> List[str]:
    text = file.open("r")
    lines = text.readlines()
    text.close()
    return lines


def test_read_file(function_to_test):
    for file in ["lines.txt", "example.csv"]:
        data = get_data(file)
        assert function_to_test(data) == reference_read_file(data)


def reference_write_file(file: pl.Path) -> None:
    file.write_text("python tutorial 2023")


def test_write_file(function_to_test, tmp_path: pl.Path):
    tmp_user = tmp_path / "user_write_file.txt"
    tmp_test = tmp_path / "test_write_file.txt"

    function_to_test(tmp_user)
    reference_write_file(tmp_test)

    assert (
        tmp_user.exists()
    ), """The file was not created. Make sure to create the file in the function. Hint: use `open(output_file, "w")`"""

    assert (
        tmp_user.read_text() == tmp_test.read_text()
    ), "The file content is not correct."


def reference_read_write_file(input_file: pl.Path, output_file: pl.Path) -> None:
    # We open the input and output file at the same time
    read_file = input_file.open("r")
    write_file = output_file.open("w") 
    # Here we iterate over each line of the input file
    for line in read_file.readlines():
        # We remove line breaks and write the line to the output file
        clean_line = line.strip("\n\r")
        # We crete the output line
        output_line = f"{clean_line}, {len(clean_line)}\n"
        # Finally we write the line and its length to the output file
        write_file.write(output_line)
    read_file.close()
    write_file.close()


def test_read_write_file(function_to_test, tmp_path: pl.Path):
    input_file = get_data("lines.txt")
    output_file = tmp_path / "output_file.txt"
    test_output_file = tmp_path / "test_output_file.txt"

    function_to_test(input_file, output_file)
    reference_read_write_file(input_file, test_output_file)
    assert output_file.exists(), "The output file was not created."

    assert output_file.read_text() == test_output_file.read_text()


def reference_exercise1(input_file: pl.Path) -> Dict[str, List[str]]:
    my_dict = {}
    with open(input_file) as csv_file:
        reader = csv.reader(csv_file)
        headers = next(reader)
        for line in reader:
            key, value = line
            my_dict[key] = value
    return my_dict


@pytest.mark.parametrize("file", ["example_dictionary.csv"])
def test_exercise1(function_to_test, file: str):
    f = get_data(file)
    assert function_to_test(f) == reference_exercise1(f)


def reference_exercise2(file: pl.Path) -> int:
    with open(input_file, "r") as file_ob:
        text = file_ob.read()
    return len(text.split())


@pytest.mark.parametrize("file", ["lines.txt", "lines2.txt"])
def test_exercise2(function_to_test, file: str):
    f = get_data(file)
    assert function_to_test(f) == reference_exercise2(f)


def reference_exercise3(input_file: pl.Path) -> Dict[str, int]:
    my_dict = {}
    # Initialize dictionary with all letters set to 0
    my_dict = {letter: 0 for letter in string.ascii_lowercase}
    with open(input_file, "r") as file_ob:
        text = file_ob.read()
        for char in text:
            if char in string.ascii_lowercase:
                my_dict[char.lower()] += 1
    return my_dict


def test_exercise3(function_to_test):
    f = get_data("lines.txt")
    # Clear '0' values from the dictionary
    solution_dict = {k: v for k, v in function_to_test(f).items() if v != 0}
    reference_dict = {k: v for k, v in reference_exercise3(f).items() if v != 0}
    assert solution_dict == reference_dict


def reference_exercise4(english: pl.Path, dictionary: pl.Path) -> List[Tuple[str, str]]:
    english_words = english.read_text().splitlines()

    with dictionary.open("r") as dict_file:
        dict_reader = csv.reader(dict_file)
        next(dict_reader)  # skip header
        translations = {en: it for _, it, en in dict_reader}

    return [
        (word, translations[word]) for word in english_words if word in translations
    ]


def test_exercise4(function_to_test):
    words = get_data("english.txt")
    dictionary = get_data("dict.csv")
    assert function_to_test(words, dictionary) == reference_exercise4(words, dictionary)


def reference_exercise5(secret_file: pl.Path) -> str:
    return decode_secret_message(secret_file)


def test_exercise5(function_to_test):
    message = get_data("secret_message.dat")
    assert function_to_test(message) == reference_exercise5(message)
