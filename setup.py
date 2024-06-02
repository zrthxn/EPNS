from setuptools import setup, find_packages

setup(
    name='epns',
    version='1.0.0',
    packages=find_packages(),
    
    # Descriptions
    description='Equivariant Neural Simulators for Stochastic Spatiotemporal Dynamics.',
    long_description=open('README.md', 'r').read(),
    long_description_content_type='text/markdown',
)