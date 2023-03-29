# -*- coding: utf-8 -*-
# @Time    : 2021/12/16 9:14
# @Author  : Tuffy
# @Description :
from inspect import Parameter, signature
from typing import Dict, List, Tuple, Type

from tortoise.contrib.fastapi import HTTPNotFoundError
from tortoise.contrib.pydantic import PydanticModel
from tortoise.expressions import Q
from tortoise.models import MODEL

from .decorators import Action


def generate_all(model: Type[MODEL], schema: Type[PydanticModel]):
    """
    生成视图集的all方法
    Args:
        model: 视图集的orm模型
        schema: 视图输出的序列化

    Returns:
        CoroutineType: 由 async def 创建的协程方法
    """

    @Action.get("/all", response_model=List[schema])
    async def all(self):
        return await schema.from_queryset(model.all())

    all.__doc__ = f"Query all {model.__name__}"

    return all


def generate_create(model: Type[MODEL], schema: Type[PydanticModel], input_schema: Type[PydanticModel]):
    """
    生成视图集的create方法
    Args:
        model: 视图集的orm模型
        schema: 视图输出序列化
        input_schema: http视图输入的body序列化对象

    Returns:
        CoroutineType: 由 async def 创建的协程方法
    """

    @Action.post("", response_model=schema)
    async def create(self, body: input_schema):
        return await schema.from_tortoise_orm(await model.create(**body.dict()))

    create.__doc__ = f"Create {model.__name__}"
    return create


def generate_get(model: Type[MODEL], schema: Type[PydanticModel], pk_type: Type):
    """
    生成视图集的get方法
    Args:
        model: 视图集的orm模型
        schema: 视图输出序列化
        pk_type: 主键类型

    Returns:
        CoroutineType: 由 async def 创建的协程方法
    """

    @Action.get(f"/{{pk}}", response_model=schema, responses={404: {"model": HTTPNotFoundError}})
    async def get(self, pk: pk_type):
        return await schema.from_queryset_single(model.get(pk=pk))

    get.__doc__ = f"Get {model.__name__} by primary key"

    return get


def generate_update(model: Type[MODEL], schema: Type[PydanticModel], pk_type: Type, input_schema: Type[PydanticModel]):
    """
    生成视图集的update方法
    Args:
        model: 视图集的orm模型
        schema: 视图输出序列化
        pk_type: 主键类型
        input_schema: http视图的body序列化

    Returns:
        CoroutineType: 由 async def 创建的协程方法
    """

    @Action.patch(f"/{{pk}}", response_model=schema, responses={404: {"model": HTTPNotFoundError}})
    async def update(self, pk: pk_type, body: input_schema):
        obj: MODEL = await model.get(pk=pk)
        obj.update_from_dict(body.dict(exclude_unset=True))
        await obj.save()
        return await schema.from_tortoise_orm(obj)

    update.__doc__ = f"Update {model.__name__} by primary key"

    return update


def generate_delete(model: Type[MODEL], schema: Type[PydanticModel], pk_type: Type):
    """
    生成视图集的delete方法
    Args:
        model: 视图集的orm模型
        schema: 视图输出序列化
        pk_type: 主键类型

    Returns:
        CoroutineType: 由 async def 创建的协程方法
    """

    @Action.delete(f"/{{pk}}", response_model=schema, responses={404: {"model": HTTPNotFoundError}})
    async def delete(self, pk: pk_type):
        obj = await model.get(pk=pk)
        deleted_count_ = await obj.delete()
        return await schema.from_tortoise_orm(obj)

    delete.__doc__ = f"Delete {model.__name__} by primary key"

    return delete


def generate_filter(model: Type[MODEL], schema: Type[PydanticModel], query_params: Dict[str, Tuple]):
    """
    生成视图集的filter方法
    Args:
        model: 视图集的orm模型
        schema: 视图输出序列化
        query_params: 查询参数
            {name: (default_value, default_type)} 例如 {"type": (None, str), "age": (18, int)}
            作为key的name为作为查询条件的字段名。
            作为value的default_value默认值和default_type默认值类型

    Returns:
        CoroutineType: 由 async def 创建的协程方法
    """

    @Action.get("/filter", response_model=List[schema])
    async def filter(self, **kwargs):
        q_filter = Q()
        for name, v_ in query_params.items():
            if name in kwargs and kwargs[name] is not None:
                q_filter &= Q(**{name: kwargs[name]})
        return await schema.from_queryset(model.filter(q_filter))

    sig_params = [
        Parameter(name, Parameter.KEYWORD_ONLY, default=v_[0], annotation=v_[1])
        for name, v_ in query_params.items()
    ]
    sig_ = signature(filter)
    sig_params.insert(0, sig_.parameters["self"])
    sig_ = sig_.replace(parameters=sig_params)

    filter.__signature__ = sig_
    filter.__doc__ = f"Filter {model.__name__} that match the query"
    return filter
