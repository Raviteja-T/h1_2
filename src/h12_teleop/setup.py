from setuptools import setup
import os
from glob import glob

package_name = 'h12_teleop'

setup(
    name=package_name,
    version='0.0.0',
    packages=[package_name],
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
        (os.path.join('share', package_name, 'launch'), glob('launch/*.launch.py')),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='Raviteja Tirumalapudi',
    maintainer_email='t.raviteja@gmail.com',
    description='H1_2 Humanoid Robot Teleoperation Package',
    license='Apache-2.0',
    tests_require=['pytest'],
    entry_points={
        'console_scripts': [
            'h12_teleop_node = h12_teleop.h12_teleop_node:main',
            'keyboard_teleop_node = h12_teleop.keyboard_teleop_node:main',
            'unitree_bridge_node = h12_teleop.unitree_bridge_node:main',
        ],
    },
)