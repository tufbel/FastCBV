# -*- coding: utf-8 -*-
# @Time    : 2021/11/23 16:10
# @Author  : Tuffy
# @Description :

from pydantic import Field, validator, BaseModel
from tortoise.contrib.pydantic import pydantic_model_creator

from .models import *


class UserPydantic(pydantic_model_creator(User, name="UserPydantic", exclude=("password",))):
    pass


class UserCreatePydantic(pydantic_model_creator(User, name="UserCreatePydantic", exclude=("uid", "company_id"), exclude_readonly=True)):
    password_again: str = Field(...)

    @validator("password_again")
    def password_again_validator(cls, password_again, values, **kwargs):
        if password_again != values["password"]:
            raise ValueError("Inconsistent passwords")
        return password_again

    class Config:
        title = "UserCreatePydantic"


class UserUpdatePydantic(pydantic_model_creator(User, name="UserUpdatePydantic", exclude=("uid", "company_id"), exclude_readonly=True)):
    username: str = None
    password: str = None
    password_again: str = Field(None)

    @validator("password")
    def password_validator(cls, password, values, **kwargs):
        if not password:
            raise ValueError("The password cannot be empty")
        return password

    @validator("password_again", always=True)
    def password_again_validator(cls, password_again, values, **kwargs):
        if "password" in values and password_again != values["password"]:
            raise ValueError("Inconsistent passwords")
        return password_again


class CompanyPydantic(pydantic_model_creator(Company, name="CompanyPydantic")):
    pass


class CompanyCreatePydantic(pydantic_model_creator(Company, name="CompanyCreatePydantic", exclude=("id",), exclude_readonly=True)):
    pass


class CompanyUpdatePydantic(pydantic_model_creator(Company, name="CompanyUpdatePydantic", exclude=("id",), exclude_readonly=True)):
    name: str = None


class CompanyAddUsersPydantic(BaseModel):
    uid: str = Field(...)
    position_id: int = Field(...)


class PositionPydantic(pydantic_model_creator(Position, name="PositionPydantic")):
    pass


class PositionCreatePydantic(pydantic_model_creator(Position, name="PositionCreatePydantic", exclude=("id", "lower"), exclude_readonly=True)):
    pass


class PositionUpdatePydantic(pydantic_model_creator(Position, name="PositionUpdatePydantic", exclude=("id", "lower", "company"), exclude_readonly=True)):
    pass
