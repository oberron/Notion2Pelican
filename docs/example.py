from dotenv import load_dotenv
from os import getenv
from os.path import abspath, join, pardir
import pkg_resources
import pathlib
import subprocess

from Notion2Pelican.Notion2Pelican import readDatabase, page_tree_ids
from Notion2Pelican.Notion2Pelican import get_notion_headers, pageid_2_md, \
    replace_invalid_characters

dp_TMP = abspath(join(__file__, pardir, pardir, "tmp"))
pathlib.Path(dp_TMP).mkdir(parents=True, exist_ok=True)

# define the content path where blog entries are to be added
dp_content = abspath(join(dp_TMP, "content"))
pathlib.Path(dp_content).mkdir(parents=True, exist_ok=True)
# define the path where the static site will be built
dp_www = abspath(join(dp_TMP, "www"))
pathlib.Path(dp_www).mkdir(parents=True, exist_ok=True)


def check_venv():
    """ Simple hook to ensure local install/ venv
    are actually supporting the CLI pelican build

    Returns
    -------
    run_pelican: bool
        if True all conditions to all Pelican to run are met
    """
    run_pelican = True
    installed_packages = pkg_resources.working_set
    # installed_versionned_packages_list = sorted(["%s==%s" %
    #     (i.key, i.version) for i in installed_packages])
    installed_packages_list = sorted([i.key for i in installed_packages])

    for needed in ["pelican", "markdown"]:
        if needed not in installed_packages_list:
            print(f"missing {needed}")
            run_pelican = False
    return run_pelican


def build_content(local_img=True):
    """ load the secrets needed to download the DB from Notion

    Parameters
    ----------
    local_img: bool
        if True, will attempt to download AWS images locally

    Raises
    ------
    ValueError
        when the 2 secrets are not available, see README for details
    """
    try:
        load_dotenv()
        MY_NOTION_SECRET = getenv("NOTIONKEY")
        PAGE_dbid = getenv("PAGE_dbid")
        assert PAGE_dbid is not None
        assert MY_NOTION_SECRET is not None
    except AssertionError as ex:
        log_msg = "the code expects a venv file or environment variable to" +\
             "have two variables set: NOTIONKEY and PAGE_dbid" +\
             "seems this is not the case in current repository" +\
             "read the README on how to fix this before further attempts " +\
             f"to run this example. Exception message: {str(ex)}"
        print(log_msg)
        raise ValueError(log_msg)

    # create the headers needed by the API
    headers = get_notion_headers(MY_NOTION_SECRET)

    res = readDatabase(databaseId=PAGE_dbid, notion_header=headers)
    site_tree = page_tree_ids(res, headers)
    # the below works with a Notion setup as
    # landing page - the DB ID where FT_dbid points to
    #  |----folder #1
    #       |-----page 0
    #       |-----page 1
    #       |...
    #       |-----page N
    #  |----folder #2
    #       |_____page 1
    #       |...
    #  |...
    for page in site_tree:
        if page["children"]:
            # if the page has children it is then considered as a folder
            folder = page["title"]
            for child in page["children"]:
                # each children in the folder is considered as a page
                # and exported in markdown with frontmatter
                child_id = child["id"]
                child_title = child["title"]

                res_t = readDatabase(databaseId=child_id,
                                     notion_header=headers)
                front_matter = {"title": child_title,
                                "page_id": child_id
                                }
                md = pageid_2_md(front_matter, res_t)
                fn = replace_invalid_characters(f"{folder}_{child_id}.md")
                fp = abspath(join(dp_content, fn))
                with open(fp, 'w', encoding="utf-8") as fo:
                    fo.write(md)


def build_site():
    run_pelican = check_venv()
    if run_pelican:
        subprocess.run(["pelican", dp_content,
                        "-o", dp_www, "-t", "notmyidea"])
    else:
        print("SEE LOGS - missing packages to run properly")


if __name__ == "__main__":
    build_content()
    build_site()
