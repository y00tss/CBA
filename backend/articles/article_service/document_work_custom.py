"""
Document processing module for custom style
"""
from articles.article_service.document_work_abstract import DocumentWorkAbstract


class DocumentWorkFlowCustom(DocumentWorkAbstract):
    """Class to process document according to APA style"""

    def __init__(self, path: str):
        self.path = path
        self.document = self._get_document()

        self.format_issues = []
        self.required_format_actions = []

        self.citation_issues = []
        self.required_citation_actions = []

    def _get_document(self):
        """Get document"""
        return "test"

    async def start_flow(self):
        """Start document processing"""
        pass

    async def create_report(self):
        """Create report"""
        pass

    async def get_updated_document(self, user_name: str):
        """Convert to docx after checking"""
        pass
