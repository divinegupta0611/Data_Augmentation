from setuptools import setup, find_packages

setup(
    name="smart_augmentation",
    version="0.2.1",
    author="Divine Gupta",
    author_email="guptadivine0611@gmail.com",
    description="Comprehensive image and video data augmentation library with AI-powered recommendations, geometric, color, noise, and occlusion techniques",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    packages=find_packages(),
    install_requires=[
        "opencv-python>=4.5.0",
        "numpy>=1.19.0"
    ],
    python_requires=">=3.7",
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Intended Audience :: Science/Research",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "Topic :: Scientific/Engineering :: Image Processing",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    keywords="image-augmentation video-augmentation data-augmentation computer-vision deep-learning ai machine-learning",
)