import os
import csv

from resume_parser.custom_resume_parser import CustomResumeParser
from pyresparser.command_line import print_cyan
from pprint import pprint as pp


def print_parsed_resume(file):
    data = CustomResumeParser(file).get_extracted_data()
    print(data)


def parse_resume_directory(directory, custom_regex=None):
    results = []
    skills_file = 'resume_parser/skills_dataset.csv'
    if os.path.exists(directory):
        # pool = mp.Pool(mp.cpu_count())

        resumes = []
        for root, dirs, filenames in os.walk(directory):
            for filename in filenames:
                file = os.path.join(root, filename)
                resumes.append([file, skills_file, custom_regex])
        results = map(resume_result_wrapper, resumes)
        # results = pool.map(resume_result_wrapper, resumes)
        # pool.close()
        # pool.join()
    return list(results)


def resume_result_wrapper(args):
    print_cyan('Extracting data from: {}'.format(args[0]))
    parser = CustomResumeParser(args[0], args[1], args[2])
    return parser.get_extracted_data()


def parse_dataset_to_csv():
    """
    Function parses resumes from a directory and writes the parsed information in a csv file
    :return: None
    """
    csv_file = 'resume_parser/parsed_results.csv'
    with open(csv_file, mode='w') as parse_results_file:
        field_names = ['skills', 'education', 'college_name', 'degree',
                       'designation', 'experience', 'company_names',
                       'total_experience', 'label']
        parse_writer = csv.DictWriter(parse_results_file, fieldnames=field_names)
        parse_writer.writeheader()
        for resume_type in ('Experienced', 'Inexperienced'):
            results = parse_resume_directory('resume_parser/%s/%s' % ('resumes', resume_type))
            for parse_result in results:
                parse_result['label'] = 1 if resume_type == 'Experienced' else 0
                parse_writer.writerow(parse_result)


def parse_directory_to_csv(directory, csv_file):
    """

    :param directory: Name of directory containing resumes to parse
    :param csv_file: Name of file where parsed resumes will be stored in csv format
    :return: None
    """
    with open(csv_file, mode='w') as parse_csv:
        field_names = ['skills', 'education', 'college_name', 'degree',
                       'designation', 'experience', 'company_names',
                       'total_experience', 'label']
        parse_writer = csv.DictWriter(parse_csv, fieldnames=field_names)
        parse_writer.writeheader()
        results = parse_resume_directory(directory)
        for parse_result in results:
            parse_writer.writerow(parse_result)


if __name__ == '__main__':
    # print_parsed_resume('C:/Users/Eduardo Perez/Documents/Resume/RESUME_EduardoAPerezVega2020sinAcentos.pdf')
    # pp(parse_resume_directory('resume_parser/resumes/Experienced', skills_file='resume_parser/skills_dataset.csv'))

    # Parse training set resumes
    parse_dataset_to_csv()

    # Convert skills txt file to csv
    # skills = pandas.read_csv("C:/Users/Eduardo Perez/Downloads/linkedin_skills.txt",
    #                          names=('technical skills',), sep='\n')
    # skills.to_csv('skills_dataset.csv', index=None)

