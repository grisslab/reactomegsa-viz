
import csv
import io
import os
import logging
from math import log10
from importlib import resources 
from jinja2 import Environment, PackageLoader, select_autoescape


# default logger
_LOGGER = logging.getLogger(__name__)


class HtmlReportGenerator:

    @staticmethod
    def create_report(json_dict: dict, r_script_token: str, out_html: str = None, reactome_url: str = "https://gsa.reactome.org") -> str | None:
        """Create a HTML report based on the passed ReactomeGSA result object.

        :param json_dict: The ReactoeGSA result object as a dict.
        :type json_dict: dict
        :param r_script_token: The ReactomeGSA result token / analysis id.
        :type r_script_token: str
        :param out_html: If set, the resulting HTML document will be written to the defined file, defaults to None
                         Note: Throws an exception in case the file exists.
        :type out_html: str, optional
        :param reactome_url: If set, this path will be used to generated ReactomeGSA associated links.
        :type reactome_url: str, optional
        :return: The HTML code as a string or None.
        :rtype: str | None
        
        """        
        # -- Get Reactome Version --
        reactome_version = json_dict["release"]

        # -- Iterate through JSON results to obtain the data in the desired format --
        all_datasets = {}
        for dataset_dict in json_dict["results"]:

            dataset_name = dataset_dict["name"]
            pathways_tsv = dataset_dict["pathways"]
            genes_tsv = dataset_dict["fold_changes"]


            # -- Modify pathways table --

            # Convert TSV into a list of dictionaries
            f = io.StringIO(pathways_tsv)
            reader = csv.DictReader(f, delimiter='\t')

            # Convert to a list to modify it
            modified_list = list(reader)

            # Modify columns 
            for row in modified_list:
                # Rename columns to standard names
                row["pathway_name"] = row.pop("Name")
                row["p_value"] = float(row.pop("PValue"))
                row["fdr"] = float(row.pop("FDR"))
                row["ngenes"] = int(float(row.pop("NGenes")))
                row["direction"] = row.pop("Direction")
                row["pathway_id"] = row.pop("Pathway")
                row["av_foldchange"] = float(row.pop("av_foldchange"))

                
                # Add new columns

                # Calculate -log10 of fdr (handling 0 safely)
                fdr = row["fdr"]
                if fdr > 0:
                    row["neg_log10_adj_pval"] = -log10(fdr)
                else:
                    row["neg_log10_adj_pval"] = 300.0 # Or some other high 'ceiling' value

                row["sig"] = row["fdr"] < 0.05

            pathways_json_output = modified_list


            # -- Modify genes table --

            # Convert TSV into a list of dictionaries
            f = io.StringIO(genes_tsv)
            reader = csv.DictReader(f, delimiter='\t')

            # Convert to a list to modify it
            modified_list = list(reader)

            # Modify columns 
            for row in modified_list:
                # Rename columns to standard names
                row["p_value"] = float(row.pop("P.Value"))
                row["adj_p_value"] = float(row.pop("adj.P.Val"))
                row["log2FC"] = float(row.pop("logFC"))
                row["B"] = float(row.pop("B"))
                row["t"] = float(row.pop("t"))
                row["AveExpr"] = float(row.pop("AveExpr"))

                
                # Add new columns

                # Calculate -log10 of adj_p_value (handling 0 safely)
                adj_p_value = row["adj_p_value"]
                if adj_p_value > 0:
                    row["neg_log10_adj_pval"] = -log10(adj_p_value)
                else:
                    row["neg_log10_adj_pval"] = 300.0 # Or some other high 'ceiling' value

            genes_json_output = modified_list

            all_datasets[dataset_name] = {
                "pathways": pathways_json_output,
                "genes": genes_json_output,
            }


        # Build dataset list
        dataset_ids = sorted(all_datasets.keys())

        r_script_template = """
# This script downloads your recent ReactomeGSA result
# into an R session
#
# Note: The result is only stored for a certain period of time
#       on the ReactomeGSA servers. Therefore, it is highly
#       recommended to store the result locally.
# Install and load the ReactomeGSA package if not available
if (!require(ReactomeGSA)) {{
    if (!requireNamespace("BiocManager", quietly = TRUE))
        install.packages("BiocManager")

    BiocManager::install("ReactomeGSA")
}}

# Load the package
library(ReactomeGSA)

# Load the analysis result
result <- get_reactome_analysis_result(analysis_id = "{token}", reactome_url = "{reactome_url}")

# Save the result
saveRDS(result, file = "my_ReactomeGSA_result.rds")

# Get the overview over all pathways
all_pathways <- pathways(result)
        """.format(token=r_script_token, reactome_url=reactome_url)

        # -- Render Jinja2 template --
        env = Environment(
            loader=PackageLoader("reactomegsa_viz", "assets"),
            autoescape=select_autoescape(['html', 'xml'])
        )

        tpl = env.get_template("report_template.html")

        # Get Reactome logo safely from package assets
        reactome_logo = resources.files("reactomegsa_viz.assets").joinpath("ReactomeGSA_logo.svg").read_text()

        # get the reactome links or use an empty array
        reactome_links = json_dict["reactome_links"] if json_dict["reactome_links"] else []

        rendered = tpl.render(
            reactome_version=reactome_version,
            reactome_links=reactome_links,
            datasets=all_datasets,
            dataset_ids=dataset_ids,
            r_script_template=r_script_template,
            initial_dataset_id=dataset_ids[0] if dataset_ids else None,
            logo_svg=reactome_logo
        )

        # write the file if set
        if out_html:
            if os.path.exists(out_html):
                _LOGGER.error("Failed to write HTML file. Target path ", out_html, " exists")
                raise FileExistsError("Target path exists: ", out_html)

            with open(out_html, "w", encoding="utf-8") as out:
                out.write(rendered)

            _LOGGER.info("HTML report file written to ", out_html)
        else:
            # return the HTML code as a string if no output file was set
            return rendered