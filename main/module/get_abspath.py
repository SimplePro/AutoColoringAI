import os

abspath = os.path.abspath("./")
abspath = abspath.replace("\\", "/")


def main_abspath():
    i = 0

    for i in range(len(abspath) - 4, 0, -1):
        if abspath[i:i+4] == "main":
            break

    if i == 0: return abspath

    return abspath[:i+4]


def project_abspath():
    abspath = main_abspath()

    return abspath[:-5]
