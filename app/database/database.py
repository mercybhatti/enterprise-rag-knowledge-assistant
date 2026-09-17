import sqlite3
from pathlib import Path


# ============================================================
# DATABASE CONFIGURATION
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parents[2]

DATABASE_DIR = PROJECT_ROOT / "data"

DATABASE_PATH = DATABASE_DIR / "knowledge_ai.db"


# ============================================================
# DATABASE CONNECTION
# ============================================================

def get_connection():
    """Create and return a SQLite database connection."""

    DATABASE_DIR.mkdir(
        parents=True,
        exist_ok=True
    )

    connection = sqlite3.connect(
        DATABASE_PATH,
        check_same_thread=False
    )

    connection.row_factory = sqlite3.Row

    # Enable foreign-key support in SQLite.
    # This is required for ON DELETE CASCADE to work.
    connection.execute(
        "PRAGMA foreign_keys = ON"
    )

    return connection


# ============================================================
# DATABASE INITIALIZATION
# ============================================================

def initialize_database():
    """Create all required application tables."""

    connection = get_connection()

    cursor = connection.cursor()

    # --------------------------------------------------------
    # USERS
    # --------------------------------------------------------

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS users (

            id INTEGER PRIMARY KEY AUTOINCREMENT,

            name TEXT NOT NULL,

            email TEXT NOT NULL UNIQUE,

            password_hash TEXT NOT NULL,

            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP

        )
        """
    )

    # --------------------------------------------------------
    # CONVERSATIONS
    # --------------------------------------------------------

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS conversations (

            id INTEGER PRIMARY KEY AUTOINCREMENT,

            user_id INTEGER NOT NULL,

            title TEXT NOT NULL,

            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

            FOREIGN KEY (user_id)
                REFERENCES users(id)
                ON DELETE CASCADE

        )
        """
    )

    # --------------------------------------------------------
    # MESSAGES
    # --------------------------------------------------------

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS messages (

            id INTEGER PRIMARY KEY AUTOINCREMENT,

            conversation_id INTEGER NOT NULL,

            role TEXT NOT NULL,

            content TEXT NOT NULL,

            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

            FOREIGN KEY (conversation_id)
                REFERENCES conversations(id)
                ON DELETE CASCADE

        )
        """
    )

    # --------------------------------------------------------
    # DOCUMENTS
    # --------------------------------------------------------

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS documents (

            id INTEGER PRIMARY KEY AUTOINCREMENT,

            filename TEXT NOT NULL UNIQUE,

            file_path TEXT NOT NULL,

            page_count INTEGER NOT NULL DEFAULT 0,

            chunk_count INTEGER NOT NULL DEFAULT 0,

            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP

        )
        """
    )

    connection.commit()

    connection.close()


# ============================================================
# USER OPERATIONS
# ============================================================

def create_user(
    name,
    email,
    password_hash
):
    """Create a new user account."""

    connection = get_connection()

    cursor = connection.cursor()

    try:

        cursor.execute(
            """
            INSERT INTO users (
                name,
                email,
                password_hash
            )

            VALUES (?, ?, ?)
            """,
            (
                name,
                email,
                password_hash
            )
        )

        connection.commit()

        user_id = cursor.lastrowid

        return user_id

    except sqlite3.IntegrityError:

        return None

    finally:

        connection.close()


def get_user_by_email(email):
    """Return a user by email address."""

    connection = get_connection()

    cursor = connection.cursor()

    cursor.execute(
        """
        SELECT
            id,
            name,
            email,
            password_hash,
            created_at

        FROM users

        WHERE email = ?
        """,
        (email,)
    )

    user = cursor.fetchone()

    connection.close()

    return user


def get_user_by_id(user_id):
    """Return a user by user ID."""
    connection = get_connection()

    cursor = connection.cursor()

    cursor.execute(
        """
        SELECT
            id,
            name,
            email,
            password_hash,
            created_at

        FROM users

        WHERE id = ?
        """,
        (user_id,)
    )

    user = cursor.fetchone()

    connection.close()

    return user

# ============================================================
# CONVERSATION OPERATIONS
# ============================================================

def create_conversation(
    user_id,
    title="New Conversation"
):
    """Create a new conversation for a user."""

    connection = get_connection()

    cursor = connection.cursor()

    cursor.execute(
        """
        INSERT INTO conversations (
            user_id,
            title
        )

        VALUES (?, ?)
        """,
        (
            user_id,
            title
        )
    )

    connection.commit()

    conversation_id = cursor.lastrowid

    connection.close()

    return conversation_id


def get_user_conversations(user_id):
    """Return all conversations belonging to a user."""

    connection = get_connection()

    cursor = connection.cursor()

    cursor.execute(
        """
        SELECT
            id,
            title,
            created_at,
            updated_at

        FROM conversations

        WHERE user_id = ?

        ORDER BY updated_at DESC
        """,
        (user_id,)
    )

    conversations = cursor.fetchall()

    connection.close()

    return conversations


