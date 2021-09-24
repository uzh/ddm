import random
import re
import string

from cryptography.fernet import Fernet
from datetime import datetime
from django.core.validators import RegexValidator
from ddm import models
from ddm.settings import ENCRYPTION_KEY


VARIABLE_VALIDATOR = RegexValidator(
    r'^[0-9a-zA-Z_-]*$',
    'Only alphanumeric characters, underscores and hyphens are allowed.'
)


def get_or_none(classmodel, **kwargs):
    """
    Regular get query that returns None when no object was found instead
    of raising an error.
    """
    try:
        return classmodel.objects.get(**kwargs)
    except classmodel.DoesNotExist:
        return None


def generate_id(id_length, letters=True, numbers=True):
    """
    Function to generate a random id of a specified length consisting
    of letters and/or numbers.
    """
    valid_characters = ''

    if letters:
        valid_characters += string.ascii_lowercase

    if numbers:
        valid_characters += string.digits

    random_id = ''.join(random.choice(valid_characters) for i in range(id_length))

    if not letters:
        if random_id[0] == '0':
            random_id = random_id[1:].join(random.choice(valid_characters))

    return random_id


def parse_date(date_string, accepted_formats):
    for fmt in accepted_formats:
        try:
            return datetime.strptime(date_string, fmt)
        except ValueError:
            pass
    raise ValueError('no valid date format found')


def cipher_variable(value, mode):
    """
    Function to encrypt or decrypt a given value.
    mode must bi in ['encrypt', 'decrypt']
    """
    if value is not None and value != '':
        # initialize encrypter
        f = Fernet(ENCRYPTION_KEY)

        # converst string to byte
        value = str.encode(value)

        if mode == 'encrypt':
            # encrypt string
            value = f.encrypt(value)
        elif mode == 'decrypt':
            # decypher string
            value = f.decrypt(value)

        # convert byte to string
        value = value.decode('utf-8')

    return value


def fill_variable_placeholder(text, sub):
    """
    Function to fill a variable placeholder.
    Placeholders are defined with [[ var_ref ]] in question texts or
    question item texts etc.
    """
    def clean_ph(ph):
        ph = ph.replace('[[', '')
        ph = ph.replace(']]', '')
        ph = ph.strip()
        ph = ph.replace(' ', '')
        return ph

    def fill_placeholder(var_name, sub):
        questionnaire = sub.questionnaire

        rel_var = models.Variable.objects.get(
            name=var_name,
            questionnaire=questionnaire
        )

        resp = models.QuestionnaireResponse.objects.filter(
            submission=sub,
            variable=rel_var
        ).first()

        if resp is None:
            var_value = ''
        else:
            var_value = resp.answer

        return var_value

    questionnaire = sub.questionnaire

    # get all occurences matching the pattern
    p = re.compile('\[\[\s*[A-Za-z0-9_|\-]+\s*\]\]')
    placeholders = p.findall(text)

    # for every placeholder, do:
    replace_values = {}
    for ph in placeholders:
        ph_clean = clean_ph(ph)

        # check for placeholder tags
        ph_elements = ph_clean.split('|')
        ph_tags = ph_elements[1:]
        ph_var = ph_elements[0]

        var_content = fill_placeholder(ph_var, sub)

        for tag in ph_tags:
            if tag == 'decrypt':
                var_content = cipher_variable(var_content, 'decrypt')

        replace_values[ph] = var_content

    for val in replace_values:
        text = text.replace(val, replace_values[val])

    return text
