if __name__ == "__main__":
    headers = get_notion_headers(MY_NOTION_SECRET)
    notion_db_id = MY_NOTION_DB_ID
    res = readDatabase(databaseId=notion_db_id, notion_header=headers)
    site_tree = page_tree_ids(res)
    for page in site_tree:
        if page["children"]:
            folder = page["title"]
            for child in page["children"]:
                child_id = child["id"]
                child_title = child["title"]

                res_t = readDatabase(databaseId=child_id, notion_header=headers, print_res=False)
                front_matter = {"title": child_title,
                                "page_id": child_id
                                }
                md = pageid_2_md(front_matter, res_t)
                fn = replace_invalid_characters(f"{folder}_{child_id}.md")
                with open(f"{fn}", 'w') as fo:
                    fo.write(md)