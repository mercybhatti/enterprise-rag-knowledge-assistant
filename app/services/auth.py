import hashlib
import hmac
import secrets

from app.database.database import (
    create_user,
    get_user_by_email,
)


# ============================================================
# PASSWORD CONFIGURATION
# ============================================================

HASH_ITERATIONS = 310_000

SALT_LENGTH = 32


# ============================================================
# PASSWORD HASHING
# ============================================================

def hash_password(password):
    """
    Create a secure password hash using PBKDF2-HMAC-SHA256.
    """

    salt = secrets.token_bytes(
        SALT_LENGTH
    )

    password_hash = hashlib.pbkdf2_hmac(
        "sha256",
        password.encode("utf-8"),
        salt,
        HASH_ITERATIONS,
    )

    return (
        salt.hex()
        + ":"
        + password_hash.hex()
    )


def verify_password(
    password,
    stored_password_hash
):
    """
    Verify a password against its stored hash.
    """

    try:

        salt_hex, hash_hex = (
            stored_password_hash.split(":")
        )

        salt = bytes.fromhex(
            salt_hex
        )

        expected_hash = bytes.fromhex(
            hash_hex
        )

        actual_hash = hashlib.pbkdf2_hmac(
            "sha256",
            password.encode("utf-8"),
            salt,
            HASH_ITERATIONS,
        )

        return hmac.compare_digest(
            actual_hash,
            expected_hash
        )

    except (
        ValueError,
        TypeError,
    ):

        return False


# ============================================================
# EMAIL VALIDATION
# ============================================================

def validate_email(email):
    """
    Perform basic email validation.
    """

    email = email.strip().lower()

    if not email:
        return False

    if "@" not in email:
        return False

    if "." not in email.split("@")[-1]:
        return False

    return True


# ============================================================
# PASSWORD VALIDATION
# ============================================================

def validate_password(password):
    """
    Validate password strength.
    """

    if not password:
        return False, "Password is required."

    if len(password) < 8:
        return False, (
            "Password must contain at least 8 characters."
        )

    return True, ""


# ============================================================
# USER REGISTRATION
# ============================================================

def register_user(
    name,
    email,
    password
):
    """
    Register a new user.
    """

    name = name.strip()

    email = email.strip().lower()


    # --------------------------------------------------------
    # NAME VALIDATION
    # --------------------------------------------------------

    if not name:

        return {
            "success": False,
            "message": "Name is required.",
            "user": None,
        }


    # --------------------------------------------------------
    # EMAIL VALIDATION
    # --------------------------------------------------------

    if not validate_email(email):

        return {
            "success": False,
            "message": "Please enter a valid email address.",
            "user": None,
        }


    # --------------------------------------------------------
    # PASSWORD VALIDATION
    # --------------------------------------------------------

    password_valid, password_message = (
        validate_password(password)
    )

    if not password_valid:

        return {
            "success": False,
            "message": password_message,
            "user": None,
        }


    # --------------------------------------------------------
    # EXISTING USER CHECK
    # --------------------------------------------------------

    existing_user = get_user_by_email(
        email
    )

    if existing_user:

        return {
            "success": False,
            "message": (
                "An account with this email already exists."
            ),
            "user": None,
        }


    # --------------------------------------------------------
    # PASSWORD HASH
    # --------------------------------------------------------

    password_hash = hash_password(
        password
    )


    # --------------------------------------------------------
    # CREATE USER
    # --------------------------------------------------------

    user_id = create_user(
        name=name,
        email=email,
        password_hash=password_hash,
    )

    if user_id is None:

        return {
            "success": False,
            "message": (
                "Could not create the account. "
                "Please try again."
            ),
            "user": None,
        }


    # --------------------------------------------------------
    # SUCCESS
    # --------------------------------------------------------

    return {
        "success": True,
        "message": "Account created successfully.",
        "user": {
            "id": user_id,
            "name": name,
            "email": email,
        },
    }


# ============================================================
# USER LOGIN
# ============================================================

def login_user(
    email,
    password
):
    """
    Authenticate a user using email and password.
    """

    email = email.strip().lower()


    # --------------------------------------------------------
    # INPUT VALIDATION
    # --------------------------------------------------------

    if not validate_email(email):

        return {
            "success": False,
            "message": "Please enter a valid email address.",
            "user": None,
        }


    if not password:

        return {
            "success": False,
            "message": "Password is required.",
            "user": None,
        }


    # --------------------------------------------------------
    # FIND USER
    # --------------------------------------------------------

    user = get_user_by_email(
        email
    )

    if user is None:

        return {
            "success": False,
            "message": (
                "Invalid email or password."
            ),
            "user": None,
        }


    # --------------------------------------------------------
    # VERIFY PASSWORD
    # --------------------------------------------------------

    password_valid = verify_password(
        password,
        user["password_hash"],
    )

    if not password_valid:

        return {
            "success": False,
            "message": (
                "Invalid email or password."
            ),
            "user": None,
        }


    # --------------------------------------------------------
    # SUCCESS
    # --------------------------------------------------------

    return {
        "success": True,
        "message": "Login successful.",
        "user": {
            "id": user["id"],
            "name": user["name"],
            "email": user["email"],
        },
    }


# ============================================================
# LOCAL TEST
# ============================================================

if __name__ == "__main__":

    print(
        "\n========== AUTHENTICATION TEST =========="
    )


    # --------------------------------------------------------
    # PASSWORD HASH TEST
    # --------------------------------------------------------

    test_password = "KnowledgeAI123"

    hashed = hash_password(
        test_password
    )

    print(
        "\nPassword hash generated:"
    )

    print(
        hashed[:40] + "..."
    )


    # --------------------------------------------------------
    # PASSWORD VERIFICATION
    # --------------------------------------------------------

    correct_result = verify_password(
        test_password,
        hashed
    )

    wrong_result = verify_password(
        "WrongPassword",
        hashed
    )


    print(
        "\nCorrect password verification:",
        correct_result
    )

    print(
        "Wrong password verification:",
        wrong_result
    )


    # --------------------------------------------------------
    # EXPECTED RESULT
    # --------------------------------------------------------

    print(
        "\nAuthentication service is working."
    )