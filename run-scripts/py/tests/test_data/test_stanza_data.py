"""Holds test data"""

TEST_FORMATED_STANZA_DATA = (
    "[default]\n"
    "ACCESS              udp/209040\n"
    "ALLOW_IP            10.10.10.10\n"
    "HMAC_KEY_BASE64     HMACKEYBASE64jhghgfhgfhgfh\n"
    "KEY_BASE64          KEYBASE64fdgfdgdfgfdgfdg\n"
    "SPA_SERVER          a.spa-server.com\n"
    "SPOOF_USER          Test user\n"
    "USE_HMAC            Y\n"
)

TEST_FORMATED_STANZA_DATA_RESOLVE = (
    "[default]\n"
    "ACCESS              udp/209040\n"
    "ALLOW_IP            resolve\n"
    "HMAC_KEY_BASE64     HMACKEYBASE64jhghgfhgfhgfh\n"
    "KEY_BASE64          KEYBASE64fdgfdgdfgfdgfdg\n"
    "SPA_SERVER          a.spa-server.com\n"
    "SPOOF_USER          Test user\n"
    "USE_HMAC            Y\n"
)
