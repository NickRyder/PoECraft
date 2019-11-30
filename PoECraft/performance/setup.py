import os

PACKAGE_NAME = 'PoECraft'


def configuration(parent_package='', top_path=None):
    from numpy.distutils.misc_util import Configuration

    config = Configuration(PACKAGE_NAME, parent_package, top_path)

    config.add_extension('_prng',
                         sources=['_prng.c'])
    config.add_extension('_bisect',
                         sources=['_bisect.c'])
    config.add_extension('_draw_affix',
                         sources=['_draw_affix.c'])

    return config


if __name__ == '__main__':
    from numpy.distutils.core import setup
    setup(**configuration(top_path='').todict())
