import pytest
import pathlib as pl
import csv 
import itertools 
from .testsuite import get_module_name
from .. import prepare_magic_file
import sys



def get_data(name: str, data_dir:str="data") -> pl.Path:
    current_module  = sys.modules[__name__]
    return (pl.Path(current_module.__file__).parent / f"{data_dir}/{name}").resolve()

def reference_solution_find_all_files(f: pl.Path) -> "list[pl.Path]":
    return list(f.parent.glob(f.name))

def test_find_all_files(function_to_test):
    f = pl.Path("data/")
    assert function_to_test(f) == reference_solution_find_all_files(f)

def reference_solution_count_parents(f: pl.Path) -> int:
    return len([ob for ob in f.parent.glob("*") if ob.is_dir()])

def test_count_parents(function_to_test):
    f  = pl.Path(sys.modules[__name__].__file__).parent.parent
    print(f)
    assert function_to_test(f) == reference_solution_count_parents(f)

def reference_solution_read_file(f: pl.Path) -> "list[str]":
    with open(f) as lines:
        return [l for l in lines.readlines()]

def test_read_file(function_to_test):
    for fp in ["lines.txt", "example.csv"]:
        data = get_data(fp)
        assert function_to_test(data) == reference_solution_read_file(data)

def reference_solution_write_file(f: pl.Path, lines: "list[str]") -> None:
    with open(f, "w") as f:
        f.writelines(lines)

def test_write_file(function_to_test):
    lines = ["python tutorial 2023"]
    f = pl.Path("test.txt")
    function_to_test(f)
    with open(f) as input_file:
        assert input_file.readlines() == lines

def reference_solution_exercise1(f: pl.Path) -> "dict[str, list[int]]":
    with open(f) as lines:
        reader = csv.reader(lines)
        headers = next(reader)
        transposed = {k:list(v) for k,v in zip(headers, itertools.zip_longest(*(l for l in reader)))}
    return transposed


def test_exercise1(function_to_test):
    f = get_data("example.csv")
    assert function_to_test(f) == reference_solution_exercise1(f)


def reference_solution_exercise2(f: pl.Path)-> int:
    with open(f) as lines:
        return len(list(itertools.chain.from_iterable([l.split() for l in lines.readlines()])))

def test_exercise2(function_to_test):
    f = get_data("lines.txt")
    assert function_to_test(f) == reference_solution_exercise2(f)


def reference_solution_exercise3(f: pl.Path) -> "dict[str, int]":
    with open(f) as lines:
        res = {k: len(list(v)) for k,v in itertools.groupby(sorted([l for l in itertools.chain(*itertools.chain(lines.readlines())) if l.isalpha()]))}
    return res

def test_exercise3(function_to_test):
    f = get_data("lines.txt")
    assert function_to_test(f) == reference_solution_exercise3(f)


def reference_solution_exercise4(english: pl.Path, dictionary: pl.Path) -> "list[(str, str)]":
    with open(english) as english_file:
        english_reader = csv.reader(english_file)
        english_words = [w for w, *rest in english_reader]
    with open(dictionary) as dict_file:
        dict_reader = csv.reader(dict_file)
        next(dict_reader)
        translations = {en:it for index,it, en,*rest in dict_reader}
    return [(e, translations[e]) for e in english_words if e in translations.keys()]

def test_exercise4(function_to_test):
    words = get_data("english.csv")
    dictionary = get_data("dict.csv")
    assert function_to_test(words, dictionary) == reference_solution_exercise4(words, dictionary)


def reference_solution_exercise5(secret_file: pl.Path) -> str:
    return prepare_magic_file.decode_secret_message(secret_file)


def test_exercise5(function_to_test):
    message = get_data("secret_message.dat")
    assert function_to_test(message) == reference_solution_exercise5(message)

