from setuptools import setup

package_name = "greenarm_perception"

setup(
    name=package_name,
    version="0.1.0",
    packages=[package_name],
    data_files=[
        ("share/ament_index/resource_index/packages",
         ["resource/" + package_name]),
        ("share/" + package_name, ["package.xml"]),
        ("share/" + package_name + "/msg", ["msg/SourceTarget.msg"]),
    ],
    install_requires=["setuptools"],
    zip_safe=True,
    maintainer="GreenArm Team",
    maintainer_email="placeholder@example.com",
    description="Publishes Kinova-ready pick targets derived from ArUco detections.",
    license="MIT",
    tests_require=["pytest"],
    entry_points={
        "console_scripts": [
            "source_detector = greenarm_perception.source_detector:main",
        ],
    },
)
