from glob import glob
import os
from setuptools import find_packages, setup

package_name = 'green_arm'

setup(
    name=package_name,
    version='0.0.0',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
        (os.path.join('share', package_name), glob('launch/*.py')),
        (os.path.join('share', package_name), glob('urdf/*')),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='murchu27',
    maintainer_email='murchu27@yorku.ca',
    description='EECS5324 Project: GreenArm',
    license='Apache-2.0',
    extras_require={
        'test': [
            'pytest',
        ],
    },
    entry_points={
        'console_scripts': [
            'opencv_camera = green_arm.opencv_camera:main',
            'view_camera = green_arm.view_camera:main',
            'yolo_pose = green_arm.yolo_pose:main',
        ],
    },
)
