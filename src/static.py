"""
Author: Haining Wang hw56@indiana.edu

This module holds functions for i/o and checking.
"""


import io
import base64
import chardet
import numpy as np
import pandas as pd
from collections import Counter

UNKNOWN = ['n/a', 'N/A', 'na', 'NA', 'Na', np.nan, 'unknown', 'UNKNOWN', '?', '??', "???"]
YES = [1, 'yes', 'y', 'Yes', 'YES', 'Y']
NO = [0, 'no', 'n', 'No', 'NO', 'N']
TYPES = ['B', 'P', 'T']
HEADINGS = {'Proposition', 'Speaker', 'Responds To', 'Relation Type', 'Distance', 'Dotted Line', 'Text'}
LOWER_HEADINGS = set(str.lower(h) for h in HEADINGS)

MD_UPLOAD_FAIL = """**😭 Uploading Failed**.  
        Please upload data in comma/tab-separated values (`.csv`/`.tsv`/`.txt`) or Excel (`.xlsx`/`.xls`) format and use the right suffix accordingly.
        
        """

MD_FEEDBACK_HEADING = f"""Please make sure the following seven headings are specified: {list(HEADINGS)}. Headings are case- and sequence-insensitive, but space within a heading matters. If you do not need "Dotted Line" or "Text," leave all values below as "NA". We recommend using the provided template."""


def read_in_uploaded(contents, filename):
    """
    Reads in a user uploaded file.
    """
    # def parse_data_upload(contents, filename):
    content_type, content_string = contents.split(',')
    # decoded is "bytes"
    decoded = base64.b64decode(content_string)
    # detect file's encoding scheme
    codec = chardet.detect(decoded)

    if "csv" == filename.split('.')[-1]:
        try:
            df = pd.read_csv(io.StringIO(decoded.decode(codec['encoding'])))
        except ValueError:
            df = MD_UPLOAD_FAIL
    elif "xls" in filename.split('.')[-1]:
        try:
            df = pd.read_excel(io.BytesIO(decoded), sheet_name="Sheet1")
        except ValueError:
            df = MD_UPLOAD_FAIL
    elif "txt" == filename.split('.')[-1] or "tsv" == filename.split('.')[-1]:
        try:
            df = pd.read_csv(io.StringIO(decoded.decode(codec['encoding'])), delimiter="\t")
        except ValueError:
            df = MD_UPLOAD_FAIL
    else:
        df = MD_UPLOAD_FAIL

    return df

def read_in_demo(filepath='./samples/BiliBili_comments.xlsx',
                 filename='BiliBili_comments.xlsx'):
    """
    Reads in an example.
    """
    try:
        if 'xlsx' in filename:
            df = pd.read_excel(filepath)
            return df
        elif 'txt' in filename:
            df = pd.read_csv(filepath, delimiter='\t')
            return df
        elif 'csv' in filename:
            df = pd.read_csv(filepath)
            return df
    except Exception as e:
        # print(e)
        # print(filename)
        df = '**Demo Failed**. Please check the validity of the demo file.'
        return df

def check_heading(df):
    """
    Checks if HEADINGS is a subset of input headings.
    Headings should be included: Proposition/Speaker/Responds To/Relation Type/Distance/Dotted Line/Text.
    Case-insensitive, sequence-insensitive.
    """
    feedback = """

**Heading check**:

"""
    unique_lower_headings = set(str.lower(h) for h in set(df.columns))
    if len(unique_lower_headings) == 7 and unique_lower_headings == LOWER_HEADINGS:
        # desired situation: 7 headings without overlap
        feedback += "The pre-defined headings look good.  "
    elif len(unique_lower_headings) == 7 and unique_lower_headings != LOWER_HEADINGS:
        # overlap exists
        count_headings = Counter(df.columns)
        overlap = [key for key in count_headings.keys() if count_headings[key] >= 2]
        feedback += f"Multiple {overlap} exist."
    elif len(unique_lower_headings) < 7:
        missing = set(str.capitalize(h) for h in (LOWER_HEADINGS - unique_lower_headings))
        redundant = set(str.capitalize(h) for h in (unique_lower_headings - LOWER_HEADINGS))
        feedback += f"Heading {[str.capitalize(h) for h in list(missing)]} {'is' if len(missing) == 1 else 'are'} missing."
        if not unique_lower_headings.issubset(HEADINGS):
            # wrong headings exist
            feedback += f" We are not going to use the values below Heading {[str.capitalize(h) for h in list(redundant)]}"
        else:
            pass
    elif len(unique_lower_headings) > 7:
        # seven desired headings are correctly specified
        if HEADINGS.issubset(unique_lower_headings):
            extra = set(str.capitalize(h) for h in (unique_lower_headings - LOWER_HEADINGS))
            feedback += f"Required headings are all specified correctly. " \
                        f"No check will be perform on extra heading{'' if len(extra) == 1 else 's'} {[str.capitalize(h) for h in extra]}, which may cause consequences."
        else:
            missing = set(str.capitalize(h) for h in (LOWER_HEADINGS - unique_lower_headings))
            redundant_or_overlap = set(str.capitalize(h) for h in (unique_lower_headings - LOWER_HEADINGS))
            if len(missing) > 0:
                feedback += f"Heading {[str.capitalize(h) for h in list(missing)]} {'is' if len(missing) == 1 else 'are'} missing.  "
            else:
                pass
            if redundant_or_overlap is not set():
                feedback += f"Heading {[str.capitalize(h) for h in list(redundant_or_overlap)]} {'looks' if len(redundant_or_overlap) == 1 else 'look'} suspicious." \
                            f" We are not going to use the values below {'it' if len(redundant_or_overlap) == 1 else 'them'}.  "
            else:
                pass
    else:
        pass
    feedback += MD_FEEDBACK_HEADING if feedback != """

**Heading check**:

""" else "Looks good.  "

    return feedback

