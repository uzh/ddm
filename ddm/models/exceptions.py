from django.db import models


# ERROR IMPLEMENTATION
# ====================

# OPTION 1: 1 Error Class with translation field.
# Pro:      - Can be easily filtered (e.g., with Error Code)
# Contra:   - Translation is messy
#           - Database prepopulation with fixture or data migration not ideal
#
# Example
# -------
# class DDMException:
#     status_code = None
#     staus_description = None
#     status_message = models.TextField(max_length=1024)  # Default english status message.
#     status_translations = models.JSONField()
#
#     type = models.CharField(
#         max_length=3,
#         choices=ExceptionType.choices,
#         default=ExceptionType.FILE_ERROR,
#     )


# OPTION 2: A separate class with fixed attributes for each error.
# Pro:      - Translation with Django's implementation of gettext possible
#           - No database prepopulation needed
#           - Relatively good overview
# Contra:   - Filtering of different errors with a dict-approach seems hacky
#           - Not easy/possible to define additional errors
#
# Open Question: Should this inherit from BaseException?
#
# Example
# -------
# class DDMBaseException:
#     exception_type = 'undefined'
#     status_code = '000'
#     description = 'Unknown Error'
#     message = _('Something went wrong.')
#
#     def some_shared_function(self):
#         pass
#
#
# class FileNameNotMatched(DDMBaseException):
#     exception_type = 'File'
#     status_code = '101'
#     description = _('File name not matched')
#     message = _('File name could not be matched. Tried the following things: %s')
#
#
# class NoDataInFile(DDMBaseException):
#     exception_type = 'Data Validity'
#     status_code = '201'
#     description = _('File does not contain any data')
#     message = _('Did you upload an empty file?')
#
#
# DDM_EXCEPTIONS = {
#     '101': FileNameNotMatched,
#     '201': NoDataInFile
# }


# EXCEPTION LOGGING
# =============
# from ddm.ddm.models import DonationProject
#
#
# class ExceptionLog(models.Model):
#     date = models.DateTimeField()
#     project = models.ForeignKey(DonationProject)
#     exception_type = models.CharField(max_lentgh=20)
#     exception_code = models.CharField(max_length=20)
#     message = models.CharField(max_length=255)
#     description = models.TextField()
