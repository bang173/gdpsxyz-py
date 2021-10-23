"""
gdps.xyz API Wrapper
by bangakek

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

Example 1:
---------

Get gdps infos::

    import gdpsxyz

    galaxium = gdpsxyz.get_gdps(1)

    print(f'gdps.one: {galaxium.name}, {galaxium.owner.username} :  {galaxium.desc}')

    comments = galaxium.get_comment_page(1)
    for comment in comments:
        print(f'{comment.author.username} | {comment.created_at_dt} :  {comment.text}')

Example 2:
-------------

Leave a comment and vote on GDPS and close session::

    import gdpsxyz

    # make sure your account is registered and activated
    with gdpsxyz.authorize('averagenjoyer@gdps.xyz', 'biggestsecret') as my_session:
        me = gdpsxyz.me()
        print(f'Logged in as {me.username}')
        print(f'Session info: {my_session.info}')

        galaxium = gdpsxyz.get_gdps(1)

        galaxium.create_comment('Hello!')
        galaxium.vote(vote_type=gdpsxyz.VoteType.like)
"""

__all__ = (
    'Object',
    'TimestampedObject',
    'SessionIPs',
    'Vote',
    'GDPSImages',
    'GDPSLinks',
    'GDPSStats',
    'PermissionLevel',
    'VoteType',
    'Locale',
    'Account',
    'MyAccount',
    'Session',
    'SessionInfo',
    'Comment',
    'GDPS',
    # 'register',
    # 'activate',
    'authorize',
    # 'send_email_key',
    # 'change_password',
    'me',
    'top',
    'get_gdps',
    'get_account',
    'create_gdps',
    'search_for_gdps',
    'errors'
)

__title__ = 'gdpsxyz'
__author__ = 'bangakek'
__license__ = 'MIT'
__copyright__ = 'Copyright 2021-present bangakek'
__version__ = '0.0.1 beta'

from .xyz import (
    Object,
    TimestampedObject,
    SessionIPs,
    Vote,
    GDPSImages,
    GDPSLinks,
    GDPSStats,
    PermissionLevel,
    VoteType,
    Locale
)
from .api import (
    Session,
    SessionInfo,
    Account,
    MyAccount,
    authorize,
    # register,
    # activate,
    # send_email_key,
    # change_password,
    get_account,
    me,
    GDPS,
    Comment,
    get_gdps, 
    create_gdps,
    search_for_gdps,
    top
)
from . import errors