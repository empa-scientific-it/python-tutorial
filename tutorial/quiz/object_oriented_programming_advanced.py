from .common import Question, Quiz


class OopAdvancedInheritance(Quiz):
    def __init__(self, title=""):
        q1 = Question(
            question="Which special method is used for object initialization in Python?",
            options={
                "__init__": "Correct! The `__init__` method is called when an object is created and is used to initialize the object.",
                "__repr__": "The `__repr__` method is used to provide an unambiguous string representation of an object.",
                "__eq__": "The `__eq__` method is used to define equality comparison between objects.",
            },
            correct_answer="__init__",
            hint="This method is automatically called when an object is instantiated.",
            shuffle=True,
        )

        q2 = Question(
            question="What is the term for a class that inherits from another class?",
            options={
                "Base class": "A base class is the class being inherited from, not the one inheriting.",
                "Derived class": "Correct! A derived class is a class that inherits from another class.",
            },
            correct_answer="Derived class",
            hint="This class extends the functionality of another class.",
            shuffle=True,
        )

        q3 = Question(
            question="What is the purpose of the `super()` function in Python?",
            options={
                "To call a method from the parent class": "Correct! `super()` is used to call a method from the parent class.",
                "To create a derived class": "Incorrect. `super()` is not used for creating derived classes.",
                "To initialize an object": "Incorrect. Object initialization is done using the `__init__` method.",
            },
            correct_answer="To call a method from the parent class",
            hint="This function is used to access inherited methods.",
            shuffle=True,
        )

        q4 = Question(
            question="What is composition in OOP?",
            options={
                "A way to build complex objects by combining simpler ones": "Correct! Composition involves including instances of other classes as attributes.",
                "A way to inherit methods from a base class": "Incorrect. This describes inheritance, not composition.",
                "A way to inherit methods from more than one class": "Incorrect. This describes multiple inheritance, not composition.",
            },
            correct_answer="A way to build complex objects by combining simpler ones",
            hint="Think about combining objects rather than inheriting from them.",
            shuffle=True,
        )

        super().__init__(questions=[q1, q2, q3, q4])


class OopAdvancedAbstractClasses(Quiz):
    def __init__(self, title=""):
        q1 = Question(
            question="Which module in Python is used to create abstract classes?",
            options={
                "abc": "Correct! The `abc` module provides the infrastructure for defining abstract base classes.",
                "abstract": "There is no module named `abstract` in Python.",
                "abstractmodule": "There is no module named `abstractmodule` in Python.",
            },
            correct_answer="abc",
            hint="This module's name is an abbreviation for 'Abstract Base Classes'.",
            shuffle=True,
        )

        q2 = Question(
            question="What is the purpose of an abstract class?",
            options={
                "To define methods that must be implemented by subclasses": "Correct! Abstract classes define methods that must be implemented by concrete subclasses.",
                "To create a class that cannot have methods": "Incorrect. Abstract classes can have methods.",
                "To create a class that cannot have attributes": "Incorrect. Abstract classes can have attributes.",
                "To create a class that cannot be inherited": "Incorrect. Abstract classes are designed to be inherited.",
            },
            correct_answer="To define methods that must be implemented by subclasses",
            hint="Abstract classes act as blueprints for other classes.",
            shuffle=True,
        )

        q3 = Question(
            question="True or False: You can instantiate an abstract class directly.",
            options={
                "True": "Incorrect. Abstract classes cannot be instantiated directly.",
                "False": "Correct! Abstract classes are meant to be subclassed and cannot be instantiated directly.",
            },
            correct_answer="False",
            hint="Abstract classes are designed to be extended by concrete subclasses.",
            shuffle=True,
        )

        super().__init__(questions=[q1, q2, q3])


