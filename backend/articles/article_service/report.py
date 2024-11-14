"""
Report of performed actions
"""
import logging
from services.logger.logger import Logger

logger = Logger(__name__, level=logging.INFO, log_to_file=True, filename='report.log').get_logger() # noqa


class Report:
    """
    Report of performed actions
    """

    def __init__(self, report):
        self.report = report

    def get_report(self):
        """Generate the report with issues and recommendations."""
        format_issues = self._get_count_issues("format_issues")
        citation_issues = self._get_count_issues("citation_issues")
        total_count = format_issues + citation_issues

        format_recommendations = self._get_count_recommendations("format_issues")
        citation_recommendations = self._get_count_recommendations("citation_issues")
        total_recommendations = format_recommendations + citation_recommendations

        recommendations = self._get_all_recommendations()

        logger.info(f"Report generated: {total_count} issues, {total_recommendations} recommendations")

        return {
            "total_count": total_count,
            "format_issues": format_issues,
            "citation_issues": citation_issues,
            "total_recommendations": total_recommendations,
            "format_recommendations": format_recommendations,
            "citation_recommendations": citation_recommendations,
            "recommendations": recommendations
        }

    def _get_count_issues(self, issue_type):
        """Return the count of issues for a specific type."""
        return len(self.report[issue_type]["issues"])

    def _get_count_recommendations(self, issue_type):
        """Return the count of recommendations for a specific type."""
        return len(self.report[issue_type]["required_actions"])

    def _get_all_recommendations(self):
        """Return all recommendations from both issue types."""
        format_recommendations = self.report["format_issues"]["required_actions"]
        citation_recommendations = self.report["citation_issues"]["required_actions"]
        return format_recommendations + citation_recommendations
