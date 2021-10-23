"""
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

from datetime import datetime
import json
import requests
from itertools import islice
from .xyz import (
    Object,
    TimestampedObject,
    GDPSStats,
    GDPSLinks,
    GDPSImages,
    SessionIPs,
    Vote,
    Voteable,
    Updateable
)
from . import errors


_authorization = None


# yeah lets make it easier
def _raise_for_errors(r, exc_of = ()):
    raises = {
        400: errors.BadRequest(r),
        401: errors.NotInitialized(r, 'you have hot initialized your session or did it wrong.'),
        404: errors.NotFound(r, 'can not act with object.'),
        406: errors.NotAcceptable(r, 'check the request data you trying to send.'),
        409: errors.NotAcceptable(r, 'Attachment error. Check your avatar or background url validation.'),
        429: errors.OutOfRateLimits(r),
        500: errors.InternalServerError(r, 'a server side error has occured. Contact developers for help.')
    }
    if r.status_code in raises and r.status_code not in exc_of:
        raise raises[r.status_code]

# for functions and methods that require authorization
def _auth_required(req):
    def auth_check(*args, **kwds):
        if not isinstance(_authorization, Session):
            raise errors.NotInitialized('you have not initialized your session.')
        return req(*args, **kwds)
    return auth_check



class Session(Object):
    """
Represents opened session authorization
    
Supports :class:`gdpsxyz.Object` operand types
    """

    __slots__ = (
        'token',
        'refresh_token',
        'token_expiration',
        'refresh_token_expiration'
    )

    def __init__(self, token_session):
        self.token = token_session.get('token')
        self.refresh_token = token_session.get('refreshToken')
        self.token_expiration = token_session.get('tokenExpiration')
        self.refresh_token_expiration = token_session.get('refreshTokenExpiration')
        super().__init__(token_session.get('id'))

    def __repr__(self):
        attrs = [
            ('id', self.id),
            ('token', self.token),
            ('refresh_token', self.refresh_token),
            ('token_expiration', self.token_expiration),
            ('refresh_token_expiration', self.refresh_token_expiration)
        ]
        inner = ', '.join('%s=%r' % t for t in attrs)
        return f'<{self.__class__.__name__} {inner}>'

    def __enter__(self):
        self.init()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type is None:
            self.close()
        return False

    @property
    def token_expiration_dt(self):
        return datetime.fromtimestamp(self.token_expiration)

    @property
    def refresh_token_expiration_dt(self):
        return datetime.fromtimestamp(self.refresh_token_expiration)

    @property
    def info(self):
        """Returns current session informations in :class:`gdpsxyz.SessionInfo` object."""
        headers = {
            'authorization': f'Bearer {self.token}'
        }
        r = requests.get(
            url = f'https://gdps.xyz/api/session/{self.id}/',
            headers = headers
        )
        if r.status_code >= 400:
            _raise_for_errors(r, exc_of=(401, 404))
            if r.status_code == 401:
                raise errors.InvalidToken(r, 'invalid session token.')
            if r.status_code == 404:
                raise errors.NotFound(r, 'session was closed or not found.')
        session_info = r.json().get('data')
        return SessionInfo(session_info)

    def sessions(self, page):
        """Returns a list of opened sessions (:class:`gdpsxyz.SessionInfo`)"""
        assert isinstance(page, int), 'page must be an integer.'
        assert page, 'page integer must be positive.'
        param = {
            'page': page
        }
        headers = {
            'authorization': f'Bearer {self.token}'
        }
        r = requests.get(
            url = 'https://gdps.xyz/api/session/all/',
            params = param,
            headers = headers
        )
        if r.status_code >= 400:
            _raise_for_errors(r)
        session_infos = r.json().get('data')
        return [SessionInfo(s) for s in session_infos]

    def refresh(self):
        """Regenerate session token using refresh token"""
        body = json.dumps({
            'refreshToken': self.refresh_token
        })
        headers = {
            'content-type': 'application/json'
        }
        r = requests.get(
            url = 'https://gdps.xyz/api/session/reauthorize/',
            data = body,
            headers = headers
        )
        session = r.json().get('data')
        if session:
            self.token = session.get('token')
            if _authorization:
                self.init()
        elif r.status_code >= 400:
            _raise_for_errors(r, exc_of = (401,))
            if r.status_code == 401:
                raise errors.InvalidToken(r, 'Can not refresh session. Invalid refresh token.')

    def close(self):
        """Close session and delete its data"""
        headers = {
            'content-type': 'application/json',
            'authorization': f'Bearer {self.token}'
        }
        r = requests.delete(
            url = f'https://gdps.xyz/api/session/{self.id}/',
            headers = headers
        )
        if r.status_code >= 400:
            _raise_for_errors(r, exc_of = (401, ))
            if r.status_code == 401:
                raise errors.InvalidToken(r, 'invalid session token.')

    def init(self):
        """Initialize opened session to work with functions and methods that require authorization"""
        global _authorization
        _authorization = self


class SessionInfo(TimestampedObject):
    """
