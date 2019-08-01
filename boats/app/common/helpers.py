from datetime import datetime
from app.models import InvalidArguments

def validate_point(longitude, latitude):
    if not(-90 <= latitude <= 90 and -180 <= longitude <= 180):
        raise InvalidArguments('Latitude and/or Longitude are out of range')


def validate_and_extract_datetimes(query_string):
    target_ts = query_string.get('target_ts')
    start_ts = query_string.get('start_ts')
    end_ts = query_string.get('end_ts')

    all_ts = [target_ts, start_ts, end_ts]
    for ts in all_ts:
        try:
            ts and not isinstance(datetime.utcfromtimestamp(ts), datetime)
        except TypeError:
            raise InvalidArguments('timestamp arguments must be UTC timestamps')

    target_dt = datetime.utcfromtimestamp(target_ts) if target_ts else None
    start_dt = datetime.utcfromtimestamp(start_ts) if start_ts else None
    end_dt = datetime.utcfromtimestamp(end_ts) if end_ts else None

    return target_dt, start_dt, end_dt
