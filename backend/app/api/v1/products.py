"""
产品API路由
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, or_, delete
from app.core.database import get_db
from app.models import User, Product
from app.schemas import (
    ProductCreate,
    ProductUpdate,
    ProductResponse,
    ProductListResponse,
    BatchDeleteRequest,
    Response,
)
from app.dependencies.auth import get_current_user, require_operator
from typing import Optional

router = APIRouter(prefix="/api/v1/products", tags=["产品管理"])


@router.get("", response_model=Response[ProductListResponse])
async def get_products(
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(10, ge=1, le=100, description="每页数量"),
    keyword: Optional[str] = Query(None, description="搜索关键词"),
    category: Optional[str] = Query(None, description="产品分类"),
    status: Optional[str] = Query(None, description="产品状态"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """获取产品列表"""
    # 构建查询
    query = select(Product)

    # 搜索关键词
    if keyword:
        query = query.where(
            or_(
                Product.name.contains(keyword),
                Product.description.contains(keyword),
            )
        )

    # 分类筛选
    if category:
        query = query.where(Product.category == category)

    # 状态筛选
    if status:
        query = query.where(Product.status == status)

    # 权限过滤（非管理员只能看自己的）
    if current_user.role.value != "admin":
        query = query.where(Product.created_by == current_user.id)

    # 获取总数
    count_query = select(func.count()).select_from(query.subquery())
    total_result = await db.execute(count_query)
    total = total_result.scalar()

    # 分页
    query = query.offset((page - 1) * page_size).limit(page_size)
    query = query.order_by(Product.created_at.desc())

    # 执行查询
    result = await db.execute(query)
    products = result.scalars().all()

    return Response(
        code=0,
        data=ProductListResponse(
            items=[ProductResponse.model_validate(p) for p in products],
            total=total,
            page=page,
            page_size=page_size,
        ),
    )


@router.post("", response_model=Response[ProductResponse])
async def create_product(
    request: ProductCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_operator),
):
    """创建产品"""
    product = Product(
        name=request.name,
        category=request.category,
        price=request.price,
        platform=request.platform,
        description=request.description,
        created_by=current_user.id,
    )

    db.add(product)
    await db.commit()
    await db.refresh(product)

    return Response(
        code=0,
        message="创建成功",
        data=ProductResponse.model_validate(product),
    )


@router.get("/{product_id}", response_model=Response[ProductResponse])
async def get_product(
    product_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """获取产品详情"""
    result = await db.execute(select(Product).where(Product.id == product_id))
    product = result.scalar_one_or_none()

    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="产品不存在",
        )

    # 权限检查（非管理员只能看自己的）
    if current_user.role.value != "admin" and product.created_by != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="无权访问此产品",
        )

    return Response(
        code=0,
        data=ProductResponse.model_validate(product),
    )


@router.put("/{product_id}", response_model=Response[ProductResponse])
async def update_product(
    product_id: int,
    request: ProductUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_operator),
):
    """更新产品"""
    result = await db.execute(select(Product).where(Product.id == product_id))
    product = result.scalar_one_or_none()

    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="产品不存在",
        )

    # 权限检查（非管理员只能修改自己的）
    if current_user.role.value != "admin" and product.created_by != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="无权修改此产品",
        )

    # 更新字段
    update_data = request.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(product, field, value)

    await db.commit()
    await db.refresh(product)

    return Response(
        code=0,
        message="更新成功",
        data=ProductResponse.model_validate(product),
    )


@router.delete("/{product_id}")
async def delete_product(
    product_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_operator),
):
    """删除产品"""
    result = await db.execute(select(Product).where(Product.id == product_id))
    product = result.scalar_one_or_none()

    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="产品不存在",
        )

    # 权限检查（非管理员只能删除自己的）
    if current_user.role.value != "admin" and product.created_by != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="无权删除此产品",
        )

    await db.delete(product)
    await db.commit()

    return Response(
        code=0,
        message="删除成功",
    )


@router.post("/batch-delete")
async def batch_delete_products(
    request: BatchDeleteRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_operator),
):
    """批量删除产品"""
    # 查询要删除的产品
    result = await db.execute(
        select(Product).where(Product.id.in_(request.ids))
    )
    products = result.scalars().all()

    if not products:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="未找到要删除的产品",
        )

    # 权限检查（非管理员只能删除自己的）
    if current_user.role.value != "admin":
        for product in products:
            if product.created_by != current_user.id:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"无权删除产品: {product.name}",
                )

    # 批量删除
    await db.execute(
        delete(Product).where(Product.id.in_(request.ids))
    )
    await db.commit()

    return Response(
        code=0,
        message=f"成功删除 {len(products)} 个产品",
    )
