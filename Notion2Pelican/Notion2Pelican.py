import json
from os.path import abspath, join, pardir
import requests
import re


def get_notion_headers(token):
    """ gives the headers as needed by Notion API

    Parameters
    ----------
    token: str
        the token given by Notion API integration
    Returns
    -------
    headers: json
        the headers needed by the API
    """
    headers = {
        "Authorization": "Bearer " + token,
        "Content-Type": "application/json",
        "Notion-Version": "2022-06-28"
        }
    return headers


def readDatabase(databaseId, notion_header, print_res=False, fp=None):
    """ reads the database (identified by Notion with databaseId) and returns the structure as a json

    Parameters
    -----------
    databaseId: str
        notion id
    notion_header: json
        header sent via REST url
    print_res: bool
        if True prints debug messages
    fp: str
        file path where the json result should be saved, defaults to "db.json"

    Returns
    -------
    data: json
        Data structure returned by the Notion API

    Documentation:
    --------------
    curl https://api.notion.com/v1/blocks/16d8004e-5f6a-42a6-9811-51c22ddada12/children?page_size=100  # noqa E501
    -H 'Authorization: Bearer '"$NOTION_API_KEY"'' \
    -H "Notion-Version: 2022-06-28"
    """
    read_url = f"https://api.notion.com/v1/blocks/{databaseId}/children?page_size=100"  # noqa E501

    if fp is None:
        fp = abspath(join(__file__, pardir, "db.json"))

    res = requests.request("GET", read_url, headers=notion_header)
    data = res.json()
    html_response = res.status_code

    if html_response == 200:  # res.status_code
        with open(fp, 'w', encoding='utf8') as f:
            f.write(json.dumps(data, indent=4))
        if print_res:
            print("print res >>>>>>>>>>>>>")
            print(json.dumps(data, indent=4))
            print("print res <<<<<<<<<<<<<<")
    else:
        print("failed to download db: html_response={html_response}")
        print(res)
    return data


def page_tree_ids(res, headers, fp=None):
    """ parses the Notion DB json into a tree

    Parameters
    ----------
    res: json
        json returned by NOTION API
    headers: json
        headers used for parameters in REST API
    fp: str
        file path where the json result should be saved, defaults to "db.json"
    Returns
    -------
    children_ids : list of dict
        each dict is a page title, page id and list of children
    """

    children_ids = []
    for b in res["results"]:
        page_title = ""
        if "child_page" in b:
            if b["has_children"]:
                print(98)
                id1 = b["id"]
                page_title = b["child_page"]["title"]
                res1 = readDatabase(id1, headers, print_res=False)
                children = page_tree_ids(res1, headers)
                children_page = {"title": page_title, "id": id1,
                                 "children": children}
                children_ids.append(children_page)

    if fp is None:
        fp = abspath(join(__file__, pardir, "page_id.json"))
    with open(fp, "w", encoding="utf-8") as fo:
        fo.write(json.dumps(children_ids, indent=4))
    return children_ids


def para_2_md(paragraph):
    """ Convets Notion Paragraph to markdown string

    Parameters
    ----------
    paragraph: dict
        dict of various values from notion paragraph definition

    Returns
    -------
    md: str
        markdown encoded in string version of the paragrap
    """
    md = ""

    for para in paragraph:
        if para == "rich_text":
            for para_block in paragraph[para]:
                if "text" in para_block:
                    content = para_block["text"]["content"]
                    if para_block["text"]["link"] is not None:
                        link = para_block["text"]["link"]["url"]
                        md += f"[{content}]({link})"
                    else:
                        # md += f"{content}"
                        raw_content = content
                        for annotation in para_block["annotations"]:
                            if para_block["annotations"][annotation]:
                                if annotation == "bold":
                                    raw_content = f"**{raw_content}**"
                                elif annotation == "italic":
                                    raw_content = f"*{raw_content}*"
                                elif annotation == "strikethrough":
                                    raw_content = f"~~{raw_content}~~"
                                elif annotation == "underline":
                                    raw_content = f"__{raw_content}__"
                        md += raw_content
                if "mention" in para_block:
                    plain_text = para_block["plain_text"]
                    url = para_block["href"]
                    md += f"[{plain_text}]({url})"
    # md += "\n"
    return md


