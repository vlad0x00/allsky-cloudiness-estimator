import numpy as np
import os
import re
import modelutils


def get_cloud_data(directory):
    labeled_output = []
    is_labeled = re.compile(r'.*l\.png$')
    count = 0
    for dirpath, dirnames, filenames in os.walk(directory):
        for f in filenames:
            if is_labeled.match(f):
                imgpath = os.path.join(dirpath, f)
                labeled_output.append(imgpath)
    for labeled in labeled_output:
        in_img = re.sub(r'l\.png$', '.png', labeled)
        count += 1
        if count % 1024 == 0:
            print('Added', count)
        yield (modelutils.load_image(in_img), modelutils.load_image(labeled))
        # print('Number of samples:', len(X))
        # return (np.array(X), np.array(y)[:, :, :, None])