Represents opened session informations

Supports :class:`gdpsxyz.Object` operand types
    """

    __slots__ = ('_ips', 'refresh_count')

    def __init__(self, session):
        self._ips = session.get('ips')
        self.refresh_count = session.get('refreshCount')
        super().__init__(
            session.get('id'),
            session.get('timestamps', {}).get('createdOn'),
            session.get('timestamps', {}).get('lastUpdatedSessionOn')
        )

    def __repr__(self):
        attrs = [
            ('id', self.id),
            ('ips', self.ips),
            ('created_at', self.created_at),
            ('last_updated_at', self.last_updated_at),
            ('refresh_count', self.refresh_count)
        ]
        inner = ', '.join('%s=%r' % t for t in attrs)
        return f'<{self.__class__.__name__} {inner}>'

    @property
    def ips(self):
        return SessionIPs(self._ips)




class Account(TimestampedObject):
    """
Represents a gdps.xyz account

Supports :class:`gdpsxyz.Object` operand types
    """

    __slots__ = (
        'permission_level',
        'username',
        'avatar_url'
    )

    def __init__(self, account):
        self.permission_level = account.get('permissionLevel')
        self.username = account.get('username')
        self.avatar_url = account.get('avatarUrl')
        super().__init__(
            account.get('id'),
            account.get('accountCreatedOn'),
            account.get('accountLastUpdatedOn')
        )

    def __repr__(self):
        attrs = [
            ('id', self.id),
            ('permission_level', self.permission_level),
            ('username', self.username),
            ('avatar_url', self.avatar_url),
            ('created_at', self.created_at),
            ('last_updated_at', self.last_updated_at)
        ]
        inner = ', '.join('%s=%r' % t for t in attrs)
        return f'<{self.__class__.__name__} {inner}>'


class MyAccount(Account, Updateable):
    """
Represents authorized account

Supports :class:`gdpsxyz.Object` operand types
    """

    __slots__ = ('_email',)

    def __init__(self, account):
        self._email = account.get('email')
        super().__init__(account)

    def __repr__(self):
        attrs = [
            ('id', self.id),
            ('permission_level', self.permission_level),
            ('username', self.username),
            ('email', self.email),
            ('avatar_url', self.avatar_url),
            ('created_at', self.created_at)
        ]
        inner = ', '.join('%s=%r' % t for t in attrs)
        return f'<{self.__class__.__name__} {inner}>'

    @property
    def email(self):
        """Gives you your account email"""
        return self._email

    @staticmethod
    @_auth_required
    def gdpslist(page):
        """
Requires authorization.

Gives you a list of your GDPSs
        """
        assert isinstance(page, int), 'page must be an integer.'
        assert page, 'page integer must be positive.'
        param = {
            'page': page
        }
        headers = {
            'content-type': 'application/json',
            'authorization': f'Bearer {_authorization.token}'
        }
        r = requests.get(
            url = 'https://gdps.xyz/api/gdps/my',
            params = param,
            headers = headers
        )
        if r.status_code >= 400:
            _raise_for_errors(r)
        gdps_pagination = r.json().get('data')
        return [GDPS(g) for g in gdps_pagination]

    @staticmethod
    @_auth_required
    def update(
        *,
        email = None,
        password = None,
        avatar_url = None,
        username = None
    ):
        """
Requires authorization.

Update your gdps.xyz account informations
        """
        body = {
            'email': email,
            'password': password,
            'username': username
        }
        for i in email, password, avatar_url, username:
            if i:
                assert isinstance(i, str), 'account informations must be strings.'
                assert i, 'do not leave argument empty after passing it.'
            else:
                del body[next(islice(body, i, None))]
        headers = {
            'content-type': 'application/json',
            'authorization': f'Bearer {_authorization.token}'
        }
        body = json.dumps(body)
        r = requests.put(
            url = 'https://gdps.xyz/api/account/update/',
            data = body,
            headers = headers
        )
        if r.status_code >= 400:
            _raise_for_errors(r)

    @staticmethod
    @_auth_required
    def delete():
        """
