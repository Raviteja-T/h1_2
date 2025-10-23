from setuptools import setup

package_name = 'unitree_h1_2_description'

setup(
    name=package_name,
    version='0.0.1',
    packages=[package_name],
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
        ('share/' + package_name + '/launch', ['launch/display.launch.py']),
        ('share/' + package_name, [
            'h1_2.urdf',
            'h1_2_handless.urdf',
            'h1_2.xml',
            'h1_2_handless.xml'
        ]),
        ('share/' + package_name + '/meshes', [
            # optionally list some meshes if needed or copy entire folder in install manually
        ])
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='Raviteja',
    maintainer_email='t.raviteja@gmail.com',
    description='Unitree H1-2 description and lowstate_to_jointstate node',
    license='Apache License 2.0',
    entry_points={
        'console_scripts': [
            'lowstate_to_jointstate_full = unitree_h1_2_description.lowstate_to_jointstate_full:main',
        ],
    },
)
