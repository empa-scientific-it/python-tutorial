import pytest
import pathlib as pl
import csv 
import itertools 
from .testsuite import get_module_name
from .. import prepare_magic_file

def reference_solution_exercise1(f: pl.Path) -> "dict[str, list[int]]":
    with open(f) as lines:
        reader = csv.reader(lines)
        headers = next(reader)
        transposed = {k:list(v) for k,v in zip(headers, itertools.zip_longest(*(l for l in reader)))}
    return transposed


def test_exercise1(function_to_test):
    f = pl.Path("data/example.csv")
    assert function_to_test(f) == reference_solution_exercise1(f)


def reference_solution_exercise2(f: pl.Path)-> int:
    with open(f) as lines:
        return len(lines.readlines())

def test_exercise2(function_to_test):
    f = pl.Path("data/example.csv")
    assert function_to_test(f) == reference_solution_exercise2(f)


def reference_solution_exercise3(f: pl.Path) -> "dict[str, int]":
    with open(f) as lines:
        res = {k: len(list(v)) for k,v in itertools.groupby(sorted([l for l in itertools.chain(*itertools.chain(lines.readlines())) if l.isalpha()]))}
    return res

def test_exercise3(function_to_test):
    f = pl.Path("data/lines.txt")
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
    words = pl.Path("data/english.csv")
    dictionary = pl.Path("data/dict.csv")
    assert function_to_test(words, dictionary) == reference_solution_exercise4(words, dictionary)


def reference_solution_exercise5(secret_file: pl.Path) -> str:
    return prepare_magic_file.decode_secret_message(secret_file)


def test_exercise5(function_to_test):
    message = pl.Path("data/secret_message.dat")
    assert function_to_test(message) == reference_solution_exercise5(message)

