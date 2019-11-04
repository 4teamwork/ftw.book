from ftw.book.tests import FunctionalTestCase


class TestTableLaTeXView(FunctionalTestCase):

    def test_grid_layout_table(self):
        self.table.border_layout = 'grid'
        self.assert_latex_code(
            self.table,
            r'''
\label{path:/plone/the-example-book/historical-background/china/population}
\makeatletter\@ifundefined{tablewidth}{\newlength\tablewidth}\makeatother
\setlength\tablewidth\linewidth
\addtolength\tablewidth{-6\tabcolsep}
\renewcommand{\arraystretch}{1.4}
\begin{center}
Population
\end{center}
\vspace{-\baselineskip}
\begin{tabular}{p{0.34\tablewidth}p{0.33\tablewidth}p{0.33\tablewidth}}
\hline
\multicolumn{1}{|p{0.34\tablewidth}|}{\raggedright \textbf{Ranking}} & \multicolumn{1}{|p{0.33\tablewidth}|}{\raggedright \textbf{City}} & \multicolumn{1}{|p{0.33\tablewidth}|}{\raggedright \textbf{Population}} \\
\hline
\multicolumn{1}{|p{0.34\tablewidth}|}{1} & \multicolumn{1}{|p{0.33\tablewidth}|}{Guangzhou} & \multicolumn{1}{|p{0.33\tablewidth}|}{44 mil \textsuperscript{1}} \\
\hline
\multicolumn{1}{|p{0.34\tablewidth}|}{2} & \multicolumn{1}{|p{0.33\tablewidth}|}{Shanghai} & \multicolumn{1}{|p{0.33\tablewidth}|}{35 mil} \\
\hline
\multicolumn{1}{|p{0.34\tablewidth}|}{3} & \multicolumn{1}{|p{0.33\tablewidth}|}{Chongqing} & \multicolumn{1}{|p{0.33\tablewidth}|}{30 mil} \\
\hline
\end{tabular}\\
\vspace{4pt}

\vspace{0pt}
{\footnotesize \textsuperscript{1} thats quite big}
        ''')

    def test_invisible_layout_table(self):
        self.table.border_layout = 'invisible'
        self.assert_latex_code(
            self.table,
            r'''
\label{path:/plone/the-example-book/historical-background/china/population}
\makeatletter\@ifundefined{tablewidth}{\newlength\tablewidth}\makeatother
\setlength\tablewidth\linewidth
\addtolength\tablewidth{-6\tabcolsep}
\renewcommand{\arraystretch}{1.4}
\begin{center}
Population
\end{center}
\vspace{-\baselineskip}
\begin{tabular}{p{0.34\tablewidth}p{0.33\tablewidth}p{0.33\tablewidth}}
\multicolumn{1}{p{0.34\tablewidth}}{\raggedright \textbf{Ranking}} & \multicolumn{1}{p{0.33\tablewidth}}{\raggedright \textbf{City}} & \multicolumn{1}{p{0.33\tablewidth}}{\raggedright \textbf{Population}} \\
\multicolumn{1}{p{0.34\tablewidth}}{1} & \multicolumn{1}{p{0.33\tablewidth}}{Guangzhou} & \multicolumn{1}{p{0.33\tablewidth}}{44 mil \textsuperscript{1}} \\
\multicolumn{1}{p{0.34\tablewidth}}{2} & \multicolumn{1}{p{0.33\tablewidth}}{Shanghai} & \multicolumn{1}{p{0.33\tablewidth}}{35 mil} \\
\multicolumn{1}{p{0.34\tablewidth}}{3} & \multicolumn{1}{p{0.33\tablewidth}}{Chongqing} & \multicolumn{1}{p{0.33\tablewidth}}{30 mil} \\
\end{tabular}\\
\vspace{4pt}

\vspace{0pt}
{\footnotesize \textsuperscript{1} thats quite big}
        ''')

    def test_fancy_listing_layout_table(self):
        self.table.border_layout = 'fancy_listing'
        self.assert_latex_code(
            self.table,
            r'''
\label{path:/plone/the-example-book/historical-background/china/population}
\makeatletter\@ifundefined{tablewidth}{\newlength\tablewidth}\makeatother
\setlength\tablewidth\linewidth
\addtolength\tablewidth{-6\tabcolsep}
\renewcommand{\arraystretch}{1.4}
\begin{center}
Population
\end{center}
\vspace{-\baselineskip}
\begin{tabular}{p{0.34\tablewidth}p{0.33\tablewidth}p{0.33\tablewidth}}
\multicolumn{1}{p{0.34\tablewidth}}{\raggedright \textbf{Ranking}} & \multicolumn{1}{p{0.33\tablewidth}}{\raggedright \textbf{City}} & \multicolumn{1}{p{0.33\tablewidth}}{\raggedright \textbf{Population}} \\
\hline
\multicolumn{1}{p{0.34\tablewidth}}{1} & \multicolumn{1}{p{0.33\tablewidth}}{Guangzhou} & \multicolumn{1}{p{0.33\tablewidth}}{44 mil \textsuperscript{1}} \\
\hline
\multicolumn{1}{p{0.34\tablewidth}}{2} & \multicolumn{1}{p{0.33\tablewidth}}{Shanghai} & \multicolumn{1}{p{0.33\tablewidth}}{35 mil} \\
\hline
\multicolumn{1}{p{0.34\tablewidth}}{3} & \multicolumn{1}{p{0.33\tablewidth}}{Chongqing} & \multicolumn{1}{p{0.33\tablewidth}}{30 mil} \\
\hline
\end{tabular}\\
\vspace{4pt}

\vspace{0pt}
{\footnotesize \textsuperscript{1} thats quite big}
            ''')
