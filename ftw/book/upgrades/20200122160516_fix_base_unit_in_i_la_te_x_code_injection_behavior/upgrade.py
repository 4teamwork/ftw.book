from ftw.book.behaviors.codeinjection import ILaTeXCodeInjection
from ftw.upgrade import UpgradeStep
from Products.CMFPlone.utils import safe_unicode


class FixBaseUnitInILaTeXCodeInjectionBehavior(UpgradeStep):
    """Fix BaseUnit in ILaTeXCodeInjection behavior.
    """

    def __call__(self):
        self.install_upgrade_profile()

        query = {'object_provides': [ILaTeXCodeInjection.__identifier__]}
        for obj in self.objects(query, 'Fix pre post latex code field'):
            if callable(ILaTeXCodeInjection(obj).pre_latex_code):
                ILaTeXCodeInjection(obj).pre_latex_code = safe_unicode(
                    ILaTeXCodeInjection(obj).pre_latex_code()
                )
            if callable(ILaTeXCodeInjection(obj).post_latex_code):
                ILaTeXCodeInjection(obj).post_latex_code = safe_unicode(
                    ILaTeXCodeInjection(obj).post_latex_code()
                )
