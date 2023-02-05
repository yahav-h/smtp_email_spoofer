from requests_oauthlib import OAuth2Session
from dataclasses import dataclass, field, asdict
import json

@dataclass
class _oauth:
    aad: OAuth2Session = field(init=False, default=OAuth2Session)
    def __repr__(self): return "<CS:OAuth %r>" % asdict(self)


oauth = _oauth()
