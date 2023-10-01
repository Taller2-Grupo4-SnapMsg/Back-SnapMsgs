# errors.py

"""
This module is for exceptions that may be raised by the repository layer.
"""


class DatabaseTimeout(Exception):
    """
    Exception raised when the database times out.
    """

    def __init__(self):
        super().__init__("Database timeout")


class PostNotFound(Exception):
    """
    Exception raised when post not found.
    """

    def __init__(self):
        super().__init__("Post not found")


class UserNotFound(Exception):
    """
    Exception raised when user not found.
    """

    def __init__(self):
        super().__init__("User not found")

class LikeNotFound(Exception):
    """
    Exception raised when like not found.
    """

    def __init__(self):
        super().__init__("Like not found")
