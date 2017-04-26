"""
Helper for encoding and decoding of data communicated through
Mercanet's POST api
"""

import hashlib


class MercanetDecodeError(Exception):
    pass

class MercanetPayload(object):
    """
    Represents a Mercanet payload. Storing of parameters inside the
    "Data" field is done using the square brackets ([]) operator.

    Named (optional) parameters:
    - secret_key: str (defaults to the Mercanet demo secret key)
    - initial_data: dict (for passing an already populated Data field)
    """
    def __init__(self, secret_key="002001000000001_KEY1", initial_data={}):
        self._secret_key = secret_key
        self._data = initial_data

    def encode(self):
        """
        Encodes and signs (seals) a Mercanet payload.
        
        returns a dict combining the "Data" field and a Seal (the
        sha256 hash of the encoded "Data" field concatenated with the
        secret_key)
        """
        fields = \
                {
                    "Data": "",
                    "Seal": ""
                }
        
        for key, value in self._data.items():
            if fields["Data"] != "":
                fields["Data"] += "|"
            
            fields["Data"] += "{0}={1}".format(key, value)

        digestor = hashlib.sha256()
        digestor.update(str.encode(fields["Data"]))
        digestor.update(str.encode(self._secret_key))

        fields["Seal"] = digestor.hexdigest()

        return fields

    def encode_as_form(self):
        """
        Returns an HTML form containing the properly encoded Mercanet
        payload.

        It is suitable for integration in a Django template and will
        be displayed by web browsers as a button on which the end user
        can simply click to proceed to payment.
        """
        fields = self.encode()

        html_template = open("test.html")
        html_code = html_template.read()
        html_template.close()

        return html_code.format(fields["Data"], fields["Seal"])

    def decode(self, payload):
        """
        Loads a Mercanet payload with encoded "Data" field and verifies it
        is properly sealed.

        Raises an exception if the seal does not match.
        """
        digestor = hashlib.sha256()
        digestor.update(str.encode(payload["Data"]))
        digestor.update(str.encode(self._secret_key))

        if digestor.hexdigest() != payload["Seal"]:
            raise MercanetDecodeError("Seals do not match")
        else:
            for element in payload["Data"].split("|"):
                element = element.split("=")
                self._data[element[0]] = element[1]

    def __setitem__(self, key, value):
        self._data[key] = value
        return value

    def __getitem__(self, key):
        return self._data[key]
