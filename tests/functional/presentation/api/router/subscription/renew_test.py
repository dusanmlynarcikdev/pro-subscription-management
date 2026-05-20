from datetime import date
from unittest.mock import patch
from uuid import UUID

from fastapi import status
from fastapi.testclient import TestClient
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from app.domain.subscription.email import Email
from app.domain.subscription.period import Period
from app.infrastructure.persistence.schema.subscription import SubscriptionSchema
from tests.functional.fake_email_sender import FakeEmailSender
from tests.generator.subscription import generate

PATH = "/api/subscriptions/{email}/renew"


async def test_renew(
    client: TestClient, email_sender: FakeEmailSender, session: AsyncSession
) -> None:
    session.add(SubscriptionSchema.from_domain(generate()))
    await session.flush()
    session.expunge_all()

    with patch("app.application.subscription.renew_use_case.date") as mock_date:
        mock_date.today.return_value = date(2026, 1, 1)
        response = client.post(PATH.format(email="john@doe.com"))
    session.expunge_all()

    assert response.status_code == status.HTTP_204_NO_CONTENT
    assert response.content == b""

    repository_subscription = (await session.exec(select(SubscriptionSchema))).one()

    assert repository_subscription.id == UUID("019d2a4c-ab5d-7a0c-87bb-d4306b6d9d04")
    assert repository_subscription.email == "john@doe.com"
    assert repository_subscription.period == Period.MONTHLY
    assert repository_subscription.expires_at == date(2026, 2, 1)

    assert len(email_sender.sent) == 1
    assert email_sender.sent[0].recipient == Email("john@doe.com")
    assert email_sender.sent[0].subject == "Subscription renewed"
    assert email_sender.sent[0].body == "Subscription renewed. Expires on Feb 1, 2026."


async def test_unknown_email(client: TestClient, session: AsyncSession) -> None:
    session.add(SubscriptionSchema.from_domain(generate()))
    await session.flush()
    session.expunge_all()

    response = client.post(PATH.format(email="john2@doe.com"))

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.content == b'{"detail":"Subscription not found"}'


def test_invalid_email(client: TestClient) -> None:
    response = client.post(PATH.format(email="johndoe.com"))

    assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT
    assert response.content == b'{"detail":"Invalid email"}'
