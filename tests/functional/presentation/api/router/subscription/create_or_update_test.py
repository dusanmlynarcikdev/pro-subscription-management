from uuid import UUID

from fastapi import status
from fastapi.testclient import TestClient
from pytest import mark
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from app.domain.subscription.email import Email
from app.domain.subscription.period import Period
from app.infrastructure.persistence.schema.subscription import SubscriptionSchema
from tests.generator.subscription import generate

PATH = "/api/subscriptions"


async def test_create(client: TestClient, session: AsyncSession) -> None:
    session.add(SubscriptionSchema.from_domain(generate()))
    await session.flush()
    session.expunge_all()

    response = client.post(
        PATH,
        json={
            "email": "john2@doe.com",
            "period": "yearly",
        },
    )
    session.expunge_all()

    assert response.status_code == status.HTTP_204_NO_CONTENT
    assert response.content == b""

    repository_subscriptions = (await session.exec(select(SubscriptionSchema))).all()

    assert len(repository_subscriptions) == 2

    assert repository_subscriptions[0].id == UUID(
        "019d2a4c-ab5d-7a0c-87bb-d4306b6d9d04"
    )
    assert repository_subscriptions[0].email == "john@doe.com"
    assert repository_subscriptions[0].period == Period.MONTHLY
    assert repository_subscriptions[0].expires_at is None

    assert repository_subscriptions[1].email == "john2@doe.com"
    assert repository_subscriptions[1].period == Period.YEARLY
    assert repository_subscriptions[1].expires_at is None


async def test_update(client: TestClient, session: AsyncSession) -> None:
    session.add(SubscriptionSchema.from_domain(generate()))
    session.add(
        SubscriptionSchema.from_domain(
            generate(
                UUID("019d43e5-eecd-7ab5-a891-7688443b13f6"),
                Email("john2@doe.com"),
            )
        )
    )
    await session.flush()
    session.expunge_all()

    response = client.post(
        PATH,
        json={
            "email": "john2@doe.com",
            "period": "yearly",
        },
    )
    session.expunge_all()

    assert response.status_code == status.HTTP_204_NO_CONTENT
    assert response.content == b""

    repository_subscriptions = (await session.exec(select(SubscriptionSchema))).all()

    assert len(repository_subscriptions) == 2

    assert repository_subscriptions[0].id == UUID(
        "019d2a4c-ab5d-7a0c-87bb-d4306b6d9d04"
    )
    assert repository_subscriptions[0].email == "john@doe.com"
    assert repository_subscriptions[0].period == Period.MONTHLY
    assert repository_subscriptions[0].expires_at is None

    assert repository_subscriptions[1].id == UUID(
        "019d43e5-eecd-7ab5-a891-7688443b13f6"
    )
    assert repository_subscriptions[1].email == "john2@doe.com"
    assert repository_subscriptions[1].period == Period.YEARLY
    assert repository_subscriptions[1].expires_at is None


@mark.parametrize(
    "json, expected_content",
    [
        (
            {
                "email": "doe.com",
                "period": "yearly",
            },
            b'{"detail":"Invalid email"}',
        ),
        (
            {
                "email": "john@doe.com",
                "period": "unknown",
            },
            b'{"detail":"Invalid request"',
        ),
    ],
)
def test_invalid_value(
    client: TestClient,
    json: dict[str, str],
    expected_content: bytes,
) -> None:
    response = client.post(PATH, json=json)

    assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT
    assert expected_content in response.content
