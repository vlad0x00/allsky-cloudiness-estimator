#!/usr/bin/env python3

from internals.cloud_detection import get_cloudiness_percentages
from datetime import datetime
import os

# TODO: Use GUI
datetimes, percentages = get_cloudiness_percentages(
                            datetime(2017, 4, 13),
                            datetime(2017, 4, 14),
                            0, 0, 0,
                            os.path.dirname(os.path.abspath(__file__)) + '/internals/unlabeled_images'
                        )

for i in range(len(percentages)):
    print(datetimes[i], percentages[i])
