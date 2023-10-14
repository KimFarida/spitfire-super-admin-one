import logging
from flask import jsonify, Blueprint, current_app as app
import datetime
from dotenv import load_dotenv

from health.utils import clean_up, check_endpoint

load_dotenv(".env")

logging.basicConfig(filename='health_check.log', level=logging.ERROR)
health_check_blueprint = Blueprint("health_check", __name__,
                                   url_prefix="/api/admin/health")
HEALTH_LOGS = []


from health.create_assessment import TO_CHECK as create_assessment

ENDPOINTS_TO_CHECK = [
    create_assessment,
]

@health_check_blueprint.route("/", methods=["GET"])
def health():
    health_results = []
    to_clean = []

    for endpoints_data in ENDPOINTS_TO_CHECK:
        base_url, endpoints, datas = endpoints_data
        for endpoint, data in zip(endpoints, datas):
            status, to_clean_obj = check_endpoint(
                base_url,
                endpoint=endpoint,
                data=data,
                to_clean_ids=to_clean
            )

            to_clean.append(to_clean_obj)

            health_results.append({
                "endpoint": f"{endpoint[0]} {base_url}{endpoint[1]}",
                "status": status
            })

    for table, obj_id in to_clean:
        clean_up(table, obj_id)

    # Log health check results along with timestamp
    log_timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_entry = {"timestamp": log_timestamp, "results": health_results}
    HEALTH_LOGS.append(log_entry)

    return jsonify(health_results)

@health_check_blueprint.route("/last_check", methods=["GET"])
def last_check():
    # Retrieve the last health check log entry
    if HEALTH_LOGS:
        last_check_entry = HEALTH_LOGS[-1]
        return jsonify(last_check_entry)
    else:
        return jsonify({"message": "No health check logs available"}), 404
