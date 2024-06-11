# Tools for quick data exploration

Plotting tools for making quick plots of both 1D and 2D MEs for selected runs and lumisections.

The MEs can be retreived in two ways:
- Read from a previously stored `.parquet` file created using the DIALS API. See e.g. the `dialstools/datasets` folder for details and examples. This is the approach of choice when the datasets are large or you have the files already anyway.
- Retrieve directly using the DIALS API in the plotting scripts. This is the easiest approach for quick tests.

Several kinds of plots can be made:
- For 1D MEs: plot a single lumisection, a selected range of lumisections overlaid, or all lumisections in a selected run overlaid. See `plot_me_1d.ipynb`.
- For multiple types of 1D MEs together: same as above, but multiple types in nicely arranged subfigures. See `plot_mes_1d.ipynb`.
- For 2D MEs: plot a single lumisection, or a gif image of a range of selected lumisections (or all lumisections in a selected run). `See plot_me_2d.ipynb`
- Other: to do...
