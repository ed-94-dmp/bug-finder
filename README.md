## Bug Finder

This Python module counts number of provided bug pattern in the provided landscape pattern.

### Getting started

1. Place bug and landscape files in the `data` folder.
2. Run the script with `python main.py -b bug.txt -l landscape.txt`.

### Some information

1. Script is tested on Python 2.7. Due to the used `with` statement and `ArgParse` module, it is expected not to be
compatible with previous versions. Due to not having quick access to previous versions of Python, I did not replace them
with their alternatives.
2. Due to the nested loops, the complexity is high. Though, there are certain rules implemented to skip some iterations.