import datetime as dt
import dateutil.parser


DTTM_FORMAT = '%Y-%m-%dT%H:%M:%SZ'


def str_to_datetime(dttm_str: str) -> dt.datetime:
    if not dttm_str:
        return dt.datetime(1970, 1, 1)
    return dateutil.parser.parse(dttm_str)
