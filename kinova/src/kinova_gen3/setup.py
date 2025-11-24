from setuptools import find_packages, setup

package_name = 'kinova_gen3'

setup(
    name=package_name,
    version='0.0.0',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='jenkin',
    maintainer_email='jenkin@yorku.ca',
    description='TODO: Package description',
    license='TODO: License declaration',
    tests_require=['pytest'],
    entry_points={
        'console_scripts': [
            'kinova_gen3_node = kinova_gen3.kinova_gen3_node:main',
            'kinova_gen3_tester = kinova_gen3.kinova_gen3_tester:main',
        ],
    },
)
