"""Generic, Extra and Enum gdps.xyz classes module

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

from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime
from enum import Enum, IntEnum

EXTRACLASS = {'init': False}

# Interface for voteable objects
class Voteable(ABC):
    id: int

    __slots__ = ()

    @abstractmethod
    def vote(self, vote_type): ...

    @abstractmethod
    def unvote(self): ...

# Interface for updateable and deleteable objects
class Updateable(ABC):
    id: int

    __slots__ = ()

    @abstractmethod
    def update(self, *args, **kwargs): ...

    @abstractmethod
    def delete(self): ...


@dataclass
class Object:
    """
Represents generic gdps.xyz API object

Supported operand types:
-----------
x == y
    Checks if objects are equal
x != y
    Checks if objects are unequal
str(x)
    Returns object informations in a string

Note: if you want to create your own gdpsxyz object, consider using this class
    """
    __slots__ = ('id', )

    id: int


@dataclass
class TimestampedObject(Object):
    """
Represents a generic gdps.xyz API object with its timestamps

Supports :class:`gdpsxyz.Object` operand types
    """
    __slots__ = ('created_at', 'last_updated_at')

    created_at: int
    last_updated_at: int

    @property
    def created_at_dt(self):
        """:class:`datetime.datetime` object creation"""
        return datetime.fromtimestamp(self.created_at)

    @property
    def last_updated_at_dt(self):
        """:class:`datetime.datetime` object last update"""
        return datetime.fromtimestamp(self.last_updated_at)



@dataclass(**EXTRACLASS)
class SessionIPs:
    """Session IP adresses"""
    __slots__ = ('authorized_ip', 'last_relogin_ip')
    def __init__(self, ips):
        self.authorized_ip = ips.get('authorizedIp')
        self.last_relogin_ip = ips.get('lastReloginIp')

@dataclass(**EXTRACLASS)
class Vote:
    """Represents your vote on a GDPS"""
    __slots__ = ('is_voted', 'vote_type')
    def __init__(self, vote):
        self.is_voted = vote.get('isVoted')
        self.vote_type = vote.get('voteType')

@dataclass(**EXTRACLASS)
class GDPSImages:
    """GDPS's attachments class"""
    __slots__ = ('avatar_url', 'background_url')
    def __init__(self, urls):
        self.avatar_url = urls.get('avatarUrl')
        self.background_url = urls.get('backgroundUrl')

@dataclass(**EXTRACLASS)
class GDPSLinks:
    """Simple class that represents GDPS's links"""
    __slots__ = (
        'download_windows',
        'download_android',
        'dashboard',
        'site'
    )
    def __init__(self, links):
        self.download_windows = links.get('download').get('windows')
        self.download_android = links.get('download').get('android')
        self.dashboard = links.get('dashboard')
        self.site = links.get('site')

@dataclass(**EXTRACLASS)
class GDPSStats:
    """GDPS Stats class"""
    __slots__ = (
        '_vote',
        'likes',
        'dislikes',
        'reviews'
    )
    def __init__(self, stats):
        self._vote = Vote(stats.get('Vote'))
        self.likes = stats.get('likes')
        self.dislikes = stats.get('dislikes')
        self.reviews = stats.get('reviews')



# Enums there

class PermissionLevel(IntEnum):
    """Account permission level on gdps.xyz class"""
    user = 0
    moderator = 1
    administrator = 2

class VoteType(IntEnum):
    """Vote type class"""
    like = 1
    dislike = 2
    not_voted = -1

class Locale(Enum):
    """GDPS supported locales class"""
    russian = 'ru'
    english = 'en'
    none = 'none'