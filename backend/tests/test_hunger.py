from datetime import datetime, timedelta

import pytest

from app.services.pet_service import recompute_hunger


def test_hunger_no_decay_just_created(db_session, test_pet):
    recompute_hunger(test_pet, db_session)
    assert test_pet.hunger == pytest.approx(100, abs=0.5)


def test_hunger_after_1_hour(db_session, test_pet):
    test_pet.last_hunger_update = datetime.utcnow() - timedelta(hours=1)
    db_session.commit()

    recompute_hunger(test_pet, db_session)
    # 100 - 1 * (100/48) ≈ 97.917
    assert test_pet.hunger == pytest.approx(97.917, abs=0.5)


def test_hunger_after_24_hours(db_session, test_pet):
    test_pet.last_hunger_update = datetime.utcnow() - timedelta(hours=24)
    db_session.commit()

    recompute_hunger(test_pet, db_session)
    # 100 - 24 * (100/48) = 50
    assert test_pet.hunger == pytest.approx(50, abs=0.5)


def test_hunger_after_48_hours(db_session, test_pet):
    test_pet.last_hunger_update = datetime.utcnow() - timedelta(hours=48)
    db_session.commit()

    recompute_hunger(test_pet, db_session)
    assert test_pet.hunger == pytest.approx(0, abs=0.5)


def test_hunger_after_72_hours(db_session, test_pet):
    test_pet.last_hunger_update = datetime.utcnow() - timedelta(hours=72)
    db_session.commit()

    recompute_hunger(test_pet, db_session)
    assert test_pet.hunger == 0


def test_hunger_restore_max_100(db_session, test_pet):
    test_pet.hunger = 90
    db_session.commit()

    test_pet.hunger = min(100, 90 + 30)
    db_session.commit()

    assert test_pet.hunger == 100
