from setuptools import setup

package_name = 'h1_2_camera_py'

setup(
    name=package_name,
    version='0.1.0',
    packages=[package_name],
    data_files=[
        ('share/' + package_name, ['package.xml']),
        ('share/ament_index/resource_index/packages', ['resource/' + package_name]),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='TIRUMALAPUDI Raviteja',
    maintainer_email='raviteja@example.com',
    description='ROS 2 Python node for Unitree H1-2 camera streaming',
    license='Apache License 2.0',
    tests_require=['pytest'],
    entry_points={
        'console_scripts': [
            'h1_camera_node = h1_2_camera_py.h1_camera_node:main'
        ],
    },
)
