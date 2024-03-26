import json
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


def readDatabase(databaseId, notion_header, print_res=False):
    """
    Parameters
    -----------
    databaseId: str
        notion id
    notion_header: json
        header sent via REST url
    print_res: bool
        if True prints debug messages

    Returns
    -------
    data: json
        Data structure returned by the Notion API

    Documentation:
    --------------
    curl https://api.notion.com/v1/blocks/16d8004e-5f6a-42a6-9811-51c22ddada12/children?page_size=100 \  # noqa E501
    -H 'Authorization: Bearer '"$NOTION_API_KEY"'' \
    -H "Notion-Version: 2022-06-28"
    """
    read_url = f"https://api.notion.com/v1/blocks/{databaseId}/children?page_size=100"  # noqa E501

    res = requests.request("GET", read_url, headers=notion_header)
    data = res.json()
    html_response = res.status_code

    if html_response == 200:  # res.status_code
        with open('./db.json', 'w', encoding='utf8') as f:
            f.write(json.dumps(data, indent=4))
        if print_res:
            print("print res >>>>>>>>>>>>>")
            print(json.dumps(data, indent=4))
            print("print res <<<<<<<<<<<<<<")
    return data


def page_tree_ids(res, headers):
    """ parses the Notion DB json into a tree

    Parameters
    ----------
    res: json
        json returned by NOTION API
    headers: json
        headers used for parameters in REST API

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
                id1 = b["id"]
                page_title = b["child_page"]["title"]
                res1 = readDatabase(id1, headers, print_res=False)
                children = page_tree_ids(res1, headers)
                children_page = {"title": page_title, "id": id1,
                                 "children": children}
                children_ids.append(children_page)

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
    md = "\n"

    for para in paragraph:
        if para == "rich_text":
            for para_block in paragraph[para]:
                if "text" in para_block:
                    content = para_block["text"]["content"]
                    if para_block["text"]["link"] is not None:
                        link = para_block["text"]["link"]["url"]
                        md += f"[{content}]({link})"
                    else:
                        md += f"{content}"
                if "mention" in para_block:
                    plain_text = para_block["plain_text"]
                    url = para_block["href"]
                    md += f"[{plain_text}]({url})"
    md += "\n"
    return md


def pageid_2_md(front_matter, res):
    """ generates markdown with front matter from notion json

    Parameters
    ----------
    front_matter: json
        the page title as the title is not in the json object
    res: json
        json returned by the NOTION API

    Returns
    --------
    md: str
        Markdown formatted page
    """
    # FIXME: 56c2ac88fa7c49d8859c44ce68eca68b

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
        # print(block["type"])
        btype = block["type"]
        bullet_index = 0
        if btype == "paragraph":  # in block:
            md += para_2_md(block[btype])
        elif btype == "heading_2":  # in block:
            """ "heading_2": {
                    "rich_text": [
                        {
                            "type": "text",
                            "text": {
                                "content": """
            head2 = block["heading_2"]["rich_text"][0]["text"]["content"]
            # print("head2",head2)
            md += f"\n## {head2}\n\n"
        elif btype == "heading_3":  # in block:
            head3 = block["heading_3"]["rich_text"][0]["text"]["content"]
            # print("head2",head2)
            md += f"\n### {head3}\n\n"
        elif btype == "bulleted_list_item":
            # bull = block[btype]["rich_text"]
            bulletpoint = block[btype]["rich_text"][0]["text"]["content"]
            md += f"* {bulletpoint}\n"
        elif btype == "numbered_list_item":
            bulletpoint = block[btype]["rich_text"][0]["text"]["content"]
            if prev_btype == btype:
                bullet_index += 1
            else:
                bullet_index = 1
            md += f"{bullet_index}. {bulletpoint}\n"
        elif btype == "image":
            caption = ""
            for c in block["image"]["caption"]:
                caption += c["plain_text"]
            url = block["image"][block["image"]["type"]]["url"]
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
