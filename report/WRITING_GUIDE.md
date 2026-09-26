# Writing the management report

The final Warehousing submission is **one report of no more than 12 pages**. It
draws on all five assessed parts: activity profiling, storage assignment, layout,
picking, and trade-off analysis. Organize the pages around a management decision.
The code should retain the detailed evidence even when the report shows only the
figures and tables needed to explain that decision.

The PDF built from `main.tex` is a working example. Its zone table and chart
come from the pipeline. The opening section explains the grading rules, and
the suggested subsections name the evidence expected for each part. The italic
text marks work for your group to complete; it is not evidence or a
recommendation. Remove the guidance and prompts before submitting.

## A useful sequence

| Report section | What the reader needs | Example of the sentence to write |
|---|---|---|
| Abstract and decision | The proposed change, effect, and condition for rollout | “We recommend [change] in [area]. Under [shared assumptions], it changes [measure] by [amount and unit] relative to the current operation. Rollout depends on [check].” |
| Evidence and current operation | Scope, source, unit, period, and checked baseline | “The active-location file contains [N] valid records across [Z] zones. We excluded [n] records with missing zone codes, so Table 1 uses [N valid] records.” |
| Storage, layout, and picking options | What each option changes and how it is modeled | “The storage model assigns [items] to [locations] while respecting [capacity condition]. We estimate [flow parameter] from [source and period].” |
| Matched comparison | Results measured on the same basis, including interactions | “Under the same demand and labor assumptions, option B reduced modeled travel distance by [x]% relative to the current assignment. The estimate excludes replenishment travel.” |
| Recommendation | Sequence, conditions, and monitoring | “Pilot [change] in [area] for [period]. Expand it if [service measure] remains above [threshold] and [cost measure] remains below [threshold].” |
| Sensitivity and limits | Which assumption matters and how it affects the decision | “When [assumption] changes from [a] to [b], the expected saving falls from [x] to [y]. The recommendation still holds because [criterion].” |

These sentences are patterns, not facts about S. P. Richards. Replace every
bracketed value with a measured or justified value. If the evidence does not
support a claimed saving, report the uncertainty instead.

## Make each result checkable

- State the numerator, denominator, units, period, and exclusions for a rate.
- Compare alternatives using the same baseline, demand, labor, and constraints.
  If an assumption differs, explain the reason and isolate its effect.
- Distinguish an observed quantity from a model output and from a management
  judgement. A stock snapshot does not measure picking time.
- Write captions that stand alone. Give the measure, population or sample size,
  units, period, and definitions. Example: “Active locations by zone in the
  DC23ACTIVE snapshot (n = [N] valid location records; units on hand are selling
  units).”
- Refer to each figure or table by its label, then state the decision-relevant
  result in the text. Do not make the reader infer your conclusion from a chart.
- Put complete calculations and intermediate outputs in the code. The report
  should show enough method to assess the result without printing full matrices.

## Tables for settings and results

The report demonstrates three table jobs. Table I records the settings needed
to repeat the calculation. Table II describes the observed inventory. Table III
places an observed value beside an arithmetic example. The example factor does
not estimate demand or evaluate a warehouse policy. Replace that comparison
with tested interventions in the final report.

| Table job | Useful columns | What to say beside it |
|---|---|---|
| Experimental settings | Setting, value, unit or evidence source; group rows by data, model, and scenario | State which settings are fixed across comparisons and which ones change. Give seeds and replications when a simulation uses randomness. |
| Baseline description | Item or zone, count, measured quantity, unit | Name the source period and denominator. Explain the pattern that matters for the decision. |
| Intervention comparison | Option, common outcome measure, absolute change, relative change | State the shared demand and constraints, then give the effect and its practical meaning. |
| Sensitivity | Assumption or scenario, tested value, outcome, decision change | Explain where the recommendation changes or remains valid. |

The experimental-settings table adapts a grouped layout from the course
author's table-design examples. The comparison table adapts a grouped result
header. Both use [booktabs](https://ctan.org/pkg/booktabs) for light horizontal
rules and [siunitx](https://ctan.org/pkg/siunitx) for consistent numbers. A
model with many symbols may also need a separate **symbol, meaning, value**
table so readers can connect each number to the mathematical formulation.

Keep numbers right aligned and use one precision per column. Put units in
headers or row labels, state the population and period in the caption, and
cite the table in the text. Use space and a few horizontal rules to separate
groups. If a table does not fit at readable type size, remove repeated columns,
split the table, or move detailed results to the code.

For example, a result paragraph could read: "With the same demand and labor
inputs, the proposed picking rule reduced modeled travel from [a] to [b] km
per batch, a change of [x]%. The model excludes replenishment trips, so the
team will measure those trips before rollout." The sentence names the baseline,
unit, effect, and limit. Replace the brackets with generated results.

## Why these templates are useful

| Source | Practice to borrow | How this project uses it |
|---|---|---|
| Natural writing notes (author's private repository) | Name the actor and action, use short paragraphs, and support claims with concrete evidence. | Each section asks for a decision or result in plain language before technical detail. |
| Academic writing guide (author's private repository) | Give each paragraph a job. Separate method, observed result, interpretation, and limitation. | The report moves from checked baseline to options, matched comparison, recommendation, and sensitivity. |
| Table-design compendium (author's private repository) | Group settings by purpose, align comparable results, and explain scope in captions. | The generated settings and comparison tables use these layout principles with warehouse data. |
| [LaTeX thesis template](https://github.com/brenobeirigo/latex-thesis-template/blob/main/README.md#writing-guide-common-elements) | Label and cite tables and figures, use clear captions, keep references together, and automate the build. | This shorter IEEE report uses `booktabs`, `\label`/`\ref`, a bibliography, and generated tables. The thesis page layout is designed for a different length of work. |
| TLM assignment template (author's private repository) | Keep calculations traceable while explaining the result beside them. | The pipeline writes checked outputs; the report imports those outputs and interprets only what they show. |

The private repositories are listed to explain the design choices. Students
can use the examples in this repository without access to them.

The [IEEE conference authoring page](https://conferences.ieeeauthorcenter.ieee.org/write-your-paper/authoring-tools-and-templates/)
explains the format used by `IEEEtran`. The course assessment brief controls the
content and 12-page limit. IEEE styling does not replace the course rubric.

## Before submission

Run `all` from a clean checkout. Open the rebuilt PDF and verify each reported
number against the generated CSV or other output. Remove the italic prompts,
check that all figures and tables have captions and are cited in the text, and
confirm that the PDF stays within 12 pages.
