"""Execute the example notebook and save its outputs in artifacts/."""

c = get_config()  # Provided by nbconvert when loading this file.
c.NbConvertApp.notebooks = ["analysis.ipynb"]
c.NbConvertApp.export_format = "notebook"
c.NbConvertApp.output_base = "analysis.executed"
c.FilesWriter.build_directory = "artifacts"
c.ExecutePreprocessor.enabled = True
c.ExecutePreprocessor.kernel_name = "warehouse-project"
c.ExecutePreprocessor.timeout = 600
c.ExecutePreprocessor.force_raise_errors = True
