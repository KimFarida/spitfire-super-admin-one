from health import check_endpoint


def extract_assessment_id(response: dict) -> tuple[str, str]:
    assessment_id = response['data']['assessment_id']

    return 'assessment', assessment_id


BASE_URL = "https://piranha-assessment.onrender.com"
ENDPOINTS = [
    ("GET", "/api/admin/assessments/", None),
    ("POST", "/api/admin/assessments/", extract_assessment_id),
    ("DELETE", "/api/admin/assessments/{}", None),
]
DATA = [
    None,
    {},
    None,
]

TO_CHECK = (BASE_URL, ENDPOINTS, DATA)


