from enum import Enum


class TeamMemberType(Enum):
    OWNER = 0
    MEMBER = 1

    @staticmethod
    def get_value(name):
        for status in TeamMemberType:
            if status.name == name:
                return status.value

    @staticmethod
    def get_name(value):
        for status in TeamMemberType:
            if status.value == value:
                return status.name


class JsonAccessMapType(Enum):
    OWNER = 0
    WRITE = 1
    READ = 2

    @staticmethod
    def get_value(name):
        for status in JsonAccessMapType:
            if status.name == name:
                return status.value

    @staticmethod
    def get_name(value):
        for status in JsonAccessMapType:
            if status.value == value:
                return status.name