Requires authorization.

Deletes your account immediately. Be careful with that :/
        """
        headers = {
            'content-type': 'application/json',
            'authorization': f'Bearer {_authorization.token}'
        }
        r = requests.delete(
            url = 'https://gdps.xyz/api/account/delete/',
            headers = headers
        )
        if r.status_code >= 400:
            _raise_for_errors(r)
            if r.status_code == 403:
                raise errors.AccountDeletionError(r, 'delete all your GDPSs before account deletion.')


class Comment(TimestampedObject, Voteable, Updateable):
    """
Represents a gdps.xyz comment

Supports :class:`gdpsxyz.Object` operand types
    """
    __slots__ = (
        '_author',
        '_stats',
        'gdps_id',
        'text',
        'content'
    )

    def __init__(self, comment):
        self._author = comment.get('account')
        self._stats = comment.get('stats')
        self.gdps_id = comment.get('gdpsId')
        self.text = comment.get('text')
        self.content = self.text
        super().__init__(
            comment.get('id'),
            comment.get('timestamps', {}).get('createdOn'),
            comment.get('timestamps', {}).get('lastUpdatedOn')
        )

    def __repr__(self):
        attrs = [
            ('id', self.id),
            ('text', self.text),
            ('author', self.author),
            ('created_at', self.created_at),
            ('last_updated_at', self.last_updated_at),
            ('stats', self.stats),
            ('gdps_id', self.gdps_id)
        ]
        inner = ', '.join('%s=%r' % t for t in attrs)
        return f'<{self.__class__.__name__} {inner}>'

    @property
    def author(self):
        return Account(self._author)

    @property
    def stats(self):
        return GDPSStats(self._stats)

    def update(self, text):
        """
Requires authorization.

Update your comment on a GDPS
        """
        
        assert isinstance(text, str), 'text must be a string.'
        assert text, 'text can not be empty.'
        body = json.dumps({
            'text': text
        })
        headers = {
            'content-type': 'application/json',
            'authorization': f'Bearer {_authorization.token}'
        }
        r = requests.put(
            url = f'https://gdps.xyz/api/gdps/{self.gdps_id}/comment/{self.id}/',
            data = body,
            headers = headers
        )
        if r.status_code >= 400:
            _raise_for_errors(r)

    @_auth_required
    def delete(self):
        """
Requires authorization.

Delete your comment on a GDPS        
        """
        
        headers = {
            'content-type': 'application/json',
            'authorization': f'Bearer {_authorization.token}'
        }
        r = requests.delete(
            url = f'https://gdps.xyz/api/gdps/{self.gdps_id}/comment/{self.id}/',
            headers = headers
        )
        if r.status_code >= 400:
            _raise_for_errors(r)

    @_auth_required
    def vote(self, vote_type):
        """
Requires authorization.

Vote on comment
        """
        
        assert isinstance(vote_type, int), 'vote type must be an integer.'
        assert vote_type, 'vote type must be like or dislike (1 or 2).'
        param = {
            'type': vote_type
        }
        headers = {
            'content-type': 'application/json',
            'authorization': f'Bearer {_authorization.token}'
        }
        r = requests.post(
            url = f'https://gdps.xyz/api/gdps/{self.gdps_id}/comment/{self.id}/vote/',
            headers = headers,
            params = param
        )
        if r.status_code >= 400:
            _raise_for_errors(r)

    @_auth_required
    def unvote(self):
        """
Requires authorization.

Remove your vote from comment
        """
        
        headers = {
            'content-type': 'application/json',
            'authorization': f'Bearer {_authorization.token}'
        }
        r = requests.delete(
            url = f'https://gdps.xyz/api/gdps/{self.gdps_id}/comment/{self.id}/vote/',
            headers = headers
        )
        if r.status_code >= 400:
            _raise_for_errors(r)
            if r.status_code == 403:
                raise errors.NotFound(r, 'you have not voted.')


class GDPS(TimestampedObject, Voteable, Updateable):
    """
Represents a gdps.xyz GDPS Object

