import os
import shutil

from logger import log


def run(cmd):
    log.debug(cmd)
    return os.popen(cmd).read()


def cut(input_file, output_file, field=0):
    with open(input_file) as input_io, open(output_file, 'w') as output_io:
        for line in input_io:
            output_io.write(line.rstrip().split("\t")[field] + "\n")


def wc(file):
    if not os.path.exists(file) or os.path.isdir(file):
        return None
    count = int(os.popen('wc -l ' + file).read().strip().split()[0])
    # log.debug("File {} has {} lines".format(file, count))
    return count


def ln(file, link):
    link_abs = os.path.abspath(link)
    if not os.path.exists(link_abs):
        run("ln -s {} {}".format(os.path.abspath(file), link_abs))


def wdiff(file1, file2, output_file=None):
    if not os.path.exists(file1):
        log.error("file {} does not exists".format(file1))
        return None
    if not os.path.exists(file2):
        log.error("file {} does not exists".format(file2))
        return None

    if not output_file:
        output_file = file2 + '.wdiff'
    run("wdiff {0} {1} | sed -e :a -e '/-]$/N; s/\\n/ /; ta'"
        " | grep -P '\\[-|{{\+' > {2}".format(file1, file2, output_file))

    return output_file


def is_parallel(file):
    with open(file) as file_io:
        return "\t" in file_io.next().strip()


def filepath(dir, file, noext=True):
    filename = os.path.split(file)[1]
    filebase = os.path.splitext(filename)[0] if noext else filename
    return os.path.join(dir, filebase)
