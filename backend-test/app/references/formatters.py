from datetime import datetime, date # Ensure 'date' is imported
import re

def format_authors_gbt7714(authors):
    if not authors:
        return ""
    
    author_names = [author['author_name'] for author in authors]
    if len(author_names) <= 3:
        return ', '.join(author_names)
    else:
        return f"{', '.join(author_names[:3])}, 等"

def format_authors_apa(authors):
    if not authors:
        return ""
    
    def format_author(name):
        parts = name.split()
        if len(parts) <= 1:
            return name
        
        last_name = parts[-1]
        # 处理首字母缩写
        initials = ' '.join([f"{p[0]}." for p in parts[:-1]])
        return f"{last_name}, {initials}"
    
    author_names = [format_author(author['author_name']) for author in authors]
    
    if len(author_names) == 1:
        return author_names[0]
    elif len(author_names) <= 7:
        # APA规范: 最后一个作者前使用"&"
        return ', '.join(author_names[:-1]) + ', & ' + author_names[-1]
    else:
        # APA规范: 超过7个作者，列出前6个，中间省略，然后是最后一个
        return ', '.join(author_names[:6]) + ', ... ' + author_names[-1]

def extract_volume_issue(journal_issue):
    """从期刊期号信息中提取卷号和期号"""
    if not journal_issue:
        return None, None
    
    # 例如: "Vol. 10, Issue 2" 或 "Volume 10, No. 2" 或 "10(2)" 等
    volume_pattern = r'[Vv]o?l\.?\s*(\d+)|^(\d+)\s*[\(\,]'
    issue_pattern = r'[Ii]ssue\s*(\d+)|[Nn]o\.?\s*(\d+)|\((\d+)\)'
    
    volume_match = re.search(volume_pattern, journal_issue)
    issue_match = re.search(issue_pattern, journal_issue)
    
    volume = None
    issue = None
    
    if volume_match:
        for group in volume_match.groups():
            if group:
                volume = group
                break
    
    if issue_match:
        for group in issue_match.groups():
            if group:
                issue = group
                break
                
    # 尝试简单的 "卷(期)" 格式
    if not volume and not issue:
        simple_pattern = r'(\d+)\((\d+)\)'
        simple_match = re.search(simple_pattern, journal_issue)
        if simple_match:
            volume, issue = simple_match.groups()
    
    return volume, issue

def extract_pages(journal_issue):
    """尝试从期刊期号信息中提取页码"""
    if not journal_issue:
        return None, None
    
    # 匹配页码范围
    # 例如: "pp. 123-145" 或 "123-145" 或 "p. 123"
    page_pattern = r'[pP]\.?[pP]?\.?\s*(\d+)(?:\s*[-–]\s*(\d+))?'
    
    page_match = re.search(page_pattern, journal_issue)
    if page_match:
        start_page = page_match.group(1)
        end_page = page_match.group(2) if len(page_match.groups()) > 1 and page_match.group(2) else start_page
        return start_page, end_page
    
    return None, None

def extract_year_from_date_input(date_input):
    if not date_input:
        return ""

    year_val = None

    if isinstance(date_input, (datetime, date)): # Handles datetime.datetime and datetime.date
        year_val = date_input.year
    elif isinstance(date_input, str):
        processed_str = date_input.strip()
        if not processed_str:
            return ""

        # Case 1: String like "YYYY-MM-DD HH:MM:SS" or "YYYY-MM-DD"
        if ' ' in processed_str:
            processed_str = processed_str.split(' ')[0]  # Get the date part
        
        if '-' in processed_str:
            parts = processed_str.split('-')
            if len(parts[0]) == 4 and parts[0].isdigit():
                try:
                    year_val = int(parts[0])
                except ValueError:
                    pass # Should not happen if isdigit() is true
        # Case 2: String is just "YYYY"
        elif len(processed_str) == 4 and processed_str.isdigit():
            try:
                year_val = int(processed_str)
            except ValueError:
                pass
        else:
            # Case 3: More complex string, try regex
            year_match = re.search(r'\b(19\d{2}|20\d{2}|[1-9]\d{3})\b', processed_str)
            if year_match:
                try:
                    year_val = int(year_match.group(0))
                except ValueError:
                    pass
            else:
                # Fallback: try parsing with common datetime formats if regex fails
                for fmt in ("%Y", "%Y-%m", "%Y-%m-%d", "%Y/%m/%d", "%b %Y", "%B %Y", "%m/%d/%Y"):
                    try:
                        dt_obj = datetime.strptime(processed_str, fmt)
                        year_val = dt_obj.year
                        break
                    except ValueError:
                        continue
    
    return str(year_val) if year_val is not None else ""


