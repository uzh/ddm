###############
For Researchers
###############

This section describes how the DDM looks from the researcher's perspective and
includes a short quickstart on how to create a simple data donation project.


Researcher Interface
********************

This section provides an overview of the interface structure.


Project List
------------

The project list provides an overview of all the projects you have created.
Here, you can also create new projects.


Project Hub
------------

The Project Hub is the entry point to editing an existing project.
It consists of the following sections:

1. Project Details
2. Project Configuration
3. Data Center
4. Danger Zone


Project Details
+++++++++++++++

Here, basic meta-configurations of the data donation project are listed and can be edited.


Project Configuration
+++++++++++++++++++++

The structure of the Project Configuration follows the steps of the prototypical
data donation process. It consists of the following sections:

1. Welcome Page: Define what is displayed to participants when they enter your project.
2. Data Donation: Define the expected data donations, extraction rules, and donation instructions.
3. Questionnaire: Define questions that will be shown to participants after they have donated their data.
4. End Page: Define what is displayed when participants reach the end of the data donation.


Data Center
+++++++++++

The Data Center will report some basic statistics about the status of an
ongoing data donation project [to be integrated].

Furthermore, you can download the collected data donations as a JSON file.


Danger Zone
+++++++++++

Here, you can find the option to delete the current project.
Please be aware that a deleted project cannot be restored and all the collected
data donations and questionnaire responses will be deleted with it.


Profile View
------------

.. todo::
    Add Content.

Set up a Data Donation Project
******************************

Create a Project
----------------

.. todo::
    Add Content.

Define the Welcome Page
-----------------------

.. todo::
    Add Content.

Set up the Data Donation
------------------------

With Donation Blueprints, researchers define what kind of data they are expecting and
which data they want to extract from the donated data.

There are two types of Donation Blueprints:

a. Donation Blueprint
b. Zip Container

The *Donation Blueprint* defines processing rules on the file level.
The *Zip Container* is a container class, that can be used to bundle
multiple *Donation Blueprints* if participants upload a ZIP file instead of a single file.


Donation Blueprint
++++++++++++++++++
The Donation Blueprint defines the logic, how a donated data file will be processed
and how the data will be extracted.

Settings:
^^^^^^^^^

**Name:**
Name of the expected data donations. Will be publicly visible to participants.
Therefore, it is important to define a meaningful name.

**Expected File Format:**
The file format of the expected data donation. Currently, only JSON is implemented.

**Expected Fields:**
The fields that must be contained in the donated file. If a file does not contain
one or more of the fields defined here, it will not be accepted as a donation.
This setting should be defined in the following format: "Field A", "Field B"

**Extracted Fields:**
The fields that will be extracted from a donated file, of the file contains the
expected fields.
This setting should be defined in the following format: "Field A", "Field B"

**Zip blueprint:**
This field is allowed to be undefined. [-- TODO: Add meaningful description --]

**Regex path:**
Here, the path where the file is expected to be located within a ZIP file is defined.
Only necessary, if the Donation Blueprint is part of a Zipped Donation Blueprint.
[-- TODO: Check if this has already been implemented correctly --]



Zip Container
+++++++++++++
A container class, to bundle one or multiple *Donation Blueprints* if a ZIP file
is expected as a donation.

Settings:
^^^^^^^^^

**Name:**
Name of the expected data donations. Will be publicly visible to participants.
Therefore, it is important to define a meaningful name.

Overwrites the name of the *Donation Blueprint* in the participant view.


Instructions
++++++++++++

Instructions can either be defined on the level of a *Donation Blueprint* or a *Zip Container*.

Instructions consist of one or more instruction pages that can be freely edited by the researcher.
Instructions will automatically be displayed in the participant-flow.

If a *Donation Blueprint* is part of a *Zip Container*, the instructions defined
on the *Zip Container* will take precedent over the instructions defined on the
Blueprint-level (i.e., the latter will not be shown).



Define Questionnaire
--------------------

Researchers can optionally define a questionnaire consisting of one or more questions.
The questions will be displayed after the data donation, but only if the data donation has been successfully completed.

Include Donated Data in a Question
++++++++++++++++++++++++++++++++++

It is possible to include information contained in the donated data in the question text.
For this, every question must be associated to a *Donation Blueprint*.
The donated data related to the associated blueprint will then be available as a
context variable.

For this, DDM utilizes the `Django template engine <https://docs.djangoproject.com/en/3.2/topics/templates/>`_.
The donated data will be available as a template variable "data" in the question text definition.
This variable can be combined flexibly with Django's `built-in template tags and filters <https://docs.djangoproject.com/en/3.2/ref/templates/builtins/>`_.

.. todo::
    Include example.

Question Types
++++++++++++++

DDM integrates the following question types:

* Single Choice Question
* Multi Choice Question
* Matrix Question
* Semantic Differential
* Open Question
* Transition Block (plain text, without any response options for the participant)

Depending on the question type, *question response items* and a *question response scale* can be defined.

Additional features:

* Question items can be randomized.
* More to come.



Define the End Page
-------------------

.. todo::
    Add Content.


Monitor an Active Data Donation Project
***************************************

.. todo::
    Add Content.


Download the Collected Data
***************************

.. todo::
    Add Content.


