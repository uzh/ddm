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

File Errors (41xx)
++++++++++++++++++
File errors relate to exceptions raised during uploading and reading a file,
but before the read contents of a file are processed.

- *4101: Not Zip*: Zip-container was expected as upload but another file type was selected (zip specific).
- *4102: Corrupt Zip*: The provided zip-container is corrupted (zip specific).
- *4103: Encrypted Zip*: The provided zip-container is encrypted (zip specific).
- *4104: Multiple Files*: Multiple files were selected.
- *4105: Wrong File Type*: The provided file does not match the expected file type.
- *4106: JSON Syntax Error*: The provided json file contains a syntax error.
- *4198: Generic Zip Error*: An unexpected exception occurred while processing the zip file (zip specific).
- *4199: Generic File Error*: An unexpected exception occurred while processing a single file.


Processing Errors (42xx)
++++++++++++++++++++++++

- *4201: Expected Fields Missing*: The supplied file did not contain the expected fields as defined in the blueprint.
- *4202: Regex Not Matched*: The expected file did not exist


Exceptions During Questionnaire (5xxx)
======================================

.. todo::
    - To be implemented
