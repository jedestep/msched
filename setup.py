from distutils.core import setup

import sys
import platform
import re

exec(open('version.py').read())

packages = [
          'msched'
        , 'msched.events'
        , 'msched.worker'
        ]


if sys.platform == 'darwin' and 'clang' in platform.python_compiler().lower():
    from distutils.sysconfig import get_config_vars
    res = get_config_vars()
    for key in ('CFLAGS', 'PY_CFLAGS'):
        if key in res:
            flags = res[key]
            flags = re.sub('-mno-fused-madd', '', flags)
            res[key] = flags

setup(
    name='msched',
    version=__version__,
    packages=packages,
    scripts=['scripts/msched'],
    author='Jed Estep',
    author_email='jedestep@gmail.com',
    url='https://github.com/jedestep/msched'
)
