from setuptools import setup, find_packages

setup(
    name='yandex_neurosupport',
    version='0.1.0',
    packages=find_packages(),
    install_requires=[
        'requests>=2.25.0',
    ],
    author='Timur Sukharev',
    author_email='tsukharev@yandex-team.ru',
    description='Клиент для Yandex NeuroSupport API: обертка для индексации документов и генеративных ответов',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    # url='https://github.com/yourusername/yandex-indexer',
    classifiers=[
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
    python_requires='>=3.8',
    keywords='yandex api neurosupport client supportgpt',
)
