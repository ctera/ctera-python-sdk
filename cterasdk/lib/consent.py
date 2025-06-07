from ..exceptions import UserConsentError


def ask(question):
    answer = None
    answers = ['Y', 'n']
    question = question + ' (' + '/'.join(answers) + '): '

    try:
        while answer not in answers:
            try:
                answer = input(question)
            except EOFError:
                raise UserConsentError()

    except KeyboardInterrupt:
        answer = 'n'
    if answer == 'Y':
        return True
    return False
