from setuptools import setup, find_packages

setup(
    name="d_augmentation",
    version="0.1.2",
    author="Divine Gupta",
    author_email="guptadivine0611@gmail.com",
    description="Comprehensive image data augmentation library with geometric, color, noise, and occlusion techniques",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    packages=find_packages(),
    install_requires=["opencv-python", "numpy"],
    python_requires=">=3.7",
)