def format_date_gbt7714(date_input):
    return extract_year_from_date_input(date_input)

def format_date_apa(date_input):
    return extract_year_from_date_input(date_input)

def format_reference_gbt7714(document, authors):
    """
    按GB/T 7714-2015格式生成期刊论文的参考文献
    格式：作者. 题名[J]. 刊名, 出版年份, 卷号(期号): 起始页码-终止页码. DOI
    """
    try:
        authors_text = format_authors_gbt7714(authors)
        title = document.get('title', '')
        date = format_date_gbt7714(document.get('publication_date', ''))
        journal_name = document.get('container_name', '')
        journal_issue = document.get('journal_issue', '')
        doi = document.get('doi', '')
        
        # 提取卷号和期号
        volume, issue = extract_volume_issue(journal_issue)
        # 提取页码
        start_page, end_page = extract_pages(journal_issue)
        
        reference = ""
        
        # 作者部分
        if authors_text:
            reference += f"{authors_text}. "
        
        # 标题部分
        if title:
            reference += f"{title}"
        
        # 期刊标志
        reference += "[J]. "
        
        # 期刊名称
        if journal_name:
            reference += f"{journal_name}, "
        
        # 年份
        if date:
            reference += f"{date}"
            
        # 卷期信息
        if volume or issue:
            if reference[-1] != ' ':
                reference += ", "
                
            if volume:
                reference += f"{volume}"
                
            if issue:
                reference += f"({issue})"
        
        # 页码部分
        if start_page:
            reference += f": {start_page}"
            if end_page and end_page != start_page:
                reference += f"-{end_page}"
        
        # DOI部分
        if doi:
            if reference[-1] != '.' and reference[-1] != ' ':
                reference += ". "
            elif reference[-1] == ' ':
                reference = reference[:-1] + ". "
            reference += f"DOI: {doi}"
        
        # 确保句尾有句点
        if not reference.endswith('.'):
            reference += "."
        
        return reference.strip()
    
    except Exception as e:
        # print(f"格式化GB/T参考文献出错: {e}")
        return document.get('title', '格式化错误')

def format_reference_apa(document, authors):
    """
    按APA格式生成期刊论文的参考文献
    格式：Author, A. A., & Author, B. B. (Year). Title of article. Name of Journal, Volume(Issue), pp-pp. https://doi.org/xxxx
    """
    try:
        authors_text = format_authors_apa(authors)
        title = document.get('title', '')
        date = format_date_apa(document.get('publication_date', ''))  # 确保只返回年份
        journal_name = document.get('container_name', '')
        journal_issue = document.get('journal_issue', '')
        doi = document.get('doi', '')
        
        # 提取卷号和期号
        volume, issue = extract_volume_issue(journal_issue)
        # 提取页码
        start_page, end_page = extract_pages(journal_issue)
        
        reference = ""
        
        # 作者部分
        if authors_text:
            reference += f"{authors_text} "
        
        # 年份部分，括号包围 - 确保只显示年份
        if date:
            reference += f"({date}). "
        else:
            reference += "(n.d.). "  # "no date"
        
        # 标题部分 - APA规范只有第一个词和专有名词首字母大写
        if title:
            # 简单方案：保持原有大小写
            reference += f"{title}. "
        
        # 期刊名称部分 - 斜体
        if journal_name:
            reference += f"<em>{journal_name}</em>"
            
            # 卷号（斜体）和期号部分
            if volume:
                reference += f", <em>{volume}</em>"
                
            if issue:
                reference += f"({issue})"
            
            # 页码部分
            if start_page:
                reference += f", {start_page}"
                if end_page and end_page != start_page:
                    reference += f"-{end_page}"
            
            reference += ". "
        
        # DOI链接部分
        if doi:
            if doi.startswith('http'):
                reference += doi
            elif doi.startswith('doi:') or doi.startswith('DOI:'):
                clean_doi = doi.replace('doi:', '').replace('DOI:', '').strip()
                reference += f"https://doi.org/{clean_doi}"
            else:
                reference += f"https://doi.org/{doi}"
        
        return reference.strip()
    
    except Exception as e:
        # print(f"格式化APA参考文献出错: {e}")
        return document.get('title', '格式化错误')
