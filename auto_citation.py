import requests
import xml.etree.ElementTree as ET
import html
import yaml


def extract_dblp_to_yaml():
    url = "https://dblp.org/pid/18/5740.xml"
    print(f"Fetching data from {url}...")
    try:
        response = requests.get(url)
        response.raise_for_status()
    except requests.RequestException as e:
        print(f"Error fetching URL: {e}")
        return

    try:
        root = ET.fromstring(response.content)
    except ET.ParseError as e:
        print(f"Error parsing XML: {e}")
        return

    papers = []

    # 遍历所有 <r> 元素的子元素（出版物）
    # XML 结构是 <dblpperson><r><article> 或 <inproceedings> ...
    for r in root.findall('./r'):
        for pub in r:  # pub 是 <article>, <inproceedings> 等

            # 提取基本信息
            title = pub.find('title')
            title_text = title.text if title is not None else "Unknown Title"
            # 如果存在末尾的点则移除
            if title_text.endswith('.'):
                title_text = title_text[:-1]

            authors = []
            for author in pub.findall('author'):
                if author.text:
                    authors.append(author.text)

            for editor in pub.findall('editor'):
                if editor.text:
                    authors.append(editor.text)

            # 出版社/会议地点
            # 优先级：期刊 -> 论文集 -> 学校（针对论文）
            publisher = "Unknown Publisher"
            journal = pub.find('journal')
            booktitle = pub.find('booktitle')
            school = pub.find('school')

            if journal is not None and journal.text:
                publisher = journal.text
            elif booktitle is not None and booktitle.text:
                publisher = booktitle.text
            elif school is not None and school.text:
                publisher = school.text

            # 日期
            year = pub.find('year')
            year_text = year.text if year is not None else "0000"
            month = pub.find('month')
            month_text = month.text if month is not None else "01"

            # 常见月份映射的简单字典
            month_map = {
                'January': '01', 'February': '02', 'March': '03', 'April': '04',
                'May': '05', 'June': '06', 'July': '07', 'August': '08',
                'September': '09', 'October': '10', 'November': '11', 'December': '12',
                'Jan': '01', 'Feb': '02', 'Mar': '03', 'Apr': '04',
                'Jun': '06', 'Jul': '07', 'Aug': '08',
                'Sep': '09', 'Oct': '10', 'Nov': '11', 'Dec': '12'
            }
            # 清理月份文本
            month_text_clean = month_text.strip()
            # 处理 "January" 或 "Jan" 或纯数字等情况
            if month_text_clean in month_map:
                month_num = month_map[month_text_clean]
            elif month_text_clean.isdigit():
                month_num = month_text_clean.zfill(2)
            else:
                month_num = "01"  # 默认回退

            date_str = f"{year_text}-{month_num}-01"

            # 链接和 ID
            # 首选 'ee'（电子版），通常是 DOI 或 URL
            ee = pub.find('ee')
            if ee is not None and ee.text:
                link = ee.text
            else:
                # 回退到 DBLP URL
                key = pub.get('key')
                link = f"https://dblp.org/{key}"

            # ID：如果可能，尝试使其看起来像 "doi:..."，否则使用唯一的标识符
            # 用户示例：id: doi:10.1109/TKDE.2023.3291006
            paper_id = link
            if "doi.org/" in link:
                # 提取 doi.org/ 之后的部分
                doi_part = link.split("doi.org/")[-1]
                paper_id = f"doi:{doi_part}"
            elif "research.nii.ac.jp" in link or "trec.nist.gov" in link:
                # skip
                continue

            publisher.replace("CoRR", "ArXiv")
            # Haonan Chen 0005 处理作者后面的编号
            for i, author in enumerate(authors):
                if " 00" in author:
                    authors[i] = author.split(" 00")[0]

            # 构建字典
            paper_entry = {
                'id': paper_id,
                'title': title_text,
                'authors': authors,
                'publisher': publisher,
                'date': date_str,
                'link': link,
                'type': 'paper',
                'plugin': 'sources.py',
                'file': 'sources.yaml'
            }
            papers.append(paper_entry)

    # title deduplication
    title_entries = {}
    for paper in papers:
        title = paper['title']
        if title not in title_entries:
            title_entries[title] = paper
        else:
            # 保留非 arXiv 版本
            if title_entries[title]['publisher'] == "ArXiv":
                title_entries[title] = paper
            else:
                # 保留更新的版本
                if paper['date'] > title_entries[title]['date']:
                    title_entries[title] = paper

    # 按日期降序排序（通常做法），或保持 DBLP 顺序（通常是按时间顺序）
    # 让我们按降序排序，以便首先显示最新的
    papers.sort(key=lambda x: x['date'], reverse=True)

    output_path = "sources.yaml"
    with open(output_path, 'w', encoding='utf-8') as f:
        # allow_unicode=True 以保留中文字符（如果有）
        # sort_keys=False 以保持插入顺序（id, title, authors...）
        # 但字典中的插入顺序仅在较新的 Python (3.7+) 中得到保证，这没问题。
        # 如果 yaml 默认不遵守顺序，我们可能需要手动强制执行。

        # 为了美观严格执行字段顺序：
        class OrderedDumper(yaml.SafeDumper):
            pass

        def _dict_representer(dumper, data):
            return dumper.represent_dict(data.items())

        OrderedDumper.add_representer(dict, _dict_representer)

        # 我们按顺序手动构建了字典，所以这应该有效。
        yaml.dump(papers, f, Dumper=OrderedDumper, allow_unicode=True, sort_keys=False, default_flow_style=False)

    print(f"Successfully extracted {len(papers)} papers to {output_path}")


if __name__ == "__main__":
    extract_dblp_to_yaml()
