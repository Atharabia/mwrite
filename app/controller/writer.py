from sqlalchemy import delete as sa_delete
from sqlalchemy.exc import IntegrityError
from sqlmodel import col
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from app.database import RoleTable
from app.database import WriterRoleTable
from app.database import WriterTable
from app.database import session
from app.models.dto import WriterDTO
from app.models.dto import WriterWithRolesDTO
from app.models.enums import Role


class WriterController:
    @staticmethod
    @session
    async def get_writer(db: AsyncSession, *, email: str) -> WriterDTO | None:
        result = await db.exec(select(WriterTable)
                               .where(WriterTable.email == email))
        row = result.first()

        if row is None:
            return None

        return WriterDTO(id=row.id, email=row.email, password=row.password,
                         created_at=row.created_at, updated_at=row.updated_at)

    @staticmethod
    @session
    async def get_writer_roles(db: AsyncSession,
                               *,
                               writer_id: int) -> list[str]:
        join_condition = WriterRoleTable.role_id == RoleTable.id
        where_condition = WriterRoleTable.writer_id == writer_id

        statement = (
            select(RoleTable.name)
            .join(WriterRoleTable, join_condition)
            .where(where_condition)
        )

        result = await db.exec(statement)
        return list(result.all())

    @staticmethod
    @session
    async def get_super_admin_ids(db: AsyncSession) -> set[int]:
        statement = (
            select(WriterRoleTable.writer_id)
            .join(RoleTable, RoleTable.id == WriterRoleTable.role_id)
            .where(RoleTable.name == Role.super_admin)
        )

        result = await db.exec(statement)
        return set(result.all())

    @staticmethod
    @session
    async def list_writers(db: AsyncSession) -> list[WriterWithRolesDTO]:
        writers_result = await db.exec(select(WriterTable))
        writers = writers_result.all()

        if not writers:
            return []

        writer_ids = [w.id for w in writers]
        roles_result = await db.exec(
            select(WriterRoleTable.writer_id, RoleTable.name)
            .join(RoleTable, RoleTable.id == WriterRoleTable.role_id)
            .where(col(WriterRoleTable.writer_id).in_(writer_ids))
        )

        roles_by_writer: dict[int, list[str]] = {}
        for writer_id, role_name in roles_result.all():
            roles_by_writer.setdefault(writer_id, []).append(role_name)

        return [
            WriterWithRolesDTO(
                id=w.id,
                email=w.email,
                roles=roles_by_writer.get(w.id, []),
                created_at=w.created_at,
            )
            for w in writers
        ]

    @staticmethod
    @session
    async def create_writer(
        db: AsyncSession,
        *,
        email: str,
        hashed_password: str,
        role_names: list[str],
    ) -> WriterWithRolesDTO:
        writer = WriterTable(email=email, password=hashed_password)
        db.add(writer)

        try:
            await db.flush()
        except IntegrityError as exc:
            await db.rollback()
            raise ValueError("EMAIL_ALREADY_EXISTS") from exc

        roles_result = await db.exec(
            select(RoleTable)
            .where(col(RoleTable.name).in_(role_names))
        )

        for role in roles_result.all():
            db.add(WriterRoleTable(writer_id=writer.id, role_id=role.id))

        await db.commit()
        await db.refresh(writer)

        return WriterWithRolesDTO(id=writer.id,
                                  email=writer.email,
                                  roles=role_names,
                                  created_at=writer.created_at,
                                  )

    @staticmethod
    @session
    async def update_writer(
        db: AsyncSession,
        *,
        writer_id: int,
        email: str | None = None,
        hashed_password: str | None = None,
        role_names: list[str] | None = None,
    ) -> WriterWithRolesDTO | None:
        result = await db.exec(select(WriterTable)
                               .where(WriterTable.id == writer_id))
        writer = result.first()

        if writer is None:
            return None

        if email is not None:
            writer.email = email

        if hashed_password is not None:
            writer.password = hashed_password

        if role_names is not None:
            await db.exec(sa_delete(WriterRoleTable)
                          .where(WriterRoleTable.writer_id == writer_id))

            roles_result = await db.exec(
                select(RoleTable)
                .where(col(RoleTable.name).in_(role_names)))

            for role in roles_result.all():
                db.add(WriterRoleTable(writer_id=writer_id, role_id=role.id))

        db.add(writer)

        try:
            await db.commit()
        except IntegrityError as exc:
            await db.rollback()
            raise ValueError("EMAIL_ALREADY_EXISTS") from exc

        await db.refresh(writer)

        final_roles = role_names if role_names is not None else \
            await WriterController.get_writer_roles(writer_id=writer_id)
        return WriterWithRolesDTO(
            id=writer.id, email=writer.email,
            roles=final_roles, created_at=writer.created_at,
        )

    @staticmethod
    @session
    async def delete_writer(
        db: AsyncSession,
        *,
        writer_id: int,
    ) -> None:
        await db.exec(
            sa_delete(WriterRoleTable)
            .where(WriterRoleTable.writer_id == writer_id))

        writer = (await db.exec(
            select(WriterTable).where(WriterTable.id == writer_id)
        )).first()
        if writer:
            await db.delete(writer)

        await db.commit()
