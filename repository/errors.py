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


class DatabaseError(Exception):
    """
    Exception raised when the database times out.
    """

    def __init__(self):
        super().__init__("Database error")


class NegativeOrZeroAmount(Exception):
    """
    Exception raised when amount is equal or less than 0
    """

    def __init__(self):
        super().__init__("Invalid amount. Equal or less than zero.")


class RepostAlreadyMade(Exception):
    """
    Exception raised when user wants to repost a post they already reposted
    """

    def __init__(self):
        super().__init__("User already reposted that post.")


class CannotLikeRepost(Exception):
    """
    Exception raised when amount is equal or less than 0
    """

    def __init__(self):
        super().__init__("Reposts cannot be liked.")


class UserWithouPermission(Exception):
    """
    Exception raised when amount is equal or less than 0
    """

    def __init__(self):
        super().__init__("User doesnt have permissions to do that action.")


class ThisUserIsBlocked(Exception):
    """
    Exception raised when this user is blocked. Error code 403 should be raised.
    """

    def __init__(self):
        super().__init__("This user is blocked.")


class OtherUserIsBlocked(Exception):
    """
    Exception raised when the user another user is trying to access
    is blocked. Error code 405 should be raised.
    """

    def __init__(self):
        super().__init__("The other user is blocked.")


class UserDoesntHavePosts(Exception):
    """
    Exception raised when post not found.
    """

    def __init__(self):
        super().__init__("User doesnt have any posts")


class UserIsPrivate(Exception):
    """
    Exception raised when post not found.
    """

    def __init__(self):
        super().__init__("User is private")


class PostNotFound(Exception):
    """
    Exception raised when post not found.
    """

    def __init__(self):
        super().__init__("Post not found")


class RepostNotFound(Exception):
    """
    Exception raised when post not found.
    """

    def __init__(self):
        super().__init__("Repost not found")


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


class FavoriteNotFound(Exception):
    """
    Exception raised when favorite not found.
    """

    def __init__(self):
        super().__init__("Favorite not found")


class EmptyPostError(Exception):
    """
    Exception raised when post is empty.
    """

    def __init__(self, message="Both text and image are empty."):
        super().__init__(message)


class TextTooLongError(Exception):
    """
    Exception raised when text is too long.
    """

    def __init__(self, message="Text exceeds maximum length of 1000 characters."):
        super().__init__(message)