Supports :class:`gdpsxyz.Object` operand types
    """

    __slots__ = (
        '_images',
        '_owner',
        '_links',
        '_stats',
        'is_pre_moderated',
        'is_verified',
        'locale',
        'name',
        'desc'
    )

    def __init__(self, gdps):
        self._images = gdps.get('images')
        self._owner = gdps.get('account')
        self._links = gdps.get('links')
        self._stats = gdps.get('stats')
        self.is_pre_moderated = gdps.get('isPreModerated')
        self.is_verified = gdps.get('isVerified')
        self.locale = gdps.get('locale')
        self.name = gdps.get('name')
        self.desc = gdps.get('desc')
        super().__init__(
            gdps.get('id'),
            gdps.get('timestamps', {}).get('createdOn'),
            gdps.get('timestamps', {}).get('lastUpdatedOn')
        )

    def __repr__(self):
        attrs = [
            ('id', self.id),
            ('name', self.name),
            ('desc', self.desc),
            ('images', self.images),
            ('owner', self.owner),
            ('created_at', self.created_at),
            ('last_updated_at', self.last_updated_at),
            ('links', self.links),
            ('stats', self.stats),
            ('is_pre_moderated', self.is_pre_moderated),
            ('is_verified', self.is_verified)
        ]
        inner = ', '.join('%s=%r' % t for t in attrs)
        return f'<{self.__class__.__name__} {inner}>'

    @property
    def images(self):
        return GDPSImages(self._images)

    @property
    def owner(self):
        return Account(self._owner)

    @property
    def links(self):
        return GDPSLinks(self._links)

    @property
    def stats(self):
        return GDPSStats(self._stats)


    def get_comment(self, comment_id, /):
        """Get GDPS comment by id."""
        assert isinstance(comment_id, int), 'comment id must be an integer.'
        assert comment_id, 'comment id must be positive.'
        r = requests.get(f'https://gdps.xyz/api/gdps/{self.id}/comment/{comment_id}/')
        if r.status_code == 500:
            raise errors.InternalServerError(r, 'a server side error has occured. Contact developers for help.')
        comment = r.json().get('data')
        if isinstance(comment, dict):
            return Comment(comment)
        return None

    @_auth_required
    def create_comment(self, text):
        """
Requires authorization.

Leave a comment on a GDPS
        """
        assert isinstance(text, str), 'comment text must be a string.'
        assert text, 'comment text can not be empty.'
        body = json.dumps({
            'text': text
        })
        headers = {
            'content-type': 'application/json',
            'authorization': f'Bearer {_authorization.token}'
        }
        r = requests.post(
            url = f'https://gdps.xyz/api/gdps/{self.id}/comment/create/',
            data = body,
            headers = headers
        )
        if r.status_code >= 400:
            _raise_for_errors(r)
        comment_id = r.json().get('data')
        return comment_id

    def get_comment_page(self, page, /):
        """Gives you a list of comment pagination"""
        assert isinstance(page, int), 'page must be an integer.'
        assert page, 'page integer must be positive.'
        param = {
            'page': page
        }
        r = requests.get(
            url = f'https://gdps.xyz/api/gdps/{self.id}/comment/all/',
            params = param
        )
        if r.status_code >= 400:
            _raise_for_errors(r)
        comments = r.json().get('data')
        return [Comment(c) for c in comments]

    @_auth_required
    def update(
        self,
        *,
        name = None,
        desc = None,
        link = None,
        dashboard_link = None,
        download_windows = None,
        download_android = None,
        locale = None,
        avatar_url = None,
        background_url = None
    ):
        """
Requires authorization.

Update GDPS informations
        """
        
        body = {
            'name': name,
            'desc': desc,
            'link': link,
            'dashboardLink': dashboard_link,
            'downloadWindowsLink': download_windows,
            'downloadAndroidLink': download_android,
            'locale': locale,
            'avatarUrl': avatar_url,
            'backgroundUrl': background_url
        }
        for i in (
            name, desc, link, dashboard_link,
            download_windows, download_android,
            locale, avatar_url, background_url
        ):
            if i:
                assert isinstance(i, str), 'GDPS update informations must be strings.'
                assert i, 'do not leave argument empty after passing it.'
            else:
                del body[next(islice(body, i, None))]
        headers = {
            'content-type': 'application/json',
            'authorization': f'Bearer {_authorization.token}'
        }
        body = json.dumps(body)
        r = requests.put(
            url = f'https://gdps.xyz/api/gdps/{self.id}',
            data = body,
            headers = headers
        )
        if r.status_code >= 400:
            _raise_for_errors(r)

    @_auth_required
    def delete(self):
        """
