"""
Report of performed actions
"""
import logging
from services.logger.logger import Logger

logger = Logger(__name__, level=logging.INFO, log_to_file=True,
                filename='report.log').get_logger()


class AbstractReport:
    """
    Abstract class for report
    """

    async def get_report(self):
        raise NotImplementedError


class Report(AbstractReport):
    """
    Report of performed actions
    """

    def __init__(self, report):
        self.report = report

    async def get_report(self):
        format_issues = await self._get_count_format_issues()
        citation_issues = await self._get_count_citation_issues()
        total_count = format_issues + citation_issues
        logger.info(f"Total count of issues: {total_count}")
        logger.info(f"Format issues: {format_issues}")
        logger.info(f"Citation issues: {citation_issues}")

        format_recommendations = await self._get_count_format_recommendations()
        citation_recommendations = await self._get_count_citation_recommendations()
        total_recommendations = format_recommendations + citation_recommendations
        logger.info(f"Total count of recommendations: {total_recommendations}")
        logger.info(f"Format recommendations: {format_recommendations}")
        logger.info(f"Citation recommendations: {citation_recommendations}")

        recommendations = await self._get_all_recommendations()
        logger.info(f"All recommendations: {recommendations}")
        return {
            "total_count": total_count,
            "format_issues": format_issues,
            "citation_issues": citation_issues,
            "total_recommendations": total_recommendations,
            "format_recommendations": format_recommendations,
            "citation_recommendations": citation_recommendations,
            "recommendations": recommendations
        }

    async def _get_count_format_issues(self):
        """ Get format issues"""
        return len(self.report["format_issues"]["issues"])

    async def _get_count_citation_issues(self):
        """ Get citation issues"""
        return len(self.report["citation_issues"]["issues"])

    async def _get_count_format_recommendations(self):
        """ Get count format recommendations"""
        return len(self.report["format_issues"]["required_actions"])

    async def _get_count_citation_recommendations(self):
        """ Get count citation recommendations"""
        return len(self.report["citation_issues"]["required_actions"])

    async def _get_all_recommendations(self):
        """ Get all recommendations"""
        return (self.report["format_issues"]["required_actions"] +
                self.report["citation_issues"]["required_actions"])
