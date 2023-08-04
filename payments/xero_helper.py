from requests_oauthlib import OAuth2Session
from next_door_backend import settings
import requests
def get_xero_oauth2_session(token=None):
    return OAuth2Session(
        client_id="9F801E1DE2FE42A88330D5DBE80F0692",
        token=token
    )

def refresh_xero_tokens(refresh_token):
    oauth = get_xero_oauth2_session()
    token = oauth.refresh_token(
        'https://identity.xero.com/connect/token',
        refresh_token=refresh_token,
        client_id="9F801E1DE2FE42A88330D5DBE80F0692",
        client_secret="XsrSRBuNuqUJKqb1-56hZIW6hc29NIO7GxafbsLzF6diAQtF"
    )
    return token
