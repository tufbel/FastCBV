# -*- coding: utf-8 -*-
# @Time    : 2021/11/23 16:16
# @Author  : Tuffy
# @Description :
from typing import List

import arrow
from fastapi import APIRouter, Depends
from fastapi.responses import ORJSONResponse
from starlette import status
from tortoise.contrib.fastapi import HTTPNotFoundError

from fast_cbv import BaseViewSet, Action
from .pydantics import *

user_routers = APIRouter(prefix=f"/{app_name}")


class UserViewSet(BaseViewSet):

    @Action("", methods=["POST"], response_model=UserPydantic)
    async def create(self, user: UserCreatePydantic):
        create_dict_ = user.dict(exclude={"password_again"})
        create_dict_["password"] = make_password(user.password)
        # 生成uid
        pre_ = arrow.now(tz=LOCAL_TIMEZONE).format("YYMM")
        suf_ = await User.filter(uid__startswith=pre_).count()
        create_dict_["uid"] = f"{pre_}{suf_ + 1:05d}"
        user_obj = await User.create(**create_dict_)
        return await UserPydantic.from_tortoise_orm(user_obj)

    @Action("/all", methods=["GET"], response_model=List[UserPydantic])
    async def all(self):
        return await UserPydantic.from_queryset(User.all())

    @Action("/{uid}", methods=["GET"], response_model=UserPydantic, responses={404: {"model": HTTPNotFoundError}})
    async def get(self, uid: str):
        return await UserPydantic.from_queryset_single(User.get(uid=uid))

    @Action("/{uid}", methods=["PATCH"], response_model=UserPydantic, responses={404: {"model": HTTPNotFoundError}})
    async def update(self, uid: str, user: UserUpdatePydantic):
        """
        修改用户信息
        """
        # 密码加密
        update_dict_ = user.dict(exclude={"password_again"}, exclude_unset=True, exclude_defaults=True)
        if "password" in update_dict_:
            update_dict_["password"] = make_password(update_dict_["password"])
        await User.filter(uid=uid).update(**update_dict_)
        return await UserPydantic.from_queryset_single(User.get(uid=uid))

    @Action("/{uid}", methods=["DELETE"], response_model=UserPydantic, responses={404: {"model": HTTPNotFoundError}})
    async def delete(self, uid: str):
        user_obj = await User.get(uid=uid)
        deleted_count_ = await User.filter(uid=uid).delete()
        return await UserPydantic.from_tortoise_orm(user_obj)


UserViewSet.register(user_routers)


class CompanyViewSet(BaseViewSet):
    model = Company
    schema = CompanyPydantic
    pk_name = "id"
    pk_type = int
    page_size = 10
    views = {
        "all": None,
        "create": CompanyCreatePydantic,
        "get": None,
        "update": CompanyUpdatePydantic,
        "delete": None,
        "filter": {
            "acronym": (None, str),
        }
    }


CompanyViewSet.register(user_routers)


class PositionViewSet(BaseViewSet):
    model = Position
    schema = PositionPydantic
    pk_name = "id"
    pk_type = int
    page_size = 10
    views = {
        "all": None,
        "create": PositionCreatePydantic,
        "get": None,
        "update": PositionUpdatePydantic,
        "delete": None,
    }


PositionViewSet.register(user_routers)


class QuerySetTestViewSet(BaseViewSet):

    @Action.get("/all_values")
    async def all_values(self):
        resp = await User.all().values("uid", "username", "created_at", "company_id")
        return resp

    @Action.get("/get_values/{uid}")
    async def get_values(self, uid: str):
        resp = await User.get(uid=uid).values("uid", "username", "created_at", "company_id")
        return resp

    @Action.get("/all_values_list")
    async def all_values_list(self):
        resp = await User.all().values_list("uid", "username", "created_at", "company_id")
        return resp

    @Action.get("/single_exists/{uid}")
    async def exists(self, uid: str):
        return await User.exists(uid=uid)

    @Action.get("/filter_exists/{uid}")
    async def filter_exists(self, uid: str):
        return await User.filter(uid=uid).exists()


QuerySetTestViewSet.register(user_routers)


class DependsTestDepends(object):
    async def get_user(self, uid: str = None):
        if uid is not None:
            return await User.get(uid=uid)


class DependsTestViewSet(BaseViewSet):

    @Action.get("/depends", response_model=UserPydantic)
    async def depends(self, user_obj: User = Depends(DependsTestDepends().get_user), company: int = None):
        if user_obj:
            return await UserPydantic.from_tortoise_orm(user_obj)
        else:
            return ORJSONResponse(status_code=status.HTTP_201_CREATED)


DependsTestViewSet.register(user_routers)
