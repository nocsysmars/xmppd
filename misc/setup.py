import os, subprocess
from setuptools import setup, find_packages

here = os.path.dirname(os.path.realpath(__file__))
wdir = here #os.path.join(here, 'my_gnmi_server')
desc_str=''
if os.path.exists(wdir):
    git_hash = subprocess.check_output(['git', 'rev-parse', '--short', 'HEAD'], cwd=wdir)

    # use the git hash in the setup
    desc_str = 'git hash [ %s ]' % git_hash.strip()

dependencies = [
]

setup(
    name='xmppd',
    install_requires=dependencies,
    version='0.1',
    description=desc_str,
    packages=find_packages(),
    license='Apache 2.0',
    author='',
    author_email='',
    entry_points={
        'console_scripts': [
            'xmppd = xmppd.xmppd:main'
        ]
    },
    data_files = [
        ('/etc/systemd/system/', ['xmppd.service']),
        ('/etc/xmppd/', ['config.ini'])
    ],
    maintainer='',
    maintainer_email='',
    classifiers=[
        'Intended Audience :: Developers',
        'Operating System :: Linux',
        'Programming Language :: Python',
    ],

)