def get_conversation(
    conversation_id,
    user_id
):
    """Return one conversation belonging to a user."""

    connection = get_connection()

    cursor = connection.cursor()

    cursor.execute(
        """
        SELECT
            id,
            title,
            created_at,
            updated_at

        FROM conversations

        WHERE id = ?
        AND user_id = ?
        """,
        (
            conversation_id,
            user_id
        )
    )

    conversation = cursor.fetchone()

    connection.close()

    return conversation


def update_conversation_title(
    conversation_id,
    user_id,
    title
):
    """Update a conversation title."""

    connection = get_connection()

    cursor = connection.cursor()

    cursor.execute(
        """
        UPDATE conversations

        SET
            title = ?,
            updated_at = CURRENT_TIMESTAMP

        WHERE id = ?
        AND user_id = ?
        """,
        (
            title,
            conversation_id,
            user_id
        )
    )

    connection.commit()

    connection.close()


def touch_conversation(
    conversation_id,
    user_id
):
    """Update the last activity time of a conversation."""

    connection = get_connection()

    cursor = connection.cursor()

    cursor.execute(
        """
        UPDATE conversations

        SET
            updated_at = CURRENT_TIMESTAMP

        WHERE id = ?
        AND user_id = ?
        """,
        (
            conversation_id,
            user_id
        )
    )

    connection.commit()

    connection.close()


def delete_conversation(
    conversation_id,
    user_id
):
    """
    Delete a conversation belonging to a specific user.

    Because the messages table uses ON DELETE CASCADE,
    all messages belonging to this conversation are also
    deleted automatically.
    """

    connection = get_connection()

    cursor = connection.cursor()

    # --------------------------------------------------------
    # Verify conversation ownership
    # --------------------------------------------------------

    cursor.execute(
        """
        SELECT
            id

        FROM conversations

        WHERE id = ?
        AND user_id = ?
        """,
        (
            conversation_id,
            user_id
        )
    )

    conversation = cursor.fetchone()

    if conversation is None:

        connection.close()

        return False

    # --------------------------------------------------------
    # Delete conversation
    # --------------------------------------------------------

    cursor.execute(
        """
        DELETE FROM conversations

        WHERE id = ?
        AND user_id = ?
        """,
        (
            conversation_id,
            user_id
        )
    )

    connection.commit()

    connection.close()

    return True


# ============================================================
# MESSAGE OPERATIONS
# ============================================================

def save_message(
    conversation_id,
    role,
    content
):
    """Save a chat message."""

    connection = get_connection()

    cursor = connection.cursor()

    cursor.execute(
        """
        INSERT INTO messages (
            conversation_id,
            role,
            content
        )

        VALUES (?, ?, ?)
        """,
        (
            conversation_id,
            role,
            content
        )
    )

    connection.commit()

    connection.close()


def get_conversation_messages(
    conversation_id,
    user_id
):
    """Return messages for a user's conversation."""

    connection = get_connection()

    cursor = connection.cursor()

    cursor.execute(
        """
        SELECT
            messages.id,
            messages.role,
            messages.content,
            messages.created_at

        FROM messages

        INNER JOIN conversations
            ON messages.conversation_id = conversations.id

        WHERE messages.conversation_id = ?
        AND conversations.user_id = ?

        ORDER BY messages.id ASC
        """,
        (
            conversation_id,
            user_id
        )
    )

    messages = cursor.fetchall()

    connection.close()

    return messages


# ============================================================
# DOCUMENT OPERATIONS
# ============================================================

def create_document(
    filename,
    file_path,
    page_count,
    chunk_count
):
    """Register an indexed document in the database."""

    connection = get_connection()

    cursor = connection.cursor()

    try:

        cursor.execute(
            """
            INSERT INTO documents (
                filename,
                file_path,
                page_count,
                chunk_count
            )

            VALUES (?, ?, ?, ?)
            """,
            (
                filename,
                file_path,
                page_count,
                chunk_count
            )
        )

        connection.commit()

        document_id = cursor.lastrowid

        return document_id

    except sqlite3.IntegrityError:

        return None

    finally:

        connection.close()


def get_documents():
    """Return all indexed documents."""

    connection = get_connection()

    cursor = connection.cursor()

    cursor.execute(
        """
        SELECT
            id,
            filename,
            file_path,
            page_count,
            chunk_count,
            created_at

        FROM documents

        ORDER BY created_at DESC
        """
    )

    documents = cursor.fetchall()

    connection.close()

    return documents


def get_document_by_filename(filename):
    """Return a document by its filename."""

    connection = get_connection()

    cursor = connection.cursor()

    cursor.execute(
        """
        SELECT
            id,
            filename,
            file_path,
            page_count,
            chunk_count,
            created_at

        FROM documents

        WHERE filename = ?
        """,
        (filename,)
    )

    document = cursor.fetchone()

    connection.close()

    return document


# ============================================================
# DATABASE TEST
# ============================================================

if __name__ == "__main__":

    initialize_database()

    print(
        "\nDatabase initialized successfully."
    )

    print(
        f"Database location:\n{DATABASE_PATH}"
    )

    documents = get_documents()

    print(
        f"\nRegistered documents: {len(documents)}"
    )

    for document in documents:

        print(
            f"- {document['filename']} "
            f"({document['page_count']} pages, "
            f"{document['chunk_count']} chunks)"
        )