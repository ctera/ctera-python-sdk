import getpass

class CTERASDKSampleBase:
    _password_request_string = "the password for {username}"

    @staticmethod
    def _get_password(username):
        return CTERASDKSampleBase._get_input(CTERASDKSampleBase._password_request_string.format(username=username), echo=False)

    @staticmethod
    def _get_input(prompt, echo=True):
        prompt = "Please enter {prompt}: ".format(prompt=prompt)
        response = None
        while not response:
            if echo:
                response = input(prompt)
            else:
                response = getpass.getpass(prompt)
        return response
