from fhir import *
import json

# JSON format and data elements for the Patient resource
headers = {'content-type': 'application/json'}
    
body = json.dumps({"resourceType":"Patient",
    "name":[{"use":"official", "family":["Ana"], "given":["Betz"]}],
    "identifier":[{"use":"usual", "label":"SSN", "value":"55567890"}],
    "gender": {
        "coding": [
            {
            "system": "http://hl7.org/fhir/v3/AdministrativeGender",
            "code": "F",
            "display": "Female"
            }
        ]},
    "birthdate":"1985-10-04",
    "deceasedBoolean": False,
    "active": True
    })

# XML format Patient data elements (body)
#Header for XML
#headers = {'content-type': 'application/xml'}

#body = "<Patient xmlns=\"http://hl7.org/fhir\">" \
#    "<name><family>John</family></name></Patient>"

query = RestfulFHIR().create('http://fhir.healthintersections.com.au/open'
    ,'Patient', body, headers)

print query
print query.text

