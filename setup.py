from setuptools import setup, find_packages

def load_requirements(path):
    requirements = []
    with open(path) as f:
        for line in f.readlines():
            line = line.strip()
            if line.startswith("git+") or line.startswith("https:"):
                continue
            elif line.startswith("-r "):
                requirements += load_requirements(line[3:])
            else:
                requirements.append(line)
    return requirements


required_packages = load_requirements("./requirements.txt")



setup(
    name='ImageTranslator',
    version='0.1a',
    url='https://github.com/A2va/ImageTranslator.git',
    author='A2va',
    description='An image translator packages',
    packages=find_packages(),    
    install_requires=required_packages
)