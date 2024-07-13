import datetime as dt
import dateutil.parser


DTTM_FORMAT = '%Y-%m-%dT%H:%M:%SZ'


def str_to_datetime(dttm_str: str) -> dt.datetime:
    return dateutil.parser.parse(dttm_str)
