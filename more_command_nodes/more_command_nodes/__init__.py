import re
from enum import Enum
from typing import Type, Union, Iterable

from mcdreforged.api.command import *
from mcdreforged.command.builder import command_builder_util

__all__ = [
    'FloatsArgument',
    'Position',
    'Facing',
    'EnumeratedText'
]


class IllegalFloat(CommandSyntaxError):
    def __init__(self, char_read: str):
        super().__init__('Invalid Float', char_read)


class IncompleteFloat(CommandSyntaxError):
    def __init__(self, char_read: str):
        super().__init__('Incomplete Float', char_read)


class FloatsArgument(ArgumentNode):
    """
    An argument with custom continuous floats.
    """

    def __init__(self, name: str, number: int):
        super().__init__(name)
        self.__number = number

    def parse(self, text: str) -> ParseResult:
        try:
            # Parse arguments
            split_text = re.split(' ', text)
            char_read = -1
            args = []
            for i in split_text:
                if i == '':
                    char_read += 1
                else:
                    args.append(i)
                    char_read += len(i) + 1
                    if len(args) == self.__number:
                        break

            # Convert to float
            if len(args) < self.__number:
                raise IncompleteFloat(text)
            else:
                coords = list(map(float, args))
        except ValueError:
            raise IllegalFloat(text)
        else:
            return ParseResult(coords, char_read)


class Position(FloatsArgument):
    """
    A position argument, it has three continues floats.
    """

    def __init__(self, name: str):
        super().__init__(name, 3)


class Facing(FloatsArgument):
    """
    A facing argument, it has two continues floats.
    """

    def __init__(self, name: str):
        super().__init__(name, 2)


class InvalidEnumeratedText(IllegalArgument):
    def __init__(self, char_read: Union[int, str]):
        super().__init__('Invalid enumerated text', char_read)


class EnumeratedText(ArgumentNode):
    """
    Same as MCDR's Enumeration,
    but it uses Enum's value as argument text instead of key.
    """

    def __init__(self, name: str, enum_class: Type[Enum]):
        super().__init__(name)
        self.__enum_class: Type[Enum] = enum_class

    def _get_suggestions(self, context: CommandContext) -> Iterable[str]:
        return map(lambda e: e.value, self.__enum_class)

    def parse(self, text: str) -> ParseResult:
        arg = command_builder_util.get_element(text)
        try:
            enum = self.__enum_class(arg)
        except ValueError:
            raise InvalidEnumeratedText(arg) from None
        else:
            return ParseResult(enum, len(arg))
