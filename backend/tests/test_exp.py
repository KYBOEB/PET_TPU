from datetime import datetime, timedelta

from app.services.pet_service import (
    apply_exp_penalty,
    get_mood,
    get_required_exp,
)


def test_required_exp_level_0():
    assert get_required_exp(0) == 200


def test_required_exp_level_1():
    assert get_required_exp(1) == 300


def test_required_exp_level_2():
    assert get_required_exp(2) == 450


def test_mood_happy():
    assert get_mood(85) == "happy"


def test_mood_neutral():
    assert get_mood(50) == "neutral"


def test_mood_sad():
    assert get_mood(10) == "sad"


def test_penalty_at_hunger_zero(db_session, test_pet):
    test_pet.hunger = 0
    test_pet.current_exp = 100
    test_pet.hunger_zero_since = datetime.utcnow() - timedelta(hours=3)
    db_session.commit()

    apply_exp_penalty(test_pet, db_session)
    # floor(3) * 10 = 30, so 100 - 30 = 70
    assert test_pet.current_exp == 70


def test_penalty_exp_not_below_zero(db_session, test_pet):
    test_pet.hunger = 0
    test_pet.current_exp = 5
    test_pet.hunger_zero_since = datetime.utcnow() - timedelta(hours=3)
    db_session.commit()

    apply_exp_penalty(test_pet, db_session)
    assert test_pet.current_exp == 0


def test_penalty_no_level_decrease(db_session, test_pet):
    test_pet.level = 2
    test_pet.current_exp = 0
    test_pet.hunger = 0
    test_pet.hunger_zero_since = datetime.utcnow() - timedelta(hours=5)
    db_session.commit()

    apply_exp_penalty(test_pet, db_session)
    assert test_pet.level == 2
    assert test_pet.current_exp == 0


def test_penalty_not_applied_when_hunger_above_zero(db_session, test_pet):
    test_pet.hunger = 50
    test_pet.current_exp = 100
    test_pet.hunger_zero_since = None
    db_session.commit()

    apply_exp_penalty(test_pet, db_session)
    assert test_pet.current_exp == 100
