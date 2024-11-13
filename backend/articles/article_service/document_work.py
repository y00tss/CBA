"""
Document processing module
"""
import docx
from docx.shared import Pt, RGBColor, Inches
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

        self.grammar_count = 0
        self.grammar_issues = []

        self.citation_count = 0
        self.citation_issues = []

    def _get_document(self):
        """Get document"""
        logger.info('GET DOCUMENT')
        looking_for = os.path.join(BASE_DIR, self.path)
        logger.info(f'Looking for: {looking_for}')
        # return docx.Document(self.path)
        with open(looking_for, 'rb') as f:
            return docx.Document(f)

    async def start_flow(self):
        """Start document processing"""
        logger.info('START FLOW')
        logger.info(f'Path: {self.path}')
        logger.info(f'Document: {self.document}')
        await self._front()
        await self._margins()
        await self._line_spacing()
        await self._running_head()
        await self._page_numbers()

        return self.document

    async def create_report(self):
        """Create report on the issues found"""
        report = {
            "format_issues": {
                "count": self.format_count,
                "issues": self.format_issues
            },
            "grammar_issues": {
                "count": self.grammar_count,
                "issues": self.grammar_issues
            },
            "citation_issues": {
                "count": self.citation_count,
                "issues": self.citation_issues
            }
        }

        json_report = json.dumps(report, indent=4)
        return json_report


    async def _front(self):
        """Check front page"""
        for paragraph in self.document.paragraphs:
            for run in paragraph.runs:
                if run.font.name != 'Times New Roman':
                    self.issues.append(f"Times New Roman should be used for: '{run.text}'")
                    self.count += 1

                    run.font.name = 'Times New Roman'

                if run.font.size and run.font.size.pt != 12:
                    self.issues.append(f"Font size should be 12px for the text: '{run.text}'")
                    self.count += 1

                    run.font.size = docx.shared.Pt(12)

    async def _margins(self):
        sections = self.document.sections
        for section in sections:
            if (section.left_margin.inches != 1 or
                    section.right_margin.inches != 1 or
                    section.top_margin.inches != 1 or
                    section.bottom_margin.inches != 1):
                self.issues.append("Margins are not set to 1 inch on all sides")
                self.count += 1
            # TODO заменить на проверку в пикселях

    async def _line_spacing(self):
        """Check line spacing"""
        for paragraph in self.document.paragraphs:
            if paragraph.text.strip():
                if paragraph.paragraph_format.line_spacing != 2:
                    self.issues.append(f"Text is not double-spaced: '{paragraph.text}'")

                space_after = paragraph.paragraph_format.space_after
                space_before = paragraph.paragraph_format.space_before

                if (space_after is not None and space_after > 0) or (space_before is not None and space_before > 0):
                    self.issues.append(f"Extra space found between paragraphs: '{paragraph.text}'")

    async def _running_head(self):
        """Check running head"""
        header = self.document.sections[0].header
        if not header.paragraphs:
            self.issues.append({"issue": "Running head missing in header"})
        else:
            running_head = header.paragraphs[0].text
            if not running_head.isupper():
                self.issues.append({"issue": "Running head should be in all caps", "location": running_head})

            if not header.paragraphs[0].alignment == 0:
                self.issues.append({"issue": "Running head should be left-aligned", "location": running_head})

    async def _page_numbers(self):
        header = self.document.sections[0].header
        if not header.paragraphs[0].runs[-1].text.isdigit():
            self.issues.append({"issue": "Page number should be in the header, right-aligned"})

    async def create_final_document(self, content: str, grammar_issues, citation_issues, format_issues):
        """Create final formatted document"""
        doc = docx.Document()

        doc.add_paragraph(content)

        for para in doc.paragraphs:
            for run in para.runs:
                run.font.name = 'Times New Roman'
                run.font.size = docx.shared.Pt(12)
                run.font.color.rgb = RGBColor(0, 0, 0)

        for para in doc.paragraphs:
            para.paragraph_format.line_spacing = Pt(24)

        section = doc.sections[0]
        section.top_margin = Pt(72)
        section.bottom_margin = Pt(72)
        section.left_margin = Pt(72)
        section.right_margin = Pt(72)

        header = section.header
        paragraph = header.paragraphs[0]
        paragraph.text = "RUNNING HEAD: EXAMPLE"
        paragraph.alignment = 0
        run = paragraph.add_run("Page 1")
        run.alignment = 2

        return doc

    async def create_report(self, grammar_issues, citation_issues, format_issues):
        """Generate a report on the issues found"""
        with open("report.txt", "w") as report:
            report.write("Grammar Issues:\n")
            for issue in grammar_issues:
                report.write(f"- {issue['issue']} at {issue.get('location', 'unknown location')}\n")
            report.write("\nCitation Issues:\n")
            for issue in citation_issues:
                report.write(f"- {issue['citation']} - {issue['issue']}\n")
            report.write("\nFormat Issues:\n")
            for issue in format_issues:
                report.write(f"- {issue['issue']} at {issue.get('location', 'unknown location')}\n")



