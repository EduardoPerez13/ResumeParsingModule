import os
import csv

from resume_parser.custom_resume_parser import CustomResumeParser
from pyresparser.command_line import print_cyan
from pprint import pprint as pp


def print_parsed_resume(file):
    data = CustomResumeParser(file).get_extracted_data()
    print(data)


def parse_resume_directory(directory, skills_file=None, custom_regex=None):
    results = []
    if os.path.exists(directory):
        pool = mp.Pool(mp.cpu_count())

        resumes = []
        for root, dirs, filenames in os.walk(directory):
            for filename in filenames:
                file = os.path.join(root, filename)
                resumes.append([file, skills_file, custom_regex])
        results = pool.map(resume_result_wrapper, resumes)
        pool.close()
        pool.join()
    return results


def resume_result_wrapper(args):
    print_cyan('Extracting data from: {}'.format(args[0]))
    parser = CustomResumeParser(args[0], args[1], args[2])
    return parser.get_extracted_data()


def parse_directory_to_csv(directory):
    """
    Function parses resumes from a directory and writes the parsed information in a csv file
    :param directory: Contains two directories, one with 'experienced' resumes and another with 'inexperienced' resumes
    :return: None
    """
    with open('resume_parser/parsed_results.csv', mode='w') as parse_results_file:
        field_names = ['name', 'email', 'skills', 'education', 'college_name', 'degree',
                       'designation', 'experience', 'company_names', 'no_of_pages',
                       'total_experience', 'label']
        parse_writer = csv.DictWriter(parse_results_file, fieldnames=field_names)
        parse_writer.writeheader()
        for resume_type in ('Experienced', 'Inexperienced'):
            results = parse_resume_directory('%s/%s' % (directory, resume_type))
            for parse_result in results:
                parse_result['label'] = 1 if resume_type == 'Experienced' else 0
                parse_writer.writerow(parse_result)


if __name__ == '__main__':
    # print_parsed_resume('C:/Users/Eduardo Perez/Documents/Resume/RESUME_EduardoAPerezVega2020sinAcentos.pdf')
    # print_parsed_resume('resumes/Experienced/PWC_Olivia Peter_Regulatory Manager.pdf')
    pp(parse_resume_directory('resume_parser/resumes/Experienced', skills_file='resume_parser/skills_dataset.csv'))
    # parse_directory_to_csv('resumes')

    # df = pandas.read_csv('parsed_results.csv', encoding='cp1252')
    # print(df)

    # Convert skills txt file to csv
    # skills = pandas.read_csv("C:/Users/Eduardo Perez/Downloads/linkedin_skills.txt",
    #                          names=('technical skills',), sep='\n')
    # skills.to_csv('skills_dataset.csv', index=None)

