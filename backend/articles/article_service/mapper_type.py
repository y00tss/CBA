from articles.article_service.document_work_apa import DocumentWorkFlowAPA
from articles.article_service.document_work_custom import DocumentWorkFlowCustom


class DocumentWorkFlowFactory:
    """
    Factory to create document processing workflow
    """

    @staticmethod
    def create_workflow(style: str, path: str):
        """
        Create workflow depending on the style editing
        """
        if style == "APA":
            return DocumentWorkFlowAPA(path)
        elif style == "Custom":
            return DocumentWorkFlowCustom(path)
        else:
            raise ValueError("Unknown style")
