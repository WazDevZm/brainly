#!/usr/bin/env python3
"""
Setup script for AI Hand Gesture Recognition App
"""

from setuptools import setup, find_packages

setup(
    name="hand-gesture-app",
    version="1.0.0",
    description="AI-powered hand gesture recognition with computer vision",
    author="Your Name",
    author_email="your.email@example.com",
    packages=find_packages(),
    install_requires=[
        "opencv-python==4.8.1.78",
        "mediapipe==0.10.7",
        "numpy==1.24.3",
        "Pillow==10.0.1",
        "pyautogui==0.9.54",
        "pynput==1.7.6"
    ],
    python_requires=">=3.8",
    entry_points={
        "console_scripts": [
            "hand-gesture-app=hand_gesture_app:main",
        ],
    },
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
)
