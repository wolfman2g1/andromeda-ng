from passlib.context import CryptContext
from password_validation import PasswordPolicy
from typing import Tuple
password_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

""" Hash and verify passwords """


def hash_password(password: str) -> str:
    """ Hash password """
    return password_context.hash(password)


def verify_password(password: str, hashed_password: str) -> bool:
    """ Verify password """
    return password_context.verify(password, hashed_password)


def verify_password_policy(password: str) -> Tuple[bool, str]:
    """ Verify password policy """
    policy = PasswordPolicy.from_names(
        length=8,
        uppercase=1,
        numbers=1,
        special=1
    )
    if policy.test(password):
        return True, "Password is valid"
    else:
        return False, "Password is invalid"
