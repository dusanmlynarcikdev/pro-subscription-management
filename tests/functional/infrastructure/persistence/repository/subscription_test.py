from datetime import date
from uuid import UUID

from pytest import raises
from sqlalchemy.exc import IntegrityError
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from app.domain.subscription.email import Email
from app.domain.subscription.errors import SubscriptionNotFoundError
from app.domain.subscription.period import Period
from app.infrastructure.persistence.repository.subscription import (
    SubscriptionRepository,
)
from app.infrastructure.persistence.schema.subscription import SubscriptionSchema
from tests.generator.subscription import generate


async def test_add(session: AsyncSession) -> None:
    subscription = generate()
    subscription.renew(date(2026, 1, 1))

    await SubscriptionRepository(session).add(subscription)
    session.expunge_all()

    repository_subscription = await get_subscription(session)

    assert repository_subscription.id == UUID("019d2a4c-ab5d-7a0c-87bb-d4306b6d9d04")
    assert repository_subscription.email == "john@doe.com"
    assert repository_subscription.period == Period.MONTHLY
    assert repository_subscription.expires_at == date(2026, 2, 1)


async def test_add_duplicity(session: AsyncSession) -> None:
    session.add(SubscriptionSchema.from_domain(generate()))
    await session.flush()
    session.expunge_all()

    with raises(IntegrityError, match="uq_subscription_email"):
        async with session.begin_nested():
            await SubscriptionRepository(session).add(
                generate(UUID("019d2fc4-e06a-7dce-a23c-b8ce364f46a2"))
            )


async def test_find_one_by_email(session: AsyncSession) -> None:
    session.add(SubscriptionSchema.from_domain(generate()))
    await session.flush()
    session.expunge_all()

    repository_subscription = await SubscriptionRepository(session).find_one_by_email(
        Email("john@doe.com")
    )

    assert repository_subscription is not None
    assert repository_subscription.id == UUID("019d2a4c-ab5d-7a0c-87bb-d4306b6d9d04")
    assert repository_subscription.email.value == "john@doe.com"
    assert repository_subscription.period == Period.MONTHLY
    assert repository_subscription.expires_at is None


async def test_find_one_by_email_another_subscription_exists(
    session: AsyncSession,
) -> None:
    session.add(SubscriptionSchema.from_domain(generate()))
    await session.flush()
    session.expunge_all()

    repository_subscription = await SubscriptionRepository(session).find_one_by_email(
        Email("john2@doe.com")
    )

    assert repository_subscription is None


async def test_find_one_by_email_empty_repository(
    session: AsyncSession,
) -> None:
    repository_subscription = await SubscriptionRepository(session).find_one_by_email(
        Email("john@doe.com")
    )

    assert repository_subscription is None


async def test_get_one_by_email(session: AsyncSession) -> None:
    session.add(SubscriptionSchema.from_domain(generate()))
    await session.flush()
    session.expunge_all()

    repository_subscription = await SubscriptionRepository(session).get_one_by_email(
        Email("john@doe.com")
    )

    assert repository_subscription.id == UUID("019d2a4c-ab5d-7a0c-87bb-d4306b6d9d04")


async def test_get_one_by_email_another_subscription_exists(
    session: AsyncSession,
) -> None:
    session.add(SubscriptionSchema.from_domain(generate()))
    await session.flush()
    session.expunge_all()

    with raises(SubscriptionNotFoundError, match="Subscription not found"):
        await SubscriptionRepository(session).get_one_by_email(Email("john2@doe.com"))


async def test_get_one_by_email_empty_repository(session: AsyncSession) -> None:
    with raises(SubscriptionNotFoundError, match="Subscription not found"):
        await SubscriptionRepository(session).get_one_by_email(Email("john@doe.com"))


async def test_update(session: AsyncSession) -> None:
    subscription = generate()
    session.add(SubscriptionSchema.from_domain(subscription))
    await session.flush()
    session.expunge_all()

    subscription.period = Period.YEARLY
    subscription.renew(date(2026, 2, 1))

    await SubscriptionRepository(session).update(subscription)
    session.expunge_all()

    repository_subscription = await get_subscription(session)

    assert repository_subscription.id == UUID("019d2a4c-ab5d-7a0c-87bb-d4306b6d9d04")
    assert repository_subscription.email == "john@doe.com"
    assert repository_subscription.period == Period.YEARLY
    assert repository_subscription.expires_at == date(2027, 2, 1)


async def test_update_unknown(session: AsyncSession) -> None:
    session.add(SubscriptionSchema.from_domain(generate()))
    await session.flush()
    session.expunge_all()

    with raises(RuntimeError, match="Subscription not found"):
        await SubscriptionRepository(session).update(
            generate(UUID("019d2fb0-b4d2-7731-9924-9de4130ec63e"))
        )


async def get_subscription(session: AsyncSession) -> SubscriptionSchema:
    result = await session.exec(select(SubscriptionSchema))

    return result.one()
