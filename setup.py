from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as f:
    long_description = f.read()

setup(
    name="smart_augmentation",
    version="0.2.3",
    author="Divine Gupta",
    author_email="guptadivine0611@gmail.com",
    description="Comprehensive image and video data augmentation library with recommendations, geometric, color, noise, and occlusion techniques",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/divinegupta0611/Data_Augmentation",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
    ],
    python_requires=">=3.7",
)
