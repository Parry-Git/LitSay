import os
import json
import uuid
import re
import time
import pandas as pd
import requests
from PyPDF2 import PdfReader
from flask import request, jsonify, current_app, g
from werkzeug.utils import secure_filename
from google import genai
from openai import OpenAI

from . import parse_bp
from app.db import query_db, get_db, close_db
from app.utils.decorators import login_required

# 允许上传的文件类型
ALLOWED_PDF_EXTENSIONS = {'pdf'}
ALLOWED_METADATA_EXTENSIONS = {'json', 'csv', 'xlsx'}

def allowed_file(filename, allowed_extensions):
    """检查文件是否具有允许的扩展名"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in allowed_extensions

def extract_doi_from_text(text):
    """
    从文本中提取DOI
    DOI格式通常为 10.xxxx/yyyy 的形式
    """
    # DOI正则表达式模式
    doi_pattern = r'\b(10\.\d{4,}(?:\.\d+)*\/(?:(?!["&\'])\S)+)\b'
    match = re.search(doi_pattern, text)
    if match:
        return match.group(0)
    return None

def get_metadata_from_crossref(doi):
    """
    从Crossref API获取元数据
    """
    if not doi:
        return None

    start_time = time.time()

    try:
        # 构建Crossref API URL
        url = f"https://api.crossref.org/works/{doi}"
        headers = {
            'User-Agent': 'LitSay/1.0 (mailto:admin@litsay.com)'  # 遵循Crossref API指南添加User-Agent
        }

        response = requests.get(url, headers=headers)

        if response.status_code != 200:
            # print(f"Crossref API error: {response.status_code}")
            return None, time.time() - start_time

        data = response.json()

        if 'message' not in data:
            return None, time.time() - start_time

        message = data['message']

        # 提取元数据
        metadata = {
            "title": message.get('title', [''])[0] if isinstance(message.get('title', []), list) else message.get('title', ''),
            "authors": [],
            "sequence": [],  # 注意一般只会返回"first"或"additional"
            "institutions": [],
            "institution_location": [],
            "email": [],
            "doi": message.get('DOI', ''),
            "publishDate": None,
            "journal": None,
            "conference": None,
            "keywords": message.get('subject', []),
        }

        # 提取日期
        if 'published-print' in message and 'date-parts' in message['published-print']:
            date_parts = message['published-print']['date-parts'][0]
            if len(date_parts) >= 3:
                metadata["publishDate"] = f"{date_parts[0]:04d}-{date_parts[1]:02d}-{date_parts[2]:02d}"
            elif len(date_parts) >= 2:
                metadata["publishDate"] = f"{date_parts[0]:04d}-{date_parts[1]:02d}-01"
            elif len(date_parts) >= 1:
                metadata["publishDate"] = f"{date_parts[0]:04d}-01-01"

        # 提取作者
        if 'author' in message:
            for author in message['author']:
                given = author.get('given', '')
                family = author.get('family', '')
                name = f"{given} {family}".strip()

                if not name:
                    continue

                metadata['authors'].append(name)

                # 提取作者角色(如果有)
                sequence = author.get('sequence', '-')
                metadata['sequence'].append(sequence)

                # 提取机构(如果有)
                affiliations = author.get('affiliation', [])
                if affiliations:
                    institution = affiliations[0].get('name', '')
                    location = f"{affiliations[0].get('city', '')}, {affiliations[0].get('country', '')}".strip(', ')
                else:
                    institution = ''
                    location = ''

                metadata['institutions'].append(institution)
                metadata['institution_location'].append(location)

                # 电子邮件通常不在Crossref中提供
                metadata['email'].append('')

        # 提取期刊或会议信息
        container_title = message.get('container-title', [''])[0] if isinstance(message.get('container-title', []), list) else message.get('container-title', '')
        if message.get('type') == 'journal-article':
            metadata['journal'] = container_title
        elif message.get('type') in ['proceedings-article', 'conference-paper']:
            metadata['conference'] = container_title

        # 计算查询时间，但还没想好前端怎么呈现这个时间orz
        query_time = time.time() - start_time

        return metadata, query_time

    except Exception as e:
        current_app.logger.error(f"Crossref API query error: {e}")
        return None, time.time() - start_time

def extract_metadata_from_pdf(file_path):
    """
    从PDF提取元数据（通过提取前两页内容获取DOI，然后使用Crossref API）
    """
    try:
        # 打开PDF并读取前两页
        reader = PdfReader(file_path)
        text = ""

        # 提取前两页内容
        max_pages = min(2, len(reader.pages))
        for i in range(max_pages):
            page = reader.pages[i]
            text += page.extract_text() + "\n"

        # 提取DOI
        doi = extract_doi_from_text(text)

        if not doi:
            # 如果未找到DOI，返回基本元数据
            current_app.logger.warning(f"No DOI found in PDF: {file_path}")
            return {
                "title": os.path.basename(file_path).replace('.pdf', ''),
                "authors": [],
                "doi": None,
                "publishDate": None,
                "journal": None,
                "conference": None,
                "keywords": [],
                "queryTime": 0,
            }

        # 使用DOI查询Crossref
        metadata, query_time = get_metadata_from_crossref(doi)

        if metadata:
            # 添加查询时间信息
            metadata["queryTime"] = round(query_time, 2)  # 四舍五入到2位小数
            return metadata
        else:
            # 如果未能获取元数据，返回基本信息
            return {
                "title": os.path.basename(file_path).replace('.pdf', ''),
                "authors": [],
                "doi": doi,  # 返回找到的DOI
                "publishDate": None,
                "journal": None,
                "conference": None,
                "keywords": [],
                "queryTime": round(query_time, 2),
            }
    except Exception as e:
        current_app.logger.error(f"PDF元数据提取错误: {e}")
        return None

def extract_metadata_using_gemini_ai(file_path):
    """
    Extracts metadata from a PDF using an AI model.
    """
    ai_response_text_for_logging = ""
    try:
        reader = PdfReader(file_path)
        pdf_text = ""
        num_pages_to_extract = min(2, len(reader.pages))
        for i in range(num_pages_to_extract):
            page = reader.pages[i]
            extracted_page_text = page.extract_text()
            if extracted_page_text:
                pdf_text += extracted_page_text + "\n"

        if not pdf_text.strip():
            current_app.logger.warning(f"AI Metadata Extraction: No text could be extracted from PDF: {file_path}")
            return {
                "title": f"AI解析失败 (无文本内容): {os.path.basename(file_path).replace('.pdf', '')}",
                "authors": [], "sequence": [], "institutions": [], "institution_location": [], "email": [],
                "doi": None, "publishDate": None, "journal": None, "conference": None, "keywords": []
            }

        max_chars = 15000
        if len(pdf_text) > max_chars:
            pdf_text = pdf_text[:max_chars]

        prompt = f"""
        You are an expert academic metadata extractor. Your task is to extract metadata from the provided text of a research paper.
        Return the output STRICTLY as a single, valid JSON object. Do not include any explanatory text, comments, or markdown formatting (like ```json) before or after the JSON.

        The JSON object must have the following keys:
        - "title": (string) The main title of the paper. If not found, use null.
        - "authors": (list of strings) Full names of the authors. If no authors are found, use an empty list [].
        - "sequence": (list of strings) Corresponding sequence for each author (e.g., "first", "corresponding", "additional"). This list MUST be the same length as the "authors" list. Use an empty string "" for an author if their sequence is not specified. If "authors" is an empty list, this should also be an empty list.
        - "institutions": (list of strings) Primary affiliation/institution for each author. This list MUST be the same length as the "authors" list. Use an empty string "" for an author if their institution is not specified. If "authors" is an empty list, this should also be an empty list.
        - "institution_location": (list of strings) Location of the institution (e.g., "City, Country") for each author. This list MUST be the same length as the "authors" list. Use an empty string "" for an author if their institution location is not specified. If "authors" is an empty list, this should also be an empty list.
        - "email": (list of strings) Email address for each author. This list MUST be the same length as the "authors" list. Use an empty string "" for an author if their email is not specified. If "authors" is an empty list, this should also be an empty list.
        - "doi": (string) The Digital Object Identifier (e.g., "10.xxxx/yyyyy"). If not found, use null.
        - "publishDate": (string) The publication date in YYYY-MM-DD format. If only year or year-month is available, normalize to YYYY-01-01 or YYYY-MM-01 respectively. If not found, use null.
        - "journal": (string) The name of the journal, if the paper is a journal article. If not found or not applicable, use null.
        - "journal_issue": (string) The issue of the journal, if available. If not found or not applicable, use null.
        - "conference": (string) The name of the conference, if the paper is a conference proceeding. If not found or not applicable, use null.
        - "conference_location": (string) The location of the conference, if available. If not found or not applicable, use null.
        - "conference_time": (string) The date of the conference in YYYY-MM-DD format, if available. If not found or not applicable, use null.
        - "keywords": (list of strings) A list of keywords associated with the paper. If no keywords are found, use an empty list [].

        Example for author-related fields:
        If authors are ["John Doe", "Jane Smith"] and only John's sequence is "first" and Jane's email is "jane@example.com":
        "authors": ["John Doe", "Jane Smith"],
        "sequence": ["first", ""],
        "institutions": ["", ""],
        "institution_location": ["", ""],
        "email": ["", "jane@example.com"]
        
        Remember to ensure the correct word segmentation. Avoid the output like "JohnDoe" or "CenterforAppliedStatistics,Renmin UniversityofChina", and ensure the output is in Chinese if the paper is in Chinese.

        Paper Text:
        ---
        {pdf_text}
        ---
        """

        # --- THIS IS THE CRUCIAL PART ---
        api_key = os.environ.get('GEMINI_KEY')
        if not api_key:
            current_app.logger.error("GEMINI_KEY environment variable not set.")
            # Return a specific error or raise an exception
            return {
                "title": f"AI解析配置错误 (API Key Missing): {os.path.basename(file_path).replace('.pdf', '')}",
                "authors": [], "sequence": [], "institutions": [], "institution_location": [], "email": [],
                "doi": None, "publishDate": None, "journal": None, "conference": None, "keywords": []
            }
        client = genai.Client(api_key=api_key)
        # --- END CRUCIAL PART ---
        print(prompt)

        response = client.models.generate_content(
            # model="gemini-2.0-flash",
            model="gemini-2.5-flash",
            # model="gemini-2.5-flash-preview-05-20",
            # model="gemini-2.0-flash-lite",
            contents=prompt
        )

        ai_response_text_for_logging = response.text
        direct_doi = extract_doi_from_text(pdf_text)

        # client = OpenAI(api_key="sk-37fa9dd4d3bc4b268eeabd61ec348fc4", base_url="https://api.deepseek.com")

        # response = client.chat.completions.create(
        #     model="deepseek-chat",
        #     messages=[
        #         {"role": "system", "content": "You are a helpful assistant"},
        #         {"role": "user", "content": prompt},
        #     ],
        #     stream=False
        # )
        # ai_response_text_for_logging = response.choices[0].message.content

        processed_response_text = ai_response_text_for_logging.strip()
        if processed_response_text.startswith("```json"):
            processed_response_text = processed_response_text[7:]
            if processed_response_text.endswith("```"):
                processed_response_text = processed_response_text[:-3]
        elif processed_response_text.startswith("```"):
            processed_response_text = processed_response_text[3:]
            if processed_response_text.endswith("```"):
                processed_response_text = processed_response_text[:-3]

        extracted_data = json.loads(processed_response_text.strip())

        final_doi = direct_doi
        if final_doi is None:
            final_doi = extracted_data.get("doi")

        default_title_if_missing = f"AI解析 标题缺失: {os.path.basename(file_path).replace('.pdf', '')}"
        metadata = {
            "title": extracted_data.get("title") if extracted_data.get("title") is not None else default_title_if_missing,
            "authors": extracted_data.get("authors", []),
            "sequence": extracted_data.get("sequence", []),
            "institutions": extracted_data.get("institutions", []),
            "institution_location": extracted_data.get("institution_location", []),
            "email": extracted_data.get("email", []),
            "doi": final_doi,
            "publishDate": extracted_data.get("publishDate"),
            "journal": extracted_data.get("journal"),
            "journal_issue": extracted_data.get("journal_issue"),
            "conference_location": extracted_data.get("conference_location"),
            "conference_time": extracted_data.get("conference_time"),
            "conference": extracted_data.get("conference"),
            "keywords": extracted_data.get("keywords", []),
        }

        num_authors = len(metadata["authors"]) if isinstance(metadata["authors"], list) else 0
        if num_authors == 0:
            metadata["authors"] = []
            metadata["sequence"] = []
            metadata["institutions"] = []
            metadata["institution_location"] = []
            metadata["email"] = []
        else:
            for key in ["sequence", "institutions", "institution_location", "email"]:
                if not isinstance(metadata.get(key), list):
                    metadata[key] = []
                current_list = metadata[key]
                while len(current_list) < num_authors:
                    current_list.append("")
                if len(current_list) > num_authors:
                    metadata[key] = current_list[:num_authors]

        return metadata

    except json.JSONDecodeError as e:
        current_app.logger.error(f"AI元数据提取错误: Failed to parse JSON response from AI for file {file_path}. Error: {e}. Response snippet: {ai_response_text_for_logging[:500]}")
        return {
            "title": f"AI解析失败 (无效JSON): {os.path.basename(file_path).replace('.pdf', '')}",
            "authors": [], "sequence": [], "institutions": [], "institution_location": [], "email": [],
            "doi": None, "publishDate": None, "journal": None, "conference": None, "keywords": []
        }
    except Exception as e:
        current_app.logger.error(f"AI元数据提取错误: An unexpected error occurred for file {file_path}. Error: {e}", exc_info=True) # Added exc_info for more details
        return {
            "title": f"AI解析失败 (未知错误): {os.path.basename(file_path).replace('.pdf', '')}",
            "authors": [], "sequence": [], "institutions": [], "institution_location": [], "email": [],
            "doi": None, "publishDate": None, "journal": None, "conference": None, "keywords": []
        }

def extract_metadata_using_qwen_ai(file_path):
    """
    Extracts metadata from a PDF using an AI model.
    """
    ai_response_text_for_logging = ""
    try:
        reader = PdfReader(file_path)
        pdf_text = ""
        num_pages_to_extract = min(1, len(reader.pages))
        for i in range(num_pages_to_extract):
            page = reader.pages[i]
            extracted_page_text = page.extract_text()
            if extracted_page_text:
                pdf_text += extracted_page_text + "\n"

        if not pdf_text.strip():
            current_app.logger.warning(f"AI Metadata Extraction: No text could be extracted from PDF: {file_path}")
            return {
                "title": f"AI解析失败 (无文本内容): {os.path.basename(file_path).replace('.pdf', '')}",
                "authors": [], "sequence": [], "institutions": [], "institution_location": [], "email": [],
                "doi": None, "publishDate": None, "journal": None, "conference": None, "keywords": []
            }

        max_chars = 15000
        if len(pdf_text) > max_chars:
            pdf_text = pdf_text[:max_chars]

        prompt = f"""
        You are an expert academic metadata extractor. Your task is to extract metadata from the provided text of a research paper.
        Return the output STRICTLY as a single, valid JSON object. Do not include any explanatory text, comments, or markdown formatting (like ```json) before or after the JSON.

        The JSON object must have the following keys:
        - "title": (string) The main title of the paper. If not found, use null.
        - "authors": (list of strings) Full names of the authors. If no authors are found, use an empty list [].
        - "sequence": (list of strings) Corresponding sequence for each author (e.g., "first", "corresponding", "additional"). This list MUST be the same length as the "authors" list. Use an empty string "" for an author if their sequence is not specified. If "authors" is an empty list, this should also be an empty list.
        - "institutions": (list of strings) Primary affiliation/institution for each author. This list MUST be the same length as the "authors" list. Use an empty string "" for an author if their institution is not specified. If "authors" is an empty list, this should also be an empty list.
        - "institution_location": (list of strings) Location of the institution (e.g., "City, Country") for each author. This list MUST be the same length as the "authors" list. Use an empty string "" for an author if their institution location is not specified. If "authors" is an empty list, this should also be an empty list.
        - "email": (list of strings) Email address for each author. This list MUST be the same length as the "authors" list. Use an empty string "" for an author if their email is not specified. If "authors" is an empty list, this should also be an empty list.
        - "doi": (string) The Digital Object Identifier (e.g., "10.xxxx/yyyyy"). If not found, use null.
        - "publishDate": (string) The publication date in YYYY-MM-DD format. If only year or year-month is available, normalize to YYYY-01-01 or YYYY-MM-01 respectively. If not found, use null.
        - "journal": (string) The name of the journal, if the paper is a journal article. If not found or not applicable, use null.
        - "journal_issue": (string) The issue of the journal, if available. If not found or not applicable, use null.
        - "conference": (string) The name of the conference, if the paper is a conference proceeding. If not found or not applicable, use null.
        - "conference_location": (string) The location of the conference, if available. If not found or not applicable, use null.
        - "conference_time": (string) The date of the conference in YYYY-MM-DD format, if available. If not found or not applicable, use null.
        - "keywords": (list of strings) A list of keywords associated with the paper. If no keywords are found, use an empty list [].

        Example for author-related fields:
        If authors are ["John Doe", "Jane Smith"] and only John's sequence is "first" and Jane's email is "jane@example.com":
        "authors": ["John Doe", "Jane Smith"],
        "sequence": ["first", ""],
        "institutions": ["", ""],
        "institution_location": ["", ""],
        "email": ["", "jane@example.com"]
        
        Remember to ensure the correct word segmentation. Avoid the output like "JohnDoe" or "CenterforAppliedStatistics,Renmin UniversityofChina", and ensure the output is in Chinese if the paper is in Chinese.

        Paper Text:
        ---
        {pdf_text}
        ---
        """

        # --- THIS IS THE CRUCIAL PART ---
        api_key = os.environ.get('QWEN_KEY')
        if not api_key:
            current_app.logger.error("QWEN_KEY environment variable not set.")
            # Return a specific error or raise an exception
            return {
                "title": f"AI解析配置错误 (API Key Missing): {os.path.basename(file_path).replace('.pdf', '')}",
                "authors": [], "sequence": [], "institutions": [], "institution_location": [], "email": [],
                "doi": None, "publishDate": None, "journal": None, "conference": None, "keywords": []
            }

        client = OpenAI(api_key=api_key, base_url="https://dashscope.aliyuncs.com/compatible-mode/v1")
        # --- END CRUCIAL PART ---
        print(prompt)

        # 使用OpenAI兼容格式调用通义千问API
        response = client.chat.completions.create(
            model="qwen2.5-14b-instruct",
            messages=[
                {"role": "system", "content": "You are an expert academic metadata extractor."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.1
        )

        # 从响应中获取文本内容
        ai_response_text_for_logging = response.choices[0].message.content

        # ai_response_text_for_logging = response.text
        direct_doi = extract_doi_from_text(pdf_text)

        # client = OpenAI(api_key="sk-37fa9dd4d3bc4b268eeabd61ec348fc4", base_url="https://api.deepseek.com")

        # response = client.chat.completions.create(
        #     model="deepseek-chat",
        #     messages=[
        #         {"role": "system", "content": "You are a helpful assistant"},
        #         {"role": "user", "content": prompt},
        #     ],
        #     stream=False
        # )
        # ai_response_text_for_logging = response.choices[0].message.content

        processed_response_text = ai_response_text_for_logging.strip()
        if processed_response_text.startswith("```json"):
            processed_response_text = processed_response_text[7:]
            if processed_response_text.endswith("```"):
                processed_response_text = processed_response_text[:-3]
        elif processed_response_text.startswith("```"):
            processed_response_text = processed_response_text[3:]
            if processed_response_text.endswith("```"):
                processed_response_text = processed_response_text[:-3]

        extracted_data = json.loads(processed_response_text.strip())

        final_doi = direct_doi
        if final_doi is None:
            final_doi = extracted_data.get("doi")

        default_title_if_missing = f"AI解析 标题缺失: {os.path.basename(file_path).replace('.pdf', '')}"
        metadata = {
            "title": extracted_data.get("title") if extracted_data.get("title") is not None else default_title_if_missing,
            "authors": extracted_data.get("authors", []),
            "sequence": extracted_data.get("sequence", []),
            "institutions": extracted_data.get("institutions", []),
            "institution_location": extracted_data.get("institution_location", []),
            "email": extracted_data.get("email", []),
            "doi": final_doi,
            "publishDate": extracted_data.get("publishDate"),
            "journal": extracted_data.get("journal"),
            "journal_issue": extracted_data.get("journal_issue"),
            "conference_location": extracted_data.get("conference_location"),
            "conference_time": extracted_data.get("conference_time"),
            "conference": extracted_data.get("conference"),
            "keywords": extracted_data.get("keywords", []),
        }

        num_authors = len(metadata["authors"]) if isinstance(metadata["authors"], list) else 0
        if num_authors == 0:
            metadata["authors"] = []
            metadata["sequence"] = []
            metadata["institutions"] = []
            metadata["institution_location"] = []
            metadata["email"] = []
        else:
            for key in ["sequence", "institutions", "institution_location", "email"]:
                if not isinstance(metadata.get(key), list):
                    metadata[key] = []
                current_list = metadata[key]
                while len(current_list) < num_authors:
                    current_list.append("")
                if len(current_list) > num_authors:
                    metadata[key] = current_list[:num_authors]

        return metadata

    except json.JSONDecodeError as e:
        current_app.logger.error(f"AI元数据提取错误: Failed to parse JSON response from AI for file {file_path}. Error: {e}. Response snippet: {ai_response_text_for_logging[:500]}")
        return {
            "title": f"AI解析失败 (无效JSON): {os.path.basename(file_path).replace('.pdf', '')}",
            "authors": [], "sequence": [], "institutions": [], "institution_location": [], "email": [],
            "doi": None, "publishDate": None, "journal": None, "conference": None, "keywords": []
        }
    except Exception as e:
        current_app.logger.error(f"AI元数据提取错误: An unexpected error occurred for file {file_path}. Error: {e}", exc_info=True) # Added exc_info for more details
        return {
            "title": f"AI解析失败 (未知错误): {os.path.basename(file_path).replace('.pdf', '')}",
            "authors": [], "sequence": [], "institutions": [], "institution_location": [], "email": [],
            "doi": None, "publishDate": None, "journal": None, "conference": None, "keywords": []
        }

@parse_bp.route('/pdf', methods=['POST'])
@login_required
def parse_pdf_metadata():
    """解析PDF文件元数据（普通方法）"""
    if 'file' not in request.files:
        return jsonify({"error": "没有文件", "message": "请求中没有文件"}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "没有选择文件", "message": "未选择任何文件"}), 400

    if file and allowed_file(file.filename, ALLOWED_PDF_EXTENSIONS):
        try:
            # 保存文件到临时位置
            filename = secure_filename(file.filename)
            user_id = g.current_user['user_id']

            # 创建临时目录
            temp_dir = os.path.join(current_app.config['UPLOAD_FOLDER'], 'temp', str(user_id))
            os.makedirs(temp_dir, exist_ok=True)

            # 使用UUID生成唯一文件名
            unique_filename = f"{uuid.uuid4()}_{filename}"
            file_path = os.path.join(temp_dir, unique_filename)
            file.save(file_path)

            current_app.logger.info(f"正在解析PDF: {file_path}")

            # 解析元数据
            metadata = extract_metadata_from_pdf(file_path)

            # 清理临时文件，不过也可以考虑先不清理
            os.remove(file_path)

            if metadata:
                return jsonify({
                    "success": True,
                    "fileName": filename,
                    "metadata": metadata
                }), 200
            else:
                return jsonify({
                    "error": "解析失败",
                    "message": "无法解析PDF元数据"
                }), 400

        except Exception as e:
            current_app.logger.error(f"PDF解析错误: {e}")
            return jsonify({"error": "服务器错误", "message": f"处理文件时出错: {str(e)}"}), 500

    return jsonify({"error": "不支持的文件类型", "message": "仅支持PDF文件"}), 400

@parse_bp.route('/pdf/ai', methods=['POST'])
@login_required
def parse_pdf_metadata_with_ai():
    # TODO：实现AI解析
    if 'file' not in request.files:
        return jsonify({"error": "没有文件", "message": "请求中没有文件"}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "没有选择文件", "message": "未选择任何文件"}), 400

    if file and allowed_file(file.filename, ALLOWED_PDF_EXTENSIONS):
        try:
            # 保存文件到临时位置
            filename = secure_filename(file.filename)
            user_id = g.current_user['user_id']

            # 创建临时目录
            temp_dir = os.path.join(current_app.config['UPLOAD_FOLDER'], 'temp', str(user_id))
            os.makedirs(temp_dir, exist_ok=True)

            # 使用UUID生成唯一文件名
            unique_filename = f"{uuid.uuid4()}_{filename}"
            file_path = os.path.join(temp_dir, unique_filename)
            file.save(file_path)

            # 使用AI解析元数据
            use_api = os.environ.get('USE_API')
            if use_api == 'qwen':
                metadata = extract_metadata_using_qwen_ai(file_path)
            elif use_api == 'gemini':
                metadata = extract_metadata_using_gemini_ai(file_path)
            else:
                return jsonify({"error": "配置错误", "message": "未设置有效的AI解析API"}), 500

            # 清理临时文件
            os.remove(file_path)

            # print(f"AI解析结果: {metadata}")  # 调试输出

            if metadata:
                return jsonify({
                    "success": True,
                    "fileName": filename,
                    "metadata": metadata
                }), 200
            else:
                return jsonify({
                    "error": "AI解析失败",
                    "message": "无法使用AI解析PDF元数据"
                }), 400

        except Exception as e:
            current_app.logger.error(f"AI PDF解析错误: {e}")
            return jsonify({"error": "服务器错误", "message": f"AI处理文件时出错: {str(e)}"}), 500

    return jsonify({"error": "不支持的文件类型", "message": "仅支持PDF文件"}), 400