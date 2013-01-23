from ftw.pdfgenerator.interfaces import IPDFAssembler
from zope.component import getMultiAdapter
import os
import re
import shlex
import subprocess
import tempfile


def export_pdf(obj, target_path):
    with open(target_path, 'w+') as target:
        assembler = getMultiAdapter((obj, obj.REQUEST),
                                    IPDFAssembler)

        target.write(assembler.build_pdf())


def diff_pdfs(result_path, expectation_path, difference_path):
    basename = os.path.splitext(os.path.basename(result_path))[0]
    temp = tempfile.mkdtemp(suffix='ftw.book-diff_pdfs-%s' % basename)

    resimages = os.path.join(temp, 'result-images')
    eximages = os.path.join(temp, 'expectation-images')
    diffimages = os.path.join(temp, 'diff-images')

    os.mkdir(resimages)
    os.mkdir(eximages)
    os.mkdir(diffimages)

    run('convert %s %s/page.png' % (result_path, resimages))
    run('convert %s %s/page.png' % (expectation_path, eximages))

    assert os.listdir(resimages) == os.listdir(eximages), 'different page amount not supported yet'

    failed_pages = []

    for name in os.listdir(resimages):
        _out, err = run(('compare -metric PSNR %(resimages)s/%(name)s '
                              '%(eximages)s/%(name)s %(diffimages)s/%(name)s') % locals())

        if err.strip() != 'inf':
            page = re.match('page-([\d]*).png', name).groups()[0]
            failed_pages.append(int(page) + 1)

    run('convert %s/* %s' % (diffimages, difference_path))
    return failed_pages

def run(cmd):
    __traceback_info__ = 'Running command: %s' % cmd
    proc = subprocess.Popen(shlex.split(cmd),
                            stderr=subprocess.PIPE,
                            stdout=subprocess.PIPE)

    output, errors = proc.communicate()
    exitcode = proc.poll()

    assert exitcode == 0, 'COMMAND FAILED: %s\n\n%s\n%s' % (cmd, output, errors)
    return output, errors
