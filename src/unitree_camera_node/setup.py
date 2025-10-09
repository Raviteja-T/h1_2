from setuptools import setup

package_name = 'unitree_camera_node'

setup(
    name=package_name,
    version='0.1.0',
    packages=[package_name],
    install_requires=['setuptools', 'opencv-python', 'cv_bridge'],
    zip_safe=True,
    author='Raviteja',
    author_email='your_email@example.com',
    description='ROS 2 node to stream Unitree H1-2 front camera using GStreamer',
    license='Apache-2.0',
    tests_require=['pytest'],
   entry_points={
    'console_scripts': [
        'camera_publisher = unitree_camera_node.camera_publisher:main',
    ],
    },
)
