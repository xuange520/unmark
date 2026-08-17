from setuptools import setup, find_packages

setup(
    name="unmark",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "torch>=2.0.0",
        "transformers>=4.46.0",
        "numpy>=1.20.0",
    ],
    extras_require={
        "dev": ["pytest>=7.0.0", "black>=23.0.0"],
        "web": ["gradio>=4.0.0"],
    },
    entry_points={
        "console_scripts": [
            "unmark=unmark.cli:main",
        ],
    },
    author="Jay",
    author_email="xuangeylw@gmail.com",
    description="A semantics-preserving toolkit for removing and evaluating statistical LLM text watermarks (SynthID-Text, etc.)",
    license="Apache-2.0",
    url="https://github.com/xuange520/unmark",
)
