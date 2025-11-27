from setuptools import setup

package_name = "greenarm_manipulation"

setup(
    name=package_name,
    version="0.1.0",
    packages=[package_name],
    data_files=[
        ("share/ament_index/resource_index/packages",
         ["resource/" + package_name]),
        ("share/" + package_name, ["package.xml"]),
    ],
    install_requires=["setuptools"],
    zip_safe=True,
    maintainer="GreenArm Team",
    maintainer_email="greenArmTeam@york.ca",
    description="Kinova pick-and-place node that subscribes to SourceTarget coordinates.",
    license="NOPE",
    tests_require=["pytest"],
    entry_points={
        "console_scripts": [
            "pickplace_node = greenarm_manipulation.pickplace_node:main",
        ],
    },
)
