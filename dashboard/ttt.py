from datetime import datetime
x = datetime(year=2022, month=10, day=24, hour=14, minute=30)-datetime.now()
print(x.total_seconds())