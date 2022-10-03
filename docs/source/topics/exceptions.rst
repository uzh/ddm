##########
Exceptions
##########

.. todo::
    - Find suitable place in documentation

This page describes the implemented exceptions that are logged in a project's exception log.



Exceptions Caught on Client Side
********************************


Exceptions During Data Donation (4xxx)
======================================

File Messages (41xx)
++++++++++++++++++++
File errors relate to exceptions raised during uploading and reading a file,
but before the read contents of a file are processed.

4101: Not Zip
-------------
| *Description:* Zip-container was expected as upload but another file type was selected (zip specific).
| *Exception Message:* TODO

4102: Corrupt Zip
-----------------
| *Description:* The provided zip-container is corrupted (zip specific).
| *Exception Message:* TODO

4103: Encrypted Zip
-------------------
| *Description:* The provided zip-container is encrypted (zip specific).
| *Exception Message:* TODO

4104: Multiple Files
--------------------
| *Description:* Multiple files were selected.
| *Exception Message:* TODO

4105: Wrong File Type
---------------------
| *Description:* The provided file does not match the expected file type.
| *Exception Message:* TODO

4106: JSON Syntax Error
-----------------------
| *Description:* The provided json file contains a syntax error.
| *Exception Message:* TODO

4198: Generic Zip Error
-----------------------
| *Description:* An unexpected exception occurred while processing the zip file (zip specific).
| *Exception Message:* TODO

4199: Generic File Error
------------------------
| *Description:* An unexpected exception occurred while processing a single file.
| *Exception Message:* TODO


Processing Messages (42xx)
++++++++++++++++++++++++++

4201: All Expected Fields Missing
------------------------
| *Description:* None of the entries in the supplied file did contain the expected fields as defined in the blueprint.
| *Exception Message:* TODO

4202: Regex Not Matched
------------------------
| *Description:* The expected file did not exist.
| *Exception Message:* TODO

4203: Entry Not Containing Expected Fields
------------------------
| *Description:* An entry did not contain one or more of the expected fields.
| *Exception Message:* TODO

4204: All Entries Filtered Out
------------------------------
| *Description:* All entries of an uploaded file were filtered out and therefore no data was extracted.
| *Exception Message:* TODO

4205: All Entries Either Missing Expected Field or Filtered
------------------------------
| *Description:* All entries of an uploaded file were either missing one or more expected fields or filtered out and therefore no data was extracted.
| *Exception Message:* TODO

4206: Entry was filtered out
------------------------------
| *Description:* A filter rule applied and the entry was deleted.
| *Exception Message:* TODO

4299: Entry Not Containing Expected Fields
------------------------
| *Description:* An entry did not contain one or more of the expected fields.
| *Exception Message:* TODO


Exceptions During Questionnaire (5xxx)
======================================

.. todo::
    - To be implemented
