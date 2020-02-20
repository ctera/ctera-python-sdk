from ..exception import ConsentException


def ask(question):
    answer = None
    answers = ['Y', 'n']
    question = question + ' (' + '/'.join(answers) + '): '

    try:
        while answer not in answers:
            try:
                answer = input(question)
            except EOFError:
                raise ConsentException()

    except KeyboardInterrupt:
        answer = 'n'
    if answer == 'Y':
        return True
    return False
