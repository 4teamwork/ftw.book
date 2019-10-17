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

        latex = assembler.render_latex()
        latex = latex.replace(r'\today', '[DATE]')

        builder = assembler.get_builder()
        replace_date_in_directory(builder.build_directory)
        pdf = builder.build(latex)

        target.write(pdf)


def replace_date_in_directory(dirpath):
    """Replaces all \@date and \today in *.cls and *.tex files in the
    directory `dirpath`.
    """

    for filename in os.listdir(dirpath):
        name, ext = os.path.splitext(filename)
        if ext not in ('.cls', '.tex'):
            continue

        path = os.path.join(dirpath, filename)
        content = open(path).read()
        content = content.replace(r'\@date', '[DATE]')
        content = content.replace(r'\today', '[DATE]')

        with open(path, 'w+') as file_:
            file_.write(content)


def diff_pdfs(result_path, expectation_path, difference_path):
    test_image_magick_commands()

    basename = os.path.splitext(os.path.basename(result_path))[0]
    temp = tempfile.mkdtemp(suffix='ftw.book-diff_pdfs-%s' % basename)

    resimages = os.path.join(temp, 'result-images')
    eximages = os.path.join(temp, 'expectation-images')
    diffimages = os.path.join(temp, 'diff-images')
    empty_page = os.path.join(os.path.basename(__file__),
                              'books', 'empty-page.png')

    os.mkdir(resimages)
    os.mkdir(eximages)
    os.mkdir(diffimages)

    run('convert -density 50 -quality 50 -strip %s %s/page.png' % (result_path, resimages))
    run('convert -density 50 -quality 50 -strip %s %s/page.png' % (expectation_path, eximages))

    failed_pages = []

    for name in set(os.listdir(resimages)) & set(os.listdir(eximages)):
        rimg = os.path.join(resimages, name)
        if not os.path.exists(rimg):
            rimg = empty_page

        eimg = os.path.join(eximages, name)
        if not os.path.exists(eimg):
            eimg = empty_page

        _out, err = run(('compare -metric PSNR %(rimg)s '
                         '%(eimg)s %(diffimages)s/%(name)s') % locals(),
                        ignore_exit_code=True)

        if err.strip() != 'inf':
            page = re.match('page-([\d]*).png', name).groups()[0]
            failed_pages.append(int(page) + 1)

    run('convert %s/* %s' % (diffimages, difference_path))
    return failed_pages


def test_image_magick_commands():
    for cmd in ('convert', 'compare'):
        try:
            run('which %s' % cmd)
        except AssertionError:
            raise AssertionError(
                ('The command "%s" could not be found. '
                 'Please install ImageMagick properly. '
                 'See http://cactuslab.com/imagemagick/') % cmd)


def run(cmd, ignore_exit_code=False):
    __traceback_info__ = 'Running command: %s' % cmd
    proc = subprocess.Popen(shlex.split(cmd),
                            stderr=subprocess.PIPE,
                            stdout=subprocess.PIPE)

    output, errors = proc.communicate()
    exitcode = proc.poll()

    if not ignore_exit_code:
        assert exitcode == 0, 'COMMAND FAILED: %s\n\n%s\n%s' % (cmd, output, errors)
    return output, errors
