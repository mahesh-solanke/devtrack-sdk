def read_version():
    with open("devtrack_sdk/__version__.py") as f:
        for line in f:
            if line.startswith("__version__"):
                delim = '"' if '"' in line else "'"
                return line.split(delim)[1]


version = read_version()
