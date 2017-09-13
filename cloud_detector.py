#!/usr/bin/env python3

from internals.cloud_detection import get_cloudiness_percentages
from datetime import datetime

# TODO: Use GUI
datetimes, percentages = get_cloudiness_percentages(
                            datetime(2016, 4, 13),
                            datetime(2017, 4, 14),
                            (45, 45), 45, 15,
                            'internals/unlabeled_images',
                            True
                        )

for i in range(len(percentages)):
    print(datetimes[i], percentages[i])
