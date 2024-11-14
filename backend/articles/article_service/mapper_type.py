from articles.article_service.document_work_apa import DocumentWorkFlowAPA
from articles.article_service.document_work_custom import DocumentWorkFlowCustom


class DocumentWorkFlowFactory:
    """
    Factory to create document processing workflow depending on the style editing
    """

    @staticmethod
    def create_workflow(style: str, path: str):
        """
        Create workflow depending on the style editing
        """
        match style:
            case "APA":
                return DocumentWorkFlowAPA(path)
            case "Custom":
                return DocumentWorkFlowCustom(path)
            case _:
                raise ValueError("Unknown style")