Requires authorization.

Delete GDPS
        """
        
        headers = {
            'content-type': 'application/json',
            'authorization': f'Bearer {_authorization.token}'
        }
        r = requests.delete(
            url = f'https://gdps.xyz/api/gdps/{self.id}/',
            headers = headers
        )
        if r.status_code >= 400:
            _raise_for_errors(r)

    @_auth_required
    def vote(self, vote_type):
        """
Requires authorization.

Vote on GDPS
        """
        
        assert isinstance(vote_type, int), 'vote type must be an integer.'
        assert vote_type, 'vote type must be like or dislike (1 or 2).'
        param = {
            'type': vote_type
        }
        headers = {
            'content-type': 'application/json',
            'authorization': f'Bearer {_authorization.token}'
        }
        r = requests.post(
            url = f'https://gdps.xyz/api/gdps/{self.id}/vote/',
            headers = headers,
            params = param
        )
        if r.status_code >= 400:
            _raise_for_errors(r)

    @_auth_required
    def unvote(self):
        """
Requires authorization.

Remove your vote from GDPS       
        """
        
        headers = {
            'content-type': 'application/json',
            'authorization': f'Bearer {_authorization.token}'
        }
        r = requests.delete(
            url = f'https://gdps.xyz/api/gdps/{self.id}/vote/',
            headers = headers
        )
        if r.status_code >= 400:
            _raise_for_errors(r)
            if r.status_code == 403:
                raise errors.NotFound(r, 'you have not voted.')





def get_account(account_id, /):
    """Get gdps.xyz account."""
    assert isinstance(account_id, int), 'account id must be an integer.'
    assert account_id, 'account id must be positive.'
    r = requests.get(url=f'https://gdps.xyz/api/account/{account_id}/')
    if r.status_code == 500:
        raise errors.InternalServerError(r, 'a server side error has occured. Contact developers for help.')
    account = r.json().get('data')
    if isinstance(account , dict):
        return Account(account)
    return None


@_auth_required
def me():
    """
Requires authorization.

Gives you an authorized account.
    """
    headers = {
        'content-type': 'application/json',
        'authorization': f'Bearer {_authorization.token}'
    }
    r = requests.get(url=f'https://gdps.xyz/api/account/me/', headers=headers)
    if r.status_code >= 400:
        _raise_for_errors(r)
    me = r.json().get('data')
    if isinstance(me, dict):
        return MyAccount(me)


# Removed due to captcha

# def register(username, email, password):
#     """
# Register an account on gdps.xyz
#     """
#     for i in username, email, password:
#         assert isinstance(i, str), 'all register args must be strings.'
#         assert i, f'any register arg can not be empty.'
#     body = json.dumps({
#         'username': username,
#         'email': email,
#         'password': password
#     })
#     headers = {
#         'content-type': 'application/json'
#     }
#     r = requests.post(
#         url='https://gdps.xyz/api/account/register/',
#         data = body,
#         headers = headers
#     )
#     if r.status_code >= 400:
#         _raise_for_errors(r)
#         if r.status_code == 403:
#             raise errors.RegistrationError(r, 'username or email is already used.')
#     account_id = r.json().get('data')
#     return account_id

# def activate(email, key):
#     """Activate your account on gdps.xyz"""
#     assert isinstance(email, str), 'email must be a string.'
#     assert isinstance(key, int), 'account activation key must be an integer.'
#     assert email, 'email can not be empty.'
#     assert len(str(key)) == 6, 'key length must be 6.'
#     body = json.dumps({
#         'email': email,
#         'key': key
#     })
#     headers = {
#         'content-type': 'application/json'
#     }
#     r = requests.post(
#         url='https://gdps.xyz/api/account/activate/',
#         data = body,
#         headers = headers
#     )
#     if r.status_code >= 400:
#         _raise_for_errors(r)
#         if r.status_code == 403:
#             raise errors.ActivationError(r, 'invalid key or account is already activated.')

def authorize(email, password):
    """Authorize into your gdps.xyz account"""
    for i in email, password:
        assert isinstance(i, str), 'email and password must be strings.'
        assert i, 'email or password can not be empty.'
    body = json.dumps({
        'email': email,
        'password': password
    })
    headers = {
        'content-type': 'application/json'
    }
    r = requests.post(
        url='https://gdps.xyz/api/account/authorize/',
        data = body,
        headers = headers
    )
    if r.status_code >= 400:
        _raise_for_errors(r)
        if r.status_code == 403:
            raise errors.AuthorizationError(r, 'invalid email or password, or account was not activated.')
    token_session = r.json().get('data')
    return Session(token_session)


