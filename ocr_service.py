import sqlite3

import os

import pytesseract

from pdf2image import convert_from_path

from sentence_transformers import SentenceTransformer

from sklearn.metrics.pairwise import cosine_similarity

from docx import Document


DB_FILE = "ocr_data.db"


model = SentenceTransformer(
    'all-MiniLM-L6-v2'
)


def create_database():

    conn = sqlite3.connect(DB_FILE)

    cursor = conn.cursor()

    cursor.execute("""

        CREATE TABLE IF NOT EXISTS documents (

            id INTEGER PRIMARY KEY AUTOINCREMENT,

            category TEXT,

            sub_category TEXT,

            file_name TEXT,

            file_path TEXT,

            page_number INTEGER,

            content TEXT

        )

    """)

    conn.commit()

    conn.close()


def scan_pdf(

    file_path,

    file_name,

    category,

    sub_category

):

    images = convert_from_path(file_path)

    conn = sqlite3.connect(DB_FILE)

    cursor = conn.cursor()

    cursor.execute("""

        DELETE FROM documents

        WHERE file_name = ?

    """, (file_name,))

    page_count = 1

    for image in images:

        text = pytesseract.image_to_string(image)

        cursor.execute("""

            INSERT INTO documents
            (
                category,
                sub_category,
                file_name,
                file_path,
                page_number,
                content
            )

            VALUES (?, ?, ?, ?, ?, ?)

        """, (

            category,
            sub_category,
            file_name,
            file_path,
            page_count,
            text

        ))

        page_count += 1

    conn.commit()

    conn.close()


def scan_word_document(

    file_path,

    file_name,

    category,

    sub_category

):

    doc = Document(file_path)

    full_text = ""

    for para in doc.paragraphs:

        full_text += para.text + "\n"

    conn = sqlite3.connect(DB_FILE)

    cursor = conn.cursor()

    cursor.execute("""

        DELETE FROM documents

        WHERE file_name = ?

    """, (file_name,))

    cursor.execute("""

        INSERT INTO documents
        (
            category,
            sub_category,
            file_name,
            file_path,
            page_number,
            content
        )

        VALUES (?, ?, ?, ?, ?, ?)

    """, (

        category,
        sub_category,
        file_name,
        file_path,
        1,
        full_text

    ))

    conn.commit()

    conn.close()


def auto_scan_past_tenders():

    base_folder = "PDFs/Past_Tenders"

    if not os.path.exists(base_folder):

        return

    for root, dirs, files in os.walk(base_folder):

        for file in files:

            file_path = os.path.join(
                root,
                file
            )

            sub_category = os.path.basename(root)

            if file.endswith(".pdf"):

                scan_pdf(

                    file_path,

                    file,

                    "Past_Tenders",

                    sub_category
                )

            elif file.endswith(".docx"):

                scan_word_document(

                    file_path,

                    file,

                    "Past_Tenders",

                    sub_category
                )


def search_documents(search_text):

    conn = sqlite3.connect(DB_FILE)

    cursor = conn.cursor()

    cursor.execute("""

        SELECT DISTINCT

        category,
        sub_category,
        file_name

        FROM documents

        WHERE content LIKE ?

    """, (f"%{search_text}%",))

    results = cursor.fetchall()

    conn.close()

    return results


def get_auto_suggestions(search_text):

    conn = sqlite3.connect(DB_FILE)

    cursor = conn.cursor()

    cursor.execute("""

        SELECT content,
               file_name

        FROM documents

        WHERE content LIKE ?

    """, (f"%{search_text}%",))

    rows = cursor.fetchall()

    conn.close()

    suggestions = []

    for row in rows:

        content = row[0]

        file_name = row[1]

        words = content.replace(
            "\n",
            " "
        ).split()

        for i in range(len(words)):

            current_word = words[i]

            if search_text.lower() in current_word.lower():

                phrase = current_word

                if i + 1 < len(words):

                    phrase += " " + words[i + 1]

                if i + 2 < len(words):

                    phrase += " " + words[i + 2]

                suggestions.append({

                    "suggestion": phrase,

                    "file_name": file_name
                })

    unique = []

    final = []

    for item in suggestions:

        if item not in unique:

            unique.append(item)

            final.append(item)

    return final[:10]


def get_ai_pdf_suggestions(user_requirement):

    conn = sqlite3.connect(DB_FILE)

    cursor = conn.cursor()

    cursor.execute("""

        SELECT DISTINCT

        category,
        sub_category,
        file_name,
        content

        FROM documents

    """)

    rows = cursor.fetchall()

    conn.close()

    results = []

    for row in rows:

        category = row[0]

        sub_category = row[1]

        file_name = row[2]

        content = row[3]

        if user_requirement.lower() in content.lower():

            keywords = []

            split_data = content.replace(
                "\n",
                ","
            ).split(",")

            for item in split_data:

                cleaned = item.strip()

                if (

                    len(cleaned) > 3

                    and

                    cleaned not in keywords

                ):

                    keywords.append(cleaned)

            keywords = keywords[:8]

            results.append({

                "category": category,

                "sub_category": sub_category,

                "file_name": file_name,

                "similarity_score": 100,

                "keywords": keywords
            })

    return results


create_database()

auto_scan_past_tenders()