def check_minimal_length(df):
    """
    Checks if the `proposition` has at least two values
    """
    feedback = """
    
**Minimal length check**:

"""
    feedback += """Looks good.""" if df['Proposition'].count() >= 2 else """Proposition count is too short (less than two)."""
    return feedback

def check_equal_length(df):
    """
    Checks whether each column has the same length to `Proposition` column.
    """
    feedback = """

**Equal length check**:

"""
    proposition_values_count = len(df.Proposition)
    heading_of_diff_len = set(heading if len(df[heading]) != proposition_values_count else None for heading in HEADINGS) - {None}
    if len(heading_of_diff_len) != 0:
        feedback += f"""The length of {[h for h in heading_of_diff_len]} {
        'is' if len({heading_of_diff_len})==1 else 'are'} not equal to the length of the "Proposition" column.  """
    else:
        pass
    feedback += """Looks good.""" if feedback == """

**Equal length check**:

""" else ""
    return feedback

def check_first_row(df):
    """
    Checks if the first row is legal.
    The rules are:
        1. the first value under `Proposition` should be "0"
        2. three headings (Responds To, Relation Type, and Distance) should be "NA" (or one of the `UNKNOWN`)
        3. two headings (Speaker and Text) should have some value
        4. `Dotted Line` should be all of zero if not going to use.(this is not checked here, will be checked in `check_value_type`)
    """
    feedback = """
    
**First row check**:
    
"""
    # check the first value under `Proposition`
    feedback += '' if df['Proposition'][0] == 0 else 'Please specify the first value under Proposition as "0". '
    problematic_headings = []
    try:
        # the three headings
        for heading in ['Responds To', 'Relation Type', 'Distance']:
            problematic_headings.append(heading) if not np.isnan(df[heading][0]) else None
        # the two headings
        feedback += '' if df['Speaker'][0] != np.nan else 'The first value under "Speaker" should not be blank. '
        feedback += '' if df['Text'][0] != np.nan else 'The first value under "Text" should not be blank. '
    except:
        pass
    if problematic_headings != []:
        feedback += f'''The first value{'s' if len(problematic_headings)>1 else ''} under {problematic_headings} should be "NA". '''
    else:
        pass

    feedback += "Looks good." if feedback == """
    
**First row check**:
    
""" else ""
    return feedback

def check_blank_value(df):
    """
    Checks if the values under headings are blank.
    Values under `Proposition` `Speaker` should never be blank or 'NA'.
    """
    feedback = """
    
**Blank value check**:
    
"""
    try:
        feedback += '' if not len(
            df.Proposition) > df.Proposition.count() else 'Values under "Proposition" should never be blank or "NA".  '
        feedback += '' if not len(
            df.Speaker) > df.Speaker.count() else 'Values under "Speaker" should never be blank or "NA".  '
        # feedback += '' if len(
        #     df.Text) > df.Text.count() else 'Values under "Text" should never be blank or "NA".  '
    except:
        pass
    feedback += "Looks good." if feedback == """
    
**Blank value check**:
    
""" else ""
    return feedback

def check_value_type(df):
    """
    Checks if the tags has right data type.
    `Proposition`: No overlap, no NA.
    `Responds To`: exist in Proposition (excluding the first value)
    `Relation Type`: T/P/B (excluding the first value)
    `Distance`: T=0, P=1/2/3, B=4 (excluding the first value)
    `Dotted Line`: 0 or 1 (including the first value)
    [TODO]
    No checks on `Speaker` and `Text`, but will convert values of those two column into strings (excluding the first values)
    """
    feedback = """
    
**Value type check**:
    
"""
    try:
        # Proposition
        feedback += '' if len(df.Proposition) == len(set(df.Proposition)) else 'Make sure no overlap or "NA" exists in "Proposition" column.  '
        # Responds To
        falling_out = set(df['Responds To'][1:]) - set(df.Proposition)
        feedback += "" if falling_out == set() else f'"Responds To" column {"has" if len(falling_out)==1 else "have"} {[v for v in falling_out]} that does not exist in "Proposition" column.  '
        # Relation Type
        lower_relation_type_set = set([str.lower(v) for v in df['Relation Type'][1:]])
        diff_relation_type_set = lower_relation_type_set - {'t', 'p', 'b'}
        feedback += "" if diff_relation_type_set == set() else f'"Relation Type" column {"has" if len(diff_relation_type_set) == 1 else "have"} {[v for v in falling_out]} that does not fit. The relation can only be one of "T" (narrowly on-Topic), "P" (Parallel shift), and "B" (Break).  '
        # Distance
        for i in range(1, len(df['Relation Type'])):
            if str.lower(df['Relation Type'][i]) == 't':
                feedback += "" if df['Distance'][i] == 0 else f"The {i}{'st' if str(i)[-1] == '1' else ('nd' if str(i)[-1] == '2' else ('rd' if str(i)[-1] == '3' else 'th'))} row's relation type and distance mismatch.  "
            elif str.lower(df['Relation Type'][i]) == 'p':
                feedback += "" if df['Distance'][i] in [1, 2, 3] else f"The {i}{'st' if str(i)[-1] == '1' else ('nd' if str(i)[-1] == '2' else ('rd' if str(i)[-1] == '3' else 'th'))} row's relation type and distance mismatch.  "
            elif str.lower(df['Relation Type'][i]) == 'b':
                feedback += "" if df['Distance'][i] == 4 else f"The {i}{'st' if str(i)[-1] == '1' else ('nd' if str(i)[-1] == '2' else ('rd' if str(i)[-1] == '3' else 'th'))} row's relation type and distance mismatch.  "
            else:
                pass
        # Dotted Line
        dotted_line_str = [v for v in df['Dotted Line'].astype(str)]
        for i in range(0, len(df['Dotted Line'])):
            feedback += "" if dotted_line_str[i] in ['1', '0', '1.0', '0.0'] else f'''The {i}{'st' if str(i)[-1] == '1' else ('nd' if str(i)[-1] == '2' else ('rd' if str(i)[-1] == '3' else 'th'))} row's dotted line is specified incorrectly. Use "1" to indicate a tenuous connection between propositions and "0" otherwise. If the field is not going to use, specify all values as 0.'''
    except:
        pass
    feedback += "Looks good." if feedback == """
    
**Value type check**:
    
""" else ""
    return feedback

def check_order(df):
    """
    Checks if value in `Responds To` appears before `Proposition`.
    """
    feedback = """"""
    try:
        proposition = list(df.Proposition[1:].astype(str))
        respondsto = list(df['Responds To'][1:].astype(str))

        for i, v in enumerate(proposition):
            for j, u in enumerate(respondsto):
                if u == v and j < i:
                    feedback += f'''"Responds To" value {u} (in the {j+3}{'st' if str(i)[-1] == '1' else ('nd' if str(i)[-1] == '2' else ('rd' if str(i)[-1] == '3' else 'th'))} row) appears ealier than its corresponding "Propostion" value {v}, double check it.'''
                elif u == v and j == i:
                    feedback += f'''"Responds To" value {u} (in the {j+3}{'st' if str(i)[-1] == '1' else ('nd' if str(i)[-1] == '2' else ('rd' if str(i)[-1] == '3' else 'th'))} row) and its corresponding "Propostion" value {v} appear at the same row, double check it.'''
                else:
                    pass
    except:
        pass
    feedback += "" if feedback == "" else ''' Please make sure the corresponding value in "Propostion" appears before the value in "Responds To".'''
    return feedback