# Removed due to captcha

# def send_email_key(email):
#     """Send an email key to restore password"""
#     assert isinstance(email, str), 'email must be a string.'
#     assert email, 'email can not be empty.'
#     body = json.dumps({
#         'email': email
#     })
#     headers = {
#         'content-type': 'application/json'
#     }
#     r = requests.post(
#         url = 'https://gdps.xyz/api/account/restorePassword/create/',
#         data = body,
#         headers = headers
#     )
#     if r.status_code >= 400:
#         _raise_for_errors(r)
#         if r.status_code == 403:
#             raise errors.PasswordRestoreError(r, 'account was not activated. You can try again in 30 minutes.')


# def change_password(email, key, new_password):
#     """Change account password with provided email key"""
#     for i in email, new_password:
#         assert isinstance(i, str), 'email and new password must be strings.'
#         assert i, 'email or password can not be empty.'
#     assert isinstance(key, int), 'key must be an integer.'
#     assert len(str(key)) == 8, 'password change mail-key length must be 8.'

#     body = json.dumps({
#         'email': email,
#         'key': key,
#         'password': new_password
#     })
#     headers = {
#         'content-type': 'application/json'
#     }
#     r = requests.post(
#         url = 'https://gdps.xyz/api/account/',
#         data = body,
#         headers = headers
#     )
#     if r.status_code >= 400:
#         _raise_for_errors(r, exc_of = (404, ))
#         if r.status_code == 403:
#             raise errors.PasswordRestoreError(r, 'account was not activated.')
        # if r.status_code == 404:
        #     raise errors.NotFound(r, 'account or key was not found.')




def get_gdps(gdps_id, /):
    """Get a gdps.xyz GDPS by id"""
    assert isinstance(gdps_id, int), 'GDPS id must be an integer.'
    assert gdps_id, 'GDPS id must be positive.'
    r = requests.get(url=f'https://gdps.xyz/api/gdps/{gdps_id}/')
    if r.status_code == 500:
        raise errors.InternalServerError(r, 'a server side error has occured. Contact developers for help.')
    gdps = r.json().get('data')
    if isinstance(gdps, dict):
        return GDPS(gdps)
    return None


@_auth_required
def create_gdps(
    name,
    desc,
    link,
    *,
    avatar_url = None,
    background_url = None
):
    """
Requires authorization.

Create a GDPS on gdps.xyz
    """
    
    for i in name, desc, link:
        assert isinstance(i, str), 'GDPS main informations must be strings.'
        assert i, 'GDPS main informations can not be empty.'
    body = {
        'name': name,
        'desc': desc,
        'link': link
    }
    if avatar_url:
        assert isinstance(avatar_url, str), 'URLs must be strings.'
        body.update({'avatarUrl': avatar_url})
    if background_url:
        assert isinstance(background_url, str), 'URLs must be strings.'
        body.update({'backgroundUrl': background_url})
    body = json.dumps(body)
    headers = {
        'content-type': 'application/json',
        'authorization': f'Bearer {_authorization.token}'
    }
    r = requests.post(
        url = 'https://gdps.xyz/api/gdps/create/',
        data = body, 
        headers = headers
    )
    if r.status_code >= 400:
        _raise_for_errors(r)
    gdps_id = r.json().get('data')
    return gdps_id


def search_for_gdps(query, page):
    """Search for GDPSs with pagination"""
    assert isinstance(query, str), 'search query must be a string.'
    assert query, 'search query can not be empty.'
    assert isinstance(page, int), 'page must be an integer.'
    assert page, 'page integer must be positive.'
    params = {
        'urlencoded': query,
        'page': page
    }
    r = requests.get(
        url = 'https://gdps.xyz/api/gdps/search',
        params = params
    )
    if r.status_code >= 400:
        _raise_for_errors(r)
    gdps_pagination = r.json().get('data')
    return [GDPS(g) for g in gdps_pagination]

def top():
    """Gives you current GDPS Top"""
    r = requests.get(url='https://gdps.xyz/api/gdps/top/')
    if r.status_code >= 400:
        _raise_for_errors(r)
    top = r.json().get('data')
    return [GDPS(g) for g in top]
