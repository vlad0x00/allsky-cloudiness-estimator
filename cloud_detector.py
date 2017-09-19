#!/usr/bin/env python3

from internals.cloud_detection import get_cloudiness_percentages
from datetime import datetime, timedelta

TABLE_FILENAME = 'tabele.csv'

# TODO: Use GUI
datetimes, percentages = get_cloudiness_percentages(
                            start_date=datetime(2016, 4, 13),
                            end_date=datetime(2017, 4, 14),
                            center_of_view=(225, 60),
                            width_of_view=60,
                            rotation=15,
                            images_dir='internals/unlabeled_images',
                            interval=timedelta(minutes=30),
                            display_images=True
                         )

if __name__ == '__main__':
    table = open(TABLE_FILENAME, 'w')

    for i in range(len(percentages)):
        print(datetimes[i], percentages[i])
        table.write(datetimes[i] + ', ' + percentages[i] + '\n')

    table.close()