def get_img(url, dpo):
    """ attempts to download the image locally, upon success returns the path
    if failed returns None

    Parameters
    ----------
    url: str
        the url path on AWS with temp token used by Notion
    dpo: str
        the path where the image should be serialized if download successful

    Returns
    -------
    fpo: str
        if None indicates failed download, else the path where the image is
    """
    import os
    from urllib.parse import urlparse
    from requests import get

    a = urlparse(url)
    # Output:
    # /7f35e08f-716e-4cce-94e2-2f47dac447ed/890539ef-92c9-4fa8-9422-1e0c589cdab5/
    # New_York_Stock_Exchange_-_panoramio.jpg
    fn = os.path.basename(a.path)
    # Output: 09-09-201315-47-571378756077.jpg
    # > New_York_Stock_Exchange_-_panoramio.jpg
    fp = abspath(join(dpo, fn))
    fpo = None
    res = get(url)
    if res.ok:
        with open(fp, mode="wb") as fo:
            fo.write(res.content)
        fpo = fn
    return fpo


def pageid_2_md(front_matter, res,
                dp_img=None, rsc_folder="",
                debug=False):
    """ generates markdown with front matter from notion json

    Parameters
    ----------
    front_matter: json
        the page title as the title is not in the json object
    res: json
        json returned by the NOTION API
    dp_img: str
        the path where images should be stored once downloaded
    rsc_folder: str
        the path prefix to be added to the filename for pelican to generate
        appropriate hmtl
    debug: bool
        if True outputs more info

    Returns
    --------
    md: str
        Markdown formatted page
    """

    img_local = False
    if dp_img is not None:
        img_local = True

    known_btype = ["bulleted_list_item",
                   "heading_1", "heading_2", "heading_3", "image",
                   "numbered_list_item", "paragraph", "quote"]

    if "status" not in front_matter:
        front_matter["status"] = "published"

    md = f"""---
title: {front_matter['title']}
id: {res["results"][0]['id']}
author_id: {res["results"][0]["created_by"]["id"]}
status: {front_matter['status']}
date: {res["results"][0]["created_time"]}
last_updated: {res["results"][0]['last_edited_time']}
---

"""

    md += f"# {front_matter['title']}\n\n"
    prev_btype = ""

    for block in res["results"]:
        btype = block["type"]
        if btype not in known_btype:
            print(f"unknown btype: {btype}")
        if debug:
            print("btype", btype)
        md_txt = para_2_md(block[btype])

        if btype != "numbered_list_item":
            bullet_index = 0

        if btype == "paragraph":  # in block:
            md += f"\n{md_txt}\n"
        elif btype == "heading_1":
            md += f"\n# {md_txt}\n\n"
        elif btype == "heading_2":  # in block:
            """ "heading_2": {
                    "rich_text": [
                        {
                            "type": "text",
                            "text": {
                                "content": """
            head2 = md_txt
            # print("head2",head2)
            md += f"\n## {head2}\n\n"
        elif btype == "heading_3":  # in block:
            head3 = md_txt
            # print("head2",head2)
            md += f"\n### {head3}\n\n"
        elif btype == "bulleted_list_item":
            # bull = block[btype]["rich_text"]
            bulletpoint = md_txt
            md += f"* {bulletpoint}\n"
        elif btype == "numbered_list_item":
            bulletpoint = md_txt
            # print("!!!!!!!!!!!!!", prev_btype, btype, bullet_index)
            if prev_btype == btype:
                bullet_index += 1
                md += f"{bullet_index}. {bulletpoint}\n"
            else:
                bullet_index = 1
                md += f"\n{bullet_index}. {bulletpoint}\n"
        elif btype == "quote":
            quote_text = md_txt
            md += f"\n> {quote_text}\n"
        elif btype == "image":
            caption = ""
            for c in block["image"]["caption"]:
                caption += c["plain_text"]
            url = block["image"][block["image"]["type"]]["url"]
            if img_local:
                fn = get_img(url, dp_img)
                img = f"![{caption}]({rsc_folder}{fn})\n\n"
            else:
                img = f"![{caption}]({url})\n\n"
            md += img
        prev_btype = btype
    return md


def replace_invalid_characters(filename):
    # Define a regular expression pattern to match invalid characters
    invalid_char_pattern = re.compile(r'[<>:"/\\|?*\x00-\x1F]')

    # Define a substitute character for invalid characters
    substitute_char = '_'

    # Replace invalid characters with the substitute character
    cleaned_filename = re.sub(invalid_char_pattern, substitute_char, filename)

    return cleaned_filename
