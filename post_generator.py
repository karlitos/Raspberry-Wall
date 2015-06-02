import random
import time
from os.path import dirname, join
from glob import glob

TEXT = 'Lorem ipsum dolor sit amet, consetetur sadipscing elitr, sed diam nonumy eirmod tempor invidunt ut' \
               ' labore et dolore magna aliquyam erat, sed diam voluptua. At vero eos et accusam et justo duo dolores' \
               ' et ea rebum. Stet clita kasd gubergren, no sea takimata sanctus est Lorem ipsum dolor sit amet.'
PERSONS = ['John', 'Kathrine', 'Angela', 'Robert']

IMAGE_EXTENSIONS = [ 'jpg', 'jpeg', 'png', 'bmp', 'gif']

IMAGES = []

for extension in IMAGE_EXTENSIONS:
    IMAGES.extend(glob(join(dirname(__file__), 'media') + '/*.' + extension))

NUMBER_OF_POSTS = 50


def generate_new_data():
        posts = []
        for x in range(NUMBER_OF_POSTS):
            post = random.choice(['image', 'text'])
            if 'image' in post:
                posts.append({
                    'viewclass': 'ImagePost',
                    'image_path': random.choice(IMAGES),
                    'timestamp': '{}.  '.format(x) + time.asctime(),
                    'from_person': random.choice(PERSONS),
                    'height': 300
                })
            else:
                posts.append({
                    'viewclass': 'TextPost',
                    'label_text': TEXT[0:random.randint(10, len(TEXT))],
                    'timestamp': '{}.  '.format(x) + time.asctime(),
                    'from_person': random.choice(PERSONS),
                    'height': 200
                })
        return posts