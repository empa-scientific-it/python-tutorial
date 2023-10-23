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


def reference_print_odd(num: int) -> None:
    for i in range(num):
        if i % 2 != 0:
            print(i)


@pytest.mark.parametrize("num", [1, 2, 3, 4, 5])
def test_print_odd(function_to_test, num: int):
    with StringIO() as solution_stdout, StringIO() as reference_stdout:
        with contextlib.redirect_stdout(solution_stdout):
            function_to_test(num)

        with contextlib.redirect_stdout(reference_stdout):
            reference_print_odd(num)

        assert reference_stdout.getvalue() == solution_stdout.getvalue()


def reference_find_all_files(f: pl.Path) -> List[pl.Path]:
    return list(f.parent.iterdir())


def test_find_all_files(function_to_test):
    f = pl.Path("data/")
    assert function_to_test(f) == reference_find_all_files(f)


def reference_count_dirs(path: pl.Path) -> int:
    return len([obj for obj in path.glob("*") if obj.is_dir()])


def test_count_dirs(function_to_test):
    path = pl.Path.cwd()
    assert function_to_test(path) == reference_count_dirs(path)


def reference_read_file(file: pl.Path) -> List[str]:
    with file.open("r") as lines:
        return list(lines.readlines())


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

    if not tmp_user.exists():
        pytest.fail("Cannot read from inexistent file.")

    assert tmp_user.read_text() == tmp_test.read_text()


def reference_read_write_file(input_file: pl.Path, output_file: pl.Path) -> None:
    with input_file.open("r") as read_file, output_file.open("w") as write_file:
        for line in read_file.readlines():
            write_file.write("{}, {}\n".format(line.strip("\n\r"), len(line)))


def test_read_write_file(function_to_test, tmp_path: pl.Path):
    input_file = get_data("lines.txt")
    output_file = tmp_path / "output_file.txt"
    test_output_file = tmp_path / "test_output_file.txt"

    function_to_test(input_file, output_file)
    reference_read_write_file(input_file, test_output_file)

    assert output_file.read_text() == test_output_file.read_text()


def reference_exercise1(file: pl.Path) -> Dict[str, List[str]]:
    with file.open("r") as lines:
        reader = csv.reader(lines)
        headers = next(reader)
        return {
            k.strip(): list(v) for k, v in zip(headers, itertools.zip_longest(*reader))
        }


def test_exercise1(function_to_test):
    f = get_data("example.csv")
    assert function_to_test(f) == reference_exercise1(f)


def reference_exercise2(file: pl.Path) -> int:
    with file.open("r") as lines:
        return len(
            list(
                itertools.chain.from_iterable(
                    [line.split() for line in lines.readlines()]
                )
            )
        )


def test_exercise2(function_to_test):
    f = get_data("lines.txt")
    assert function_to_test(f) == reference_exercise2(f)


def reference_exercise3(file: pl.Path) -> Dict[str, int]:
    with file.open("r") as lines:
        res = sorted(
            line
            for line in itertools.chain.from_iterable(lines.readlines())
            if line.isalpha()
        )
    return Counter(res)


def test_exercise3(function_to_test):
    f = get_data("lines.txt")
    assert function_to_test(f) == reference_exercise3(f)


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
