from dotenv import load_dotenv
import json
from os import getenv
from os.path import abspath, exists, join, pardir
import pathlib
import requests

from pandas import DataFrame

from Notion2Pelican.Notion2Pelican import readDatabase, page_tree_ids
from Notion2Pelican.Notion2Pelican import get_notion_headers, pageid_2_md

dp_TMP = abspath(join(__file__, pardir, pardir, "tmp"))
pathlib.Path(dp_TMP).mkdir(parents=True, exist_ok=True)


def test_import_csv_non_reg():
    """ Example of how to download a databased into a csv
    """

    load_dotenv()
    MY_NOTION_SECRET = getenv("NOTIONKEY_CSV")
    PAGE_dbid = getenv("CSV_DBID")
    DB_ID = getenv("DB_ID")

    headers = get_notion_headers(MY_NOTION_SECRET)
    db_filter = {}

    fn_csv = "db_csv.json"
    fp_csv = abspath(join(dp_TMP, fn_csv))

    db_filter = {}

    headers = get_notion_headers(MY_NOTION_SECRET)
    # query DB columns information
    read_url = f"https://api.notion.com/v1/databases/{DB_ID}"  # noqa E501
    res = requests.request("GET", read_url, headers=headers)

    # 2. get the DB values
    if exists(fp_csv):
        print("loading", fp_csv)
        with open(fp_csv) as fi:
            data = fi.read()
        data = json.loads(data)
    else:
        print("writing", fp_csv)
        read_url = f"https://api.notion.com/v1/databases/{PAGE_dbid}/query"  # noqa E501
        res = requests.request("POST", read_url, headers=headers,
                               data=db_filter)
        # 3. serialize the data
        data = res.json()
        # print(json.dumps(data, indent=4))
        with open(fp_csv, 'w') as fo:
            fo.write(json.dumps(data, indent=4))

    # 4. process the data

    csv_rows = []
    for r in data["results"]:
        properties = r["properties"]
        row = {}
        for prop in properties:
            if prop == "Date":
                if r["properties"][prop]["date"] is None:
                    row["Date"] = None
                else:
                    row["Date"] = r["properties"][prop]["date"]["start"]
            if prop == "":
                if r["properties"][prop]["multi_select"]:
                    row["Name"] = r["properties"][prop]["multi_select"][0]["name"]  # noqa E501
                else:
                    row["Name"] = "?"
            if prop == "Property":
                row["Value"] = r["properties"][prop]["number"]
        csv_rows.append([row["Date"], row["Name"], row["Value"]])
    df = DataFrame(data=csv_rows, columns=["Date", "Name", "Value"])
    fpo = join(dp_TMP, "DB.html")
    df.to_html(fpo)
    fpo = join(dp_TMP, "DB.csv")
    df.to_csv(fpo)
    assert df[df["Date"] == "2023-07-10"]["Value"].iloc[0] == 10.0


def test_import_page_non_reg():
    """ Non regression testing with a private Notion page
    comparing the output to the golden reference to ensure non-regression
    of the notion 2 markdown conversion

    Raises
    ------
    AssertionError
        if the generated .md is not the expected one, possible regression.
    """
    load_dotenv()
    MY_NOTION_SECRET = getenv("NOTIONKEY")
    PAGE_dbid = getenv("PAGE_dbid")

    headers = get_notion_headers(MY_NOTION_SECRET)
    db_page = "db.json"
    fp = abspath(join(dp_TMP, db_page))
    fpst = abspath(join(dp_TMP, "site_tree.json"))
    if not exists(fp):
        print("downloading db.json")
        res = readDatabase(databaseId=PAGE_dbid,
                           notion_header=headers,
                           fp=fp)
    else:
        print("loading db.json")
        with open(fp, 'r') as fi:
            fc = fi.read()
        res = json.loads(fc)
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
            # NOTE: the folder variable can be used to store
            # pages in different folders based on teh parent page
            # name in Notion
            # folder = page["title"]
            for child in page["children"]:
                child_id = child["id"]
                ref_id = "5a763841-b62f-4388-8ad3-0d41f7bf03f3"
                # only seek for the golden page to be tested
                if not child_id == ref_id:
                    # print("skipping child_id", child_id)
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
                md = pageid_2_md(front_matter, page_json,
                                 debug=False, rsc_folder="../img/",
                                 dp_img=dp_TMP)
                # load the golden reference for comparison
                # check against golden generated file stored locally

                fp_ref = abspath(join(__file__, pardir, f"{ref_id}.md"))
                with open(fp_ref) as fo:
                    fc = fo.read()
                try:
                    assert md == fc
                except AssertionError:
                    print("failed here")
                    fp_err = abspath(join(__file__, pardir,
                                          f"{ref_id}_fail.md"))
                    # if failed store the result for checking
                    print("fperr", fp_err)
                    with open(fp_err, 'w') as fo:
                        fo.write(md)
                    raise
                else:
                    print(".md generated is without regressions")
