"""gdps.xyz errors module

MIT License

Copyright (c) 2021 bangakek

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and 
associated documentation files (the "Software"), to deal in the Software without restriction, 
including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, 
and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, 
subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, 
INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND 
NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, 
WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR 
THE USE OR OTHER DEALINGS IN THE SOFTWARE.
"""


class XYZException(Exception):
    """Generic gdps.xyz exception"""

    __slots__ = (
        'res',
        'msg',
        'exc_data'
    )

    def __init__(self, res, msg = None):
        self.res = res
        self.msg = msg
        self.exc_data = f'({self.res.status_code} | {self.res.reason})'
        if self.msg:
            self.exc_data += f' {self.msg}'
        super().__init__(self.exc_data)


class BadRequest(XYZException):
    """Bad request to gdps.xyz API"""

    pass


class InternalServerError(XYZException):
    """A server side error has occured"""

    pass


class NotFound(XYZException):
    """
Occurs when you trying to act with something that
was not found
    """

    pass


class RegistrationError(XYZException):
    """Can occur while account registration"""

    pass


class ActivationError(XYZException):
    """Can occur while account activation"""

    pass


class AuthorizationError(XYZException):
    """Can occur while authorization"""

    pass


class PasswordRestoreError(XYZException):
    """No description"""

    pass


class AccountDeletionError(XYZException):
    """No description"""

    pass


class OutOfRateLimits(XYZException):
    """No description"""

    pass


class NotAllowed(XYZException):
    """Occurs when you dont have access to something"""
    
    pass


class InvalidToken(XYZException):
    """Occurs when your token or refresh token becomes invalid"""

    pass


class NotInitialized(XYZException):
    """Occurs when you have not initialized your session"""

    pass


class NotAcceptable(XYZException):
    """Occurs when you trying to send not acceptable data to the gdps.xyz API"""
    
    pass


class AlreadyExists(XYZException):
    """Occurs when the same data exists in the gdps.xyz database"""

    pass