# -*- coding: utf-8 -*-
# @Time    : 2021/11/23 16:00
# @Author  : Tuffy
# @Description :

from tortoise import fields, models

from src.my_tools.regex_tools import chinese_regex
from . import app_name


class User(models.Model):
    """
    用户
    """

    user_number = fields.IntField(pk=True)
    uid = fields.CharField(max_length=10)
    username = fields.CharField(max_length=32)
    password = fields.CharField(max_length=64)

    name = fields.CharField(max_length=32, null=True)
    family_name = fields.CharField(max_length=32, null=True)

    created_at = fields.DatetimeField(auto_now_add=True)
    modified_at = fields.DatetimeField(auto_now=True)

    company = fields.ForeignKeyField("user_model.Company", null=True, related_name="users")

    def full_name(self) -> str:
        """
        用户全名
        """
        if self.name or self.family_name:
            if chinese_regex.search(f"{self.name}") or chinese_regex.search(f"{self.family_name}"):
                return f"{self.family_name or ''}{self.name or ''}".strip()
            return f"{self.name or ''} {self.family_name or ''}".strip()
        return self.username

    class PydanticMeta(object):
        computed = ("full_name",)
        exclude = ("user_number", "created_at", "modified_at")

        allow_cycles = True
        max_recursion = 1

    class Meta(object):
        table = f"{app_name}_user"


class Position(models.Model):
    name = fields.CharField(max_length=32)
    company = fields.ForeignKeyField("user_model.Company", related_name="positions")

    higher = fields.ForeignKeyField(
        "user_model.Position",
        null=True,
        related_name="lower",
        on_delete="SET NULL",
    )
    lower: fields.ReverseRelation["Position"]

    class PydanticMeta(object):
        allow_cycles = True
        max_recursion = 1

    class Meta(object):
        table = f"{app_name}_position"


class Company(models.Model):
    """
    公司
    """
    name = fields.CharField(max_length=32)
    acronym = fields.CharField(max_length=12)

    users: fields.ReverseRelation["User"]

    class PydanticMeta(object):
        allow_cycles = True
        max_recursion = 1

    class Meta(object):
        table = f"{app_name}_company"