class OopAdvancedDecorators(Quiz):
    def __init__(self, title=""):
        q1 = Question(
            question="Which decorator is used to define a method that belongs to the class rather than an instance?",
            options={
                "@staticmethod": "Incorrect. A static method does not belong to the class or instance.",
                "@classmethod": "Correct! A class method belongs to the class and takes `cls` as its first parameter.",
                "@property": "Incorrect. The `@property` decorator is used to define getter methods.",
                "@abstractmethod": "Incorrect. The `@abstractmethod` decorator is used in abstract classes.",
            },
            correct_answer="@classmethod",
            hint="This method takes `cls` as its first parameter.",
            shuffle=True,
        )

        q2 = Question(
            question="What is the purpose of the `@property` decorator?",
            options={
                "To define a computed attribute": "Correct! The `@property` decorator is used to define computed attributes.",
                "To define a static method": "Incorrect. Static methods are defined using the `@staticmethod` decorator.",
                "To define a class method": "Incorrect. Class methods are defined using the `@classmethod` decorator.",
                "To define an abstract method": "Incorrect. Abstract methods are defined using the `@abstractmethod` decorator.",
            },
            correct_answer="To define a computed attribute",
            hint="This decorator allows you to define methods that can be accessed like attributes.",
            shuffle=True,
        )

        q3 = Question(
            question="Which decorator is used to define a method that does not access the class or instance?",
            options={
                "@staticmethod": "Correct! A static method does not access the class or instance.",
                "@classmethod": "Incorrect. A class method accesses the class using `cls`.",
                "@property": "Incorrect. The `@property` decorator is used to define getter methods.",
                "@abstractmethod": "Incorrect. The `@abstractmethod` decorator is used in abstract classes.",
            },
            correct_answer="@staticmethod",
            hint="This method is often used for utility functions.",
            shuffle=True,
        )

        q4 = Question(
            question="A method with which decorator takes `cls` as its first parameter?",
            options={
                "@classmethod": "Correct! A class method is bound to a class rather than its instances and the parameter `cls` represents the class itself.",
                "@staticmethod": "A static method does not have access to `cls` or `self` and cannot modify the class state.",
                "@abstractmethod": "This decorator defines a method in an abstract class that **must** be implemented by all its concrete subclasses.",
            },
            correct_answer="@classmethod",
            hint="",
            shuffle=True,
        )

        q5 = Question(
            question="What is the purpose of the `@classmethod` decorator?",
            options={
                "To define a method that belongs to the class rather than an instance": "Correct! A class method belongs to the class and takes `cls` as its first parameter.",
                "To define a method that does not access the class or instance": "Incorrect. This describes a static method.",
                "To define a computed attribute": "Incorrect. Computed attributes are defined using the `@property` decorator.",
                "To define an abstract method": "Incorrect. Abstract methods are defined using the `@abstractmethod` decorator.",
            },
            correct_answer="To define a method that belongs to the class rather than an instance",
            hint="This method takes `cls` as its first parameter.",
            shuffle=True,
        )

        q6 = Question(
            question="What is the difference between `@staticmethod` and `@classmethod`?",
            options={
                "`@staticmethod` does not access the class or instance, while `@classmethod` takes `cls` as its first parameter": "Correct! This is the key difference between the two decorators.",
                "`@staticmethod` is used for utility functions, while `@classmethod` is used for abstract methods": "Incorrect. Abstract methods are unrelated to these decorators.",
                "`@staticmethod` is faster than `@classmethod`": "Incorrect. Performance is not the defining difference.",
                "`@staticmethod` is used for computed attributes, while `@classmethod` is used for class-level attributes": "Incorrect. Computed attributes are defined using `@property`.",
            },
            correct_answer="`@staticmethod` does not access the class or instance, while `@classmethod` takes `cls` as its first parameter",
            hint="Think about the parameters each decorator uses.",
            shuffle=True,
        )

        super().__init__(questions=[q1, q2, q3, q4, q5, q6])


class OopAdvancedEncapsulation(Quiz):
    def __init__(self, title=""):
        q1 = Question(
            question="Which naming convention is used to indicate a private attribute in Python?",
            options={
                "_attribute": "Incorrect. A single underscore indicates a protected attribute.",
                "__attribute": "Correct! A double underscore indicates a private attribute.",
                "attribute_": "Incorrect. This is not a convention for private attributes.",
                "__attribute__": "Incorrect. Double underscores at both ends are used for special methods.",
            },
            correct_answer="__attribute",
            hint="Private attributes use double underscores.",
            shuffle=True,
        )

        q2 = Question(
            question="Even though it's not recommended, which type of attributes and methods can be accessed using name mangling in Python?",
            options={
                "public": "All public attributes and methods can be accessed from anywhere, by default.",
                "private": "Correct! Even though private attributes and methods should not be directly accessed from outside the class, Python allows for name mangling.",
                "protected": "Protected attibutes and methods should not be accessed directly from outside the class, but there's no strict enforcement.",
            },
            correct_answer="private",
            hint="",
            shuffle=True,
        )

        q3 = Question(
            question="What is the purpose of encapsulation in OOP?",
            options={
                "To bundle data and methods into a single unit": "Correct! Encapsulation bundles data and methods into a single unit.",
                "To define abstract methods": "Incorrect. Abstract methods are defined using the `abc` module.",
                "To create a class that cannot be inherited": "Incorrect. Encapsulation does not restrict inheritance.",
                "To define static methods": "Incorrect. Static methods are defined using the `@staticmethod` decorator.",
            },
            correct_answer="To bundle data and methods into a single unit",
            hint="Encapsulation is one of the fundamental principles of OOP.",
            shuffle=True,
        )

        q4 = Question(
            question="True or False: Protected attributes can be accessed directly from outside the class.",
            options={
                "True": "Correct! Protected attributes can be accessed directly, but it is not recommended.",
                "False": "Incorrect. Protected attributes can be accessed directly, but it is not recommended.",
            },
            correct_answer="True",
            hint="Protected attributes are indicated by a single underscore.",
            shuffle=True,
        )

        super().__init__(questions=[q1, q2, q3, q4])


class OopAdvancedAttrsDataclasses(Quiz):
    def __init__(self, title=""):
        q1 = Question(
            question="What is something that `attrs` provides but `dataclasses` doesn't?",
            options={
                "__init__()": "Both packages automatically generate `__init__()`: `dataclasses` uses the `@dataclass` decorator, while `attrs` uses `@define`.",
                "__repr__()": "Both packages automatically generate `__repr__()` to help you easily print a class instance.",
                "validators": "Correct! You need to define the attribute as a `field()` and then use the validator decorator.",
            },
            correct_answer="validators",
            hint="",
            shuffle=True,
        )

        super().__init__(questions=[q1])
