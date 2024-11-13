"""
Document processing module
"""
from datetime import datetime
import uuid
import docx
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.shared import Pt
import json
import logging
from services.logger.logger import Logger
import os

logger = Logger(__name__, level=logging.INFO, log_to_file=True,
                filename='workflow.log').get_logger()

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class DocumentWorkFlow:
    def __init__(self, path: str):
        self.path = path
        self.document = self._get_document()

        self.format_count = 0
        self.format_issues = []
        self.required_format_actions = []

        self.grammar_count = 0
        self.grammar_issues = []
        self.required_grammar_actions = []


        self.citation_count = 0
        self.citation_issues = []
        self.required_citation_actions = []

    def _get_document(self):
        """Get document"""
        try:
            logger.info('GET DOCUMENT')
            looking_for = os.path.join(BASE_DIR, self.path)
            logger.info(f'Looking for: {looking_for}')
            return docx.Document(looking_for)
        except Exception as e:
            logger.error(f"Error getting document: {e}")

    async def start_flow(self):
        """Start document processing"""
        # 1. General Document Formatting Rules
        await self._front()
        await self._margins()
        await self._line_spacing()
        # await self._running_head()
        # await self._page_numbers()

        # 2. Document Structure Overview
        await self._title_page()
        await self._abstract()

        # 3. Keywords
        await self._keywords()

        # 4. Main Text
        # await self._main_text()
        # await self._in_text_citations()
        # await self._heading_levels()
        # await self._tables()
        # await self._figures()

        return self.document

    async def create_report(self):
        """Create report on the issues found"""
        report = {
            "format_issues": {
                "count": self.format_count,
                "issues": self.format_issues,
                "required_actions": self.required_format_actions
            },
            "grammar_issues": {
                "count": self.grammar_count,
                "issues": self.grammar_issues,
                "required_actions": self.required_grammar_actions
            },
            "citation_issues": {
                "count": self.citation_count,
                "issues": self.citation_issues,
                "required_actions": self.required_citation_actions
            }
        }

        json_report = json.dumps(report, indent=4)
        return json_report

    async def _front(self):
        """Check front page"""
        for paragraph in self.document.paragraphs:
            for run in paragraph.runs:
                if run.font.name != 'Times New Roman':
                    self.format_issues.append(f"Times New Roman should be used for: '{run.text}'")
                    self.format_count += 1

                    run.font.name = 'Times New Roman'

                if run.font.size and run.font.size.pt != 12:
                    self.format_issues.append(f"Font size should be 12px for the text: '{run.text}'")
                    self.format_count += 1

                    run.font.size = docx.shared.Pt(12)

    async def _margins(self):
        sections = self.document.sections
        for section in sections:
            if (section.left_margin.inches != 1 or
                    section.right_margin.inches != 1 or
                    section.top_margin.inches != 1 or
                    section.bottom_margin.inches != 1):
                section.left_margin = 1
                section.right_margin = 1
                section.top_margin = 1
                section.bottom_margin = 1
                self.format_issues.append("Margins were corrected to 1 inch on all sides")
                self.format_count += 1

    async def _line_spacing(self):
        """Check line spacing"""
        for paragraph in self.document.paragraphs:
            if paragraph.text.strip():
                if paragraph.paragraph_format.line_spacing != 2:
                    paragraph.paragraph_format.line_spacing = 2
                    self.format_issues.append(f"Line spacing corrected to 2 for paragraph: '{paragraph.text}'")
                    self.format_count += 1

                space_after = paragraph.paragraph_format.space_after
                space_before = paragraph.paragraph_format.space_before

                if space_after is not None and space_after > 0:
                    paragraph.paragraph_format.space_after = 0
                    self.format_issues.append(f"Extra space after paragraph removed: '{paragraph.text}'")
                    self.format_count += 1

                if space_before is not None and space_before > 0:
                    paragraph.paragraph_format.space_before = 0
                    self.format_issues.append(f"Extra space before paragraph removed: '{paragraph.text}'")
                    self.format_count += 1

    async def _running_head(self):
        """Check running head"""
        header = self.document.sections[0].header

        if not header.paragraphs:
            paragraph = header.paragraphs.add_paragraph()
            paragraph.text = "RUNNING HEAD: TITLE OF THE PAPER"
            paragraph.paragraph_format.alignment = 0
            self.format_issues.append({"issue": "Running head added to header"})
            self.format_count += 1
        else:
            running_head = header.paragraphs[0].text
            if not running_head.isupper():
                header.paragraphs[0].text = running_head.upper()
                self.format_issues.append({"issue": "Running head corrected to uppercase", "location": running_head})
                self.format_count += 1

            if not header.paragraphs[0].alignment == 0:
                header.paragraphs[0].paragraph_format.alignment = 0
                self.format_issues.append({"issue": "Running head aligned to left", "location": running_head})
                self.format_count += 1

    async def _page_numbers(self):
        """Check and fix page numbers in header"""
        header = self.document.sections[0].header

        page_number = None
        for paragraph in header.paragraphs:
            for run in paragraph.runs:
                if run.text.isdigit():
                    page_number = run.text

        if not page_number:
            paragraph = header.paragraphs.add()
            paragraph.alignment = 2
            paragraph.text = "1"
            self.format_issues.append({"issue": "Page number added to header, right-aligned"})
            self.format_count += 1
        else:
            if not header.paragraphs[-1].alignment == 2:
                header.paragraphs[-1].paragraph_format.alignment = 2
                self.format_issues.append({"issue": "Page number aligned to right"})
                self.format_count += 1

    async def _title_page(self):
        """Check title page"""
        first_page = self.document.paragraphs[:12]
        found_title = False
        for para in first_page:
            if para.style.name == 'Title':
                found_title = True
                if not self._is_title_case(para.text):
                    self.format_issues.append("Should be user 'Title Case'")
                    self.format_count += 1
                    para.text = para.text.title()

                if not self._is_centered(para):
                    self.format_issues.append("Title should be centered")
                    self.format_count += 1
                    para.alignment = WD_ALIGN_PARAGRAPH.CENTER
                if not any(run.bold for run in para.runs):
                    self.format_issues.append("Title should be bolded")
                    self.format_count += 1
                    for run in para.runs:
                        run.bold = True
                break

        if not found_title:
            self.format_issues.append("Title not found in upper half of first page")
            self.required_format_actions.append("Add title to upper half of first page")
            self.format_count += 1

        author_info_found = False
        for para in first_page[1:]:
            if para.text.strip():
                author_info_found = True
                if not self._is_centered(para):
                    self.format_issues.append("Author information is not centered")
                    self.format_count += 1
                    para.alignment = WD_ALIGN_PARAGRAPH.CENTER
                if para.paragraph_format.line_spacing != Pt(24):  # 24 pt соответствует двойному интервалу
                    self.format_issues.append("Author information should be double-spaced")
                    self.format_count += 1
                    para.paragraph_format.line_spacing = Pt(24)
                break

        if not author_info_found:
            self.format_issues.append("Author information not found")
            self.required_format_actions.append("Add author information to upper half of first page")
            self.format_count += 1

        author_note_found = False
        for para in first_page:
            if 'Author Note' in para.text:
                author_note_found = True
                if para.alignment != WD_ALIGN_PARAGRAPH.CENTER:
                    self.format_issues.append("Author Note is not centered")
                    self.format_count += 1
                    para.alignment = WD_ALIGN_PARAGRAPH.CENTER
                if not any(run.bold for run in para.runs):
                    self.format_issues.append("Author Note heading is not bolded")
                    self.format_count += 1
                    for run in para.runs:
                        run.bold = True
                break

        if not author_note_found:
            self.format_issues.append("Author Note not found")
            self.required_format_actions.append("Add Author Note to upper half of first page")
            self.format_count += 1

    async def _abstract(self):
        """Check and correct Abstract section formatting"""
        found_abstract = False
        abstract_page = False
        for i, paragraph in enumerate(self.document.paragraphs):
            if paragraph.text.strip().lower() == "abstract":
                found_abstract = True

                if paragraph.alignment != WD_ALIGN_PARAGRAPH.CENTER:
                    self.format_issues.append("Abstract heading should be centered")
                    self.format_count += 1
                    paragraph.alignment = WD_ALIGN_PARAGRAPH.CENTER

                if not any(run.bold for run in paragraph.runs):
                    self.format_issues.append("Abstract heading should be bolded")
                    self.format_count += 1
                    for run in paragraph.runs:
                        run.bold = True

                if paragraph.page_break_before is None:
                    self.format_issues.append("Abstract should start on a new page")
                    self.format_count += 1
                    paragraph.insert_paragraph_before('\n', style='Normal').page_break_before = True
                abstract_page = True

                if len(self.document.paragraphs) > i + 1:
                    abstract_text = self.document.paragraphs[i + 1]

                    if abstract_text.paragraph_format.first_line_indent:
                        self.format_issues.append("First line of the Abstract should not be indented")
                        self.format_count += 1
                        abstract_text.paragraph_format.first_line_indent = None

                    word_count = len(abstract_text.text.split())
                    if word_count > 250:
                        self.format_issues.append("Abstract exceeds the 250-word limit")
                        self.format_count += 1
                        abstract_text.text = ' '.join(abstract_text.text.split()[:250])

                break

        if not found_abstract:
            self.format_issues.append("Abstract heading not found")
            self.format_count += 1
        elif not abstract_page:
            self.format_issues.append("Abstract is not on a separate page")
            self.format_count += 1

    async def _keywords(self):
        """Check and correct Keywords section formatting"""
        found_keywords = False
        for i, paragraph in enumerate(self.document.paragraphs):
            # Найти строку ниже Abstract
            if paragraph.text.strip().lower() == "abstract":
                if len(self.document.paragraphs) > i + 2:
                    keywords_paragraph = self.document.paragraphs[i + 2]
                    if not paragraph.text.lower().startswith("keywords:"):
                        self.format_issues.append("Keywords heading should begin with word: 'Keywords:'")
                        self.format_count += 1
                    if not any(run.font.italic for run in paragraph.runs):
                        self.format_issues.append("Keywords heading is not italicized")
                        self.format_count += 1

                    # Установить отступ 0.5 дюйма
                    keywords_paragraph.paragraph_format.left_indent = Pt(0.5 * 72)
                    self.format_issues.append("Keywords section indented by 0.5 inches")
                    self.format_count += 1

                    keywords_text = keywords_paragraph.text.split(":")[1].strip()
                    keywords_lower = ', '.join([word.strip().lower() for word in keywords_text.split(",")])
                    keywords_paragraph.clear()
                    run = keywords_paragraph.add_run(f"Keywords: {keywords_lower}")
                    run.italic = True
                    found_keywords = True
                    break

        if not found_keywords:
            self.format_issues.append("Keywords section not found or not properly formatted")
            self.required_format_actions.append("Add Keywords section below Abstract")
            self.format_count += 1

    async def _main_text(self):
        """Check and format main text according to APA requirements"""
        self.document.add_paragraph().clear()
        self.document.paragraphs[-1].add_run("\f")

        # Повторить заголовок на новой странице
        title_paragraph = self.document.add_paragraph(self.document.paragraphs[0].text)
        title_paragraph.alignment = WD_ALIGN_PARAGRAPH.CENTER
        title_paragraph.runs[0].bold = True

        self.format_issues.append("Main text started on a new page with repeated title in bold.")
        self.format_count += 1

    async def _in_text_citations(self):
        """Check in-text citations for author-date format"""
        for paragraph in self.document.paragraphs:
            text = paragraph.text
            if ("(" in text and ")" in text) and "," in text:
                self.format_issues.append("In-text citation format corrected.")
                self.required_citation_actions.append("Correct in-text citation format to author-date.")
                self.format_count += 1

    async def _heading_levels(self):
        """Format APA-style headings"""
        for paragraph in self.document.paragraphs:
            # Проверка и форматирование уровня 1
            if paragraph.style.name == 'Heading 1':
                paragraph.alignment = WD_ALIGN_PARAGRAPH.CENTER
                paragraph.runs[0].bold = True

            # Проверка и форматирование уровня 2
            elif paragraph.style.name == 'Heading 2':
                paragraph.alignment = WD_ALIGN_PARAGRAPH.LEFT
                paragraph.runs[0].bold = True

            self.format_issues.append("Headings formatted according to APA style.")
            self.format_count += 1

    async def _tables(self):
        """Format tables according to APA style"""
        for table in self.document.tables:
            table_number = f"Table {self.format_count + 1}"
            table_title = self.document.add_paragraph(table_number)
            table_title.alignment = WD_ALIGN_PARAGRAPH.LEFT
            table_title.runs[0].bold = True
            table_title.add_run(": Title").italic = True

            for cell in table.columns[0].cells:
                cell.text = cell.text.title()

            self.format_issues.append(f"Table {self.format_count + 1} formatted with APA style borders and title.")
            self.format_count += 1

    async def _figures(self):
        """Format figures according to APA style"""
        figure_count = 0
        for paragraph in self.document.paragraphs:
            if "Figure" in paragraph.text:
                figure_count += 1
                paragraph.text = f"Figure {figure_count}"
                paragraph.alignment = WD_ALIGN_PARAGRAPH.LEFT
                paragraph.runs[0].bold = True

                caption_paragraph = self.document.add_paragraph("Caption for Figure")
                caption_paragraph.alignment = WD_ALIGN_PARAGRAPH.CENTER
                caption_paragraph.runs[0].italic = True
                self.format_issues.append(f"Figure {figure_count} formatted with APA style.")
                self.format_count += 1

    # """ENCAPSULATED FUNCTIONS"""
    def _is_title_case(self, text: str) -> bool:
        """Check if text is in title case"""
        words = text.split()
        for word in words:
            if not word[0].isupper():
                return False
        return True

    def _is_centered(self, paragraph) -> bool:
        """Check if paragraph is centered"""
        return paragraph.alignment == WD_ALIGN_PARAGRAPH.CENTER

    async def get_updated_document(self, user_name: str):
        """Convert to docx after checking"""
        file_name = f"updated_document_{datetime.now().date()}_{uuid.uuid4()}.docx"
        file_path = f"articles/documents/{user_name}/{file_name}"

        os.makedirs(os.path.dirname(file_path), exist_ok=True)

        self.document.save(file_path)

        return file_path, self.document
