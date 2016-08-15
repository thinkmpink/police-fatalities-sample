*Document*

Each document is a list of victim names where the incident occurred during
or before the month given by the document title.

`combine_names.py` collects all current sources (right now limited to Fatal Encounters and 
Wiki Killings) of victim names and collects a set of unique date-name tuples, writing the
names to a file:
- `4_2015_names.tsv` contains names where the incident date was prior to the argument 
month end date, i.e. names of all the victims prior to May 1, 2015. 
- `<dataset>_name_date.tsv` contains only the lowercase version of `<dataset>_names.tsv`, 
but contains the incident date in addition to the name. 
- `<dataset>_names_strict_month.tsv` contains the names of all the victims for only the
argument month. This is needed for precision/recall evaluation in e.g. `pr_eval.py`

Sources for names include the following files (some are untracked):

* `fe_names.tsv` contains dates and names from our copy of the Fatal Encounters database.
* `wk_names.tsv` contains dates and names from our copy of the Wikipedia record of police killings.
* `wk_names_only.tsv` contains the same as the previous file, except only names, no dates.

