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
    i = 0

    for i in range(len(abspath) - 16, 0, -1):
        if abspath[i:i+16] == "auto_coloring_ai":
            break

    if i == 0: return abspath

    return abspath[:i+16]
