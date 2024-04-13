from dotenv import load_dotenv
import json
from os import getenv
from os.path import abspath, exists, join, pardir
import pathlib

from Notion2Pelican.Notion2Pelican import readDatabase, page_tree_ids
from Notion2Pelican.Notion2Pelican import get_notion_headers, pageid_2_md

dp_TMP = abspath(join(__file__, pardir, pardir, "tmp"))
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
    fp = abspath(join(__file__, pardir, "db.json"))
    if not exists(fp):
        print("downloading db.json")
        res = readDatabase(databaseId=FT_dbid,
                           notion_header=headers,
                           fp=fp)
    else:
        print("loading db.json")
        with open(fp, 'r') as fi:
            fc = fi.read()
        res = json.loads(fc)
    fpst = abspath(join(__file__, pardir, "site_tree.json"))
    if exists(fpst):
        print("site_tree local opening")
        with open(fpst, "r", encoding="utf-8") as fi:
            fc = fi.read()
        site_tree = json.loads(fc)
    else:
        print("downloading site_tree")
        site_tree = page_tree_ids(res, headers, fp=fpst)
    for page in site_tree:
        if page["children"]:
            folder = page["title"]
            for child in page["children"]:
                child_id = child["id"]
                # only seek for the golden page to be tested
                if not child_id == "5a763841-b62f-4388-8ad3-0d41f7bf03f3":
                    continue
                child_title = child["title"]
                fp = abspath(join(__file__, pardir, f"{child_id}.json"))
                # get the page notion structure
                if exists(fp):
                    with open(fp, "r") as fi:
                        page_json = json.loads(fi.read())
                else:
                    page_json = readDatabase(databaseId=child_id,
                                         notion_header=headers,
                                         print_res=False,
                                         fp=fp)
                # generate the front matter needed by pelican
                front_matter = {"title": child_title,
                                "page_id": child_id
                                }
                # generate the markdown
                md = pageid_2_md(front_matter, page_json, debug=False)
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
                else:
                    print(".md generated is without regressions")

if __name__ == "__main__":
    test_import_non_reg()