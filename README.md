# Warehouse project template

You are free to use any tools or programming language, as long as the evidence
used in your report is generated automatically by code and saved in a folder.
This includes KPIs, data tables, the data behind charts, and the charts themselves.

[View the example report PDF](report/example.pdf).

## Course requirements

- Put the original files downloaded from the approved sources in `data/raw/`.
- Provide one entry point that processes those files and saves the evidence
  used in your report.
- Keep your README brief: give the setup, the command to generate the evidence,
  and the folder where it is saved.

Import or copy the generated evidence into your LaTeX report. Organize the
remaining project files to suit your tools.

## Minimal submission structure

A project in your chosen language can use this structure:

```text
project/
├── data/raw/      # original input files
├── src/           # analysis code (or a notebook at the project root)
├── report/        # LaTeX project, evidence, and final PDF
├── README.md      # setup and execution command
└── .gitignore     # local files excluded from Git
```

Save the generated evidence in a documented folder, such as `report/evidence/`.
Choose the dependency files needed by your tools.

## Example structures

The supplied repository includes both entry points below. Choose either one.
They use the same analysis in `src/` and save the same evidence in `artifacts/`.
Each tree shows the files used by that entry point.

### Python script with `src/`

```text
project/
├── data/
│   ├── raw/.gitkeep              # keeps the original-data folder in Git
│   └── sources.json              # approved URLs, filenames, and checksums
├── src/
│   ├── __init__.py               # makes src a Python package
│   ├── generate_artifacts.py     # script entry point
│   └── pipeline.py              # data, analysis, and report functions
├── requirements.txt             # Python analysis dependencies
├── report/
│   ├── main.tex                  # example LaTeX report
│   ├── references.bib            # report bibliography
│   └── example.pdf               # report preview viewable on GitHub
├── README.md                    # setup and execution instructions
└── .gitignore                   # files excluded from Git
```

### Notebook

The notebook is the entry point. In this example, it calls the shared Python
functions in `src/`. You can also write your analysis directly in the notebook.

```text
project/
├── data/
│   ├── raw/.gitkeep              # keeps the original-data folder in Git
│   └── sources.json              # approved URLs, filenames, and checksums
├── analysis.ipynb                # notebook entry point
├── notebook_config.py            # settings for running every cell
├── src/                         # shared analysis called by this notebook
├── requirements.txt             # Python analysis dependencies
├── requirements-notebook.txt     # additional notebook dependencies
├── report/                      # main.tex, references.bib, and example.pdf
├── README.md                    # setup and execution instructions
└── .gitignore                   # files excluded from Git
```

Setup creates `.venv/` for the Python environment. The analysis saves evidence
in `artifacts/`; report compilation saves the PDF there too. The commented
`.gitignore` excludes raw data, environments, caches, and temporary build files.
Keep your finished report assets with the report when preparing your submission.

## Run the supplied Python example

For this example, install [Python](https://www.python.org/downloads/) 3.11 or
newer. Create a repository with **Use this template**, then clone or download
it. You can also select **Code > Download ZIP** and extract the folder.

Open a new terminal in the folder containing this README. Put any approved
original files you already have in `data/raw/` with their original filenames.
The example checks existing files and downloads missing inputs.

### Python script

On Windows, use PowerShell or Command Prompt:

```text
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m src.generate_artifacts
```

On macOS or Linux:

```sh
python3 -m venv .venv
./.venv/bin/python -m pip install -r requirements.txt
./.venv/bin/python -m src.generate_artifacts
```

After setup, run the last command whenever you want to regenerate the evidence.

### Notebook

Create the environment, install the notebook dependencies, register its
kernel, and run the supplied notebook. On Windows:

```text
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements-notebook.txt
.\.venv\Scripts\python.exe -m ipykernel install --sys-prefix --name warehouse-project
.\.venv\Scripts\python.exe -m nbconvert --config notebook_config.py
```

On macOS or Linux, use `python3 -m venv .venv` for the first command and replace
`.\.venv\Scripts\python.exe` with `./.venv/bin/python` in the remaining commands.
The last command executes the notebook from start to finish and saves the
same evidence as the script, plus `artifacts/analysis.executed.ipynb`.

## Outputs from this example

The example downloads the active-location workbook if needed and saves its
outputs in `artifacts/`:

| File | Contents |
|---|---|
| `zone_summary.csv` | Zone measures and chart data |
| `scenario_inventory_factor.csv` | Baseline and illustrative scenario values |
| `zone_locations.png` | Chart of active picking locations by zone |
| Generated `.tex` files | Tables, summary values, and captions used by the report |

Run the command again to check that it reuses the original data. Add your
analyses to [src/generate_artifacts.py](src/generate_artifacts.py) or call them from
it. The [notebook](analysis.ipynb) uses the same function.

## Prepare the report

Start with [report/main.tex](report/main.tex). Each section briefly describes
what it should cover. You are free to organize the discussion within each section.
Generated evidence examples at the end show how to include tables and a chart.
The main sections cover warehouse activity profiling, storage assignment and
space requirements, warehouse layout design, order picking system design, and
performance evaluation and trade-offs. Introduction, methods, and conclusion
sections connect them.
Replace the guidance and examples with your work.

State the finding in each result caption. Give units in table headings and
chart axes. Report the settings used for each comparison and use the same
measures for the baseline and proposed interventions.

**Local LaTeX:** install [TeX Live](https://www.tug.org/texlive/) or
[TinyTeX](https://yihui.org/tinytex/), then open a new terminal. Install the
report packages once:

```sh
tlmgr install latexmk ieeetran booktabs float graphics siunitx url psnfss times amsfonts
```

After generating the evidence, compile from the project root:

```sh
latexmk -g -pdf -interaction=nonstopmode -halt-on-error -outdir=artifacts report/main.tex
```

The PDF is saved as `artifacts/main.pdf`. The repository's preview is a copy
saved as `report/example.pdf`; replace it after rebuilding the example report.

**Overleaf:** make a ZIP with a copy of `report/main.tex` named `main.tex` at
the ZIP root, `report/references.bib`, and the generated `.tex` files and
`zone_locations.png` inside `artifacts/`. Upload it to Overleaf, select
`main.tex` as the main document, and compile with pdfLaTeX. Download the
finished source project and PDF for submission.

## Submit

Before submitting, run your documented command in a clean copy, compare its
outputs with the report, and check that the complete LaTeX project compiles.
Submit the exact Git commit or ZIP, the complete LaTeX project, and the final PDF.
Check the [current course requirements](https://brenobeirigo.github.io/course-wh/assessment/index.html)
and Canvas for assessment criteria, page limits, deadlines, and upload instructions.

## Sources and help

- [Current exercises](https://brenobeirigo.github.io/course-wh/assessment/index.html)
  and [grading rubrics](https://brenobeirigo.github.io/course-wh/admin/syllabus-2026.html#milestone-rubrics).
- [S. P. Richards source data](https://www.warehouse-science.com/wh/projects/spr3/main.html)
  and the [source manifest](data/sources.json). Keep raw data out of public repositories.
- [The Turing Way](https://book.the-turing-way.org/reproducible-research/compendia/),
  [IEEE templates](https://conferences.ieeeauthorcenter.ieee.org/write-your-paper/authoring-tools-and-templates/),
  and [LaTeX writing examples](https://github.com/brenobeirigo/latex-thesis-template#writing-guide-common-elements).
