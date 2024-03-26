from dotenv import load_dotenv
from os import getenv
from os.path import abspath, join, pardir
import pathlib

from Notion2Pelican.Notion2Pelican import readDatabase, page_tree_ids
from Notion2Pelican.Notion2Pelican import get_notion_headers, pageid_2_md

dp_TMP = abspath(join(__file__, pardir, pardir, "out"))
pathlib.Path(dp_TMP).mkdir(parents=True, exist_ok=True) 

def test_import_non_reg():
    """ Non regression testing with a private Notion page
    comparing the output to the golden reference to ensure non-regression
    of the notion 2 markdown conversion
    """
    load_dotenv()
    MY_NOTION_SECRET = getenv("NOTIONKEY")
    FT_dbid = getenv("FT_dbid")

    headers = get_notion_headers(MY_NOTION_SECRET)
    res = readDatabase(databaseId=FT_dbid,
                       notion_header=headers)
    site_tree = page_tree_ids(res, headers)
    for page in site_tree:
        if page["children"]:
            folder = page["title"]
            for child in page["children"]:
                child_id = child["id"]
                # only seek for the golden page to be tested
                if not child_id == "5a763841-b62f-4388-8ad3-0d41f7bf03f3":
                    continue
                child_title = child["title"]

                # get the page notion structure
                res_t = readDatabase(databaseId=child_id,
                                     notion_header=headers,
                                     print_res=False)
                # generate the front matter needed by pelican
                front_matter = {"title": child_title,
                                "page_id": child_id
                                }
                # generate the markdown
                md = pageid_2_md(front_matter, res_t)
                # load the golden reference for comparison
                # check against golden generated file stored locally

                fp = abspath(join(__file__, pardir, f"{child_id}.md"))
                with open(fp) as fo:
                    fc = fo.read()
                try:
                    assert md == fc
                except:
                    print("failed here")
                    # if failed store the result for checking
                    with open(f"{child_id}_fail.md", 'w') as fo:
                        fo.write(md)
                    raise

if __name__ == "__main__":
    test_import_non_reg()