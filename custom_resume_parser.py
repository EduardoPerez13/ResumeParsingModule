import io
import os
import inspect
import re

import spacy
from pyresparser import ResumeParser, utils, constants as cs
from spacy.matcher import Matcher


class CustomResumeParser(ResumeParser):
    def __init__(
            self,
            resume,
            skills_file=None,
            custom_regex=None
    ):
        nlp = spacy.load('en_core_web_sm')
        custom_nlp = spacy.load(os.path.dirname(os.path.abspath(inspect.getfile(ResumeParser))))
        self.__skills_file = skills_file
        self.__custom_regex = custom_regex
        self.__matcher = Matcher(nlp.vocab)
        self.__details = {
            'name': None,
            'email': None,
            'skills': None,
            'education': None,
            'college_name': None,
            'degree': None,
            'designation': None,
            'experience': None,
            'company_names': None,
            'no_of_pages': None,
            'total_experience': None,
        }
        self.__resume = resume
        if not isinstance(self.__resume, io.BytesIO):
            ext = os.path.splitext(self.__resume)[1].split('.')[1]
        else:
            ext = self.__resume.name.split('.')[1]
        self.__text_raw = utils.extract_text(self.__resume, '.' + ext)
        self.__text = ' '.join(self.__text_raw.split())
        self.__nlp = nlp(self.__text)
        self.__custom_nlp = custom_nlp(self.__text_raw)
        self.__noun_chunks = list(self.__nlp.noun_chunks)
        self.__get_basic_details()

    def get_extracted_data(self):
        return self.__details

    def __get_basic_details(self):
        cust_ent = utils.extract_entities_wih_custom_model(
            self.__custom_nlp
        )
        name = utils.extract_name(self.__nlp, matcher=self.__matcher)
        email = utils.extract_email(self.__text)
        mobile = utils.extract_mobile_number(self.__text, self.__custom_regex)
        skills = utils.extract_skills(
            self.__nlp,
            self.__noun_chunks,
            self.__skills_file
        )
        edu = extract_education_with_gpa(
                      [sent.string.strip() for sent in self.__nlp.sents]
              )
        # TODO: Extract concentration, gpa, work experiences from entities
        entities = utils.extract_entity_sections_grad(self.__text_raw)

        # if 'education' in entities:
        #     gpa = extract_gpa(entities['education'])

        # extract name
        try:
            self.__details['name'] = cust_ent['Name'][0]
        except (IndexError, KeyError):
            self.__details['name'] = name

        # extract email
        self.__details['email'] = email

        # extract skills
        self.__details['skills'] = skills

        # TODO: Currently extracting degree and year, not concentration nor university
        self.__details['education'] = edu

        # extract college name
        try:
            self.__details['college_name'] = entities['College Name']
        except KeyError:
            pass

        # extract education Degree
        try:
            self.__details['degree'] = cust_ent['Degree']
        except KeyError:
            pass

        # extract designation
        try:
            self.__details['designation'] = cust_ent['Designation']
        except KeyError:
            pass

        # extract company names
        try:
            self.__details['company_names'] = cust_ent['Companies worked at']
        except KeyError:
            pass

        try:
            self.__details['experience'] = entities['experience']
            try:
                exp = round(
                    utils.get_total_experience(entities['experience']) / 12,
                    2
                )
                self.__details['total_experience'] = exp
            except KeyError:
                self.__details['total_experience'] = 0
        except KeyError:
            self.__details['total_experience'] = 0
        self.__details['no_of_pages'] = utils.get_number_of_pages(
            self.__resume
        )
        return


def extract_education_with_gpa(nlp_text):
    '''
        Helper function to extract education from spacy nlp text

        :param nlp_text: object of `spacy.tokens.doc.Doc`
        :return: tuple of education degree and year if year if found
                 else only returns education degree
        '''
    edu = {}
    # Extract education degree
    try:
        for index, text in enumerate(nlp_text):
            for tex in text.split():
                tex = re.sub(r'[?|$|.|!|,]', r'', tex)
                if tex.upper() in cs.EDUCATION and tex not in cs.STOPWORDS:
                    edu[tex] = text + nlp_text[index + 1]
    except IndexError:
        pass

    # Extract year and gpa if available
    education = []
    gpa_regex = r'(\d{1})\.(\d{1,2})'
    for key in edu.keys():
        year = re.search(re.compile(cs.YEAR), edu[key])
        gpa = re.search(re.compile(gpa_regex), edu[key])
        edu_tuple = (key,)
        if year:
            edu_tuple = edu_tuple + (''.join(year.group(0)),)
        if gpa:
            edu_tuple = edu_tuple + (gpa.group(),)

        if gpa or year:
            education.append(edu_tuple)
        else:
            education.append(key)
    return education


