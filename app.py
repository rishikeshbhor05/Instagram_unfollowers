import logging
import os
import re
import uuid
import zipfile
import json

from flask import Flask, render_template, request
from werkzeug.utils import secure_filename

# --------------------------------
# App setup
# --------------------------------

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
UPLOAD_FOLDER = os.path.join(BASE_DIR, "uploads")
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

app = Flask(__name__)
app.config["MAX_CONTENT_LENGTH"] = 50 * 1024 * 1024  # 50 MB upload cap

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def extract_following_usernames(data):
    """
    Extract usernames from Instagram following.json.

    Instagram stores the username in:
        "title": "username"
    """

    usernames = set()

    if isinstance(data, dict):
        following = data.get("relationships_following", [])

        for account in following:

            if not isinstance(account, dict):
                continue

            username = account.get("title")

            if isinstance(username, str):

                username = username.strip().lower()

                if username:
                    usernames.add(username)

    return usernames


def extract_follower_usernames(data):
    """
    Extract usernames from Instagram followers_*.json.

    Instagram stores the username in:
        string_list_data -> value
    """

    usernames = set()

    def walk(obj):

        if isinstance(obj, dict):

            string_list_data = obj.get("string_list_data")

            if isinstance(string_list_data, list):

                for item in string_list_data:

                    if isinstance(item, dict):

                        username = item.get("value")

                        if isinstance(username, str):

                            username = username.strip().lower()

                            if username:
                                usernames.add(username)

            for value in obj.values():
                walk(value)

        elif isinstance(obj, list):

            for item in obj:
                walk(item)

    walk(data)

    return usernames


def find_instagram_files(zip_file):

    follower_files = []
    following_file = None

    # Matches "followers_1.json" AND plain "followers.json"
    # (small accounts sometimes export a single un-numbered file)
    follower_pattern = re.compile(r"followers(_\d+)?\.json$")

    for filename in zip_file.namelist():

        normalized = filename.replace("\\", "/").lower()
        basename = normalized.split("/")[-1]

        if follower_pattern.match(basename):
            follower_files.append(filename)

        elif basename == "following.json":
            following_file = filename

    follower_files.sort()

    return follower_files, following_file


@app.route("/", methods=["GET", "POST"])
def index():

    if request.method == "POST":

        uploaded_file = request.files.get("instagram_data")

        if not uploaded_file or not uploaded_file.filename:
            return render_template(
                "index.html",
                error="Please select your Instagram ZIP file."
            )

        if not uploaded_file.filename.lower().endswith(".zip"):
            return render_template(
                "index.html",
                error="Please upload the ZIP file downloaded from Instagram."
            )

        # Sanitize the filename and make it unique so concurrent
        # uploads (or repeat uploads of the same filename) never collide.
        safe_name = secure_filename(uploaded_file.filename) or "upload.zip"
        zip_path = os.path.join(UPLOAD_FOLDER, f"{uuid.uuid4().hex}_{safe_name}")

        uploaded_file.save(zip_path)

        try:

            with zipfile.ZipFile(zip_path, "r") as zip_file:

                # --------------------------------
                # Find Instagram files
                # --------------------------------

                follower_files, following_file = find_instagram_files(
                    zip_file
                )

                if not follower_files:
                    return render_template(
                        "index.html",
                        error="Could not find your followers data."
                    )

                if not following_file:
                    return render_template(
                        "index.html",
                        error="Could not find your following data."
                    )

                # --------------------------------
                # Read ALL follower files
                # --------------------------------

                followers = set()

                for follower_file in follower_files:

                    logger.info("Reading follower file: %s", follower_file)

                    with zip_file.open(follower_file) as file:

                        follower_data = json.load(file)

                        extracted = extract_follower_usernames(follower_data)

                        logger.info(
                            "Extracted %d usernames from %s",
                            len(extracted), follower_file
                        )

                        followers.update(extracted)

                logger.info("Total followers extracted: %d", len(followers))

                # --------------------------------
                # Read following.json
                # --------------------------------

                with zip_file.open(following_file) as file:

                    following_data = json.load(file)

                    following = extract_following_usernames(
                        following_data
                    )

                logger.info("Total following extracted: %d", len(following))

                # --------------------------------
                # Compare
                # --------------------------------

                not_following_back = sorted(
                    following - followers
                )

                logger.info(
                    "Follower files: %d | Followers: %d | Following: %d | "
                    "Don't follow back: %d",
                    len(follower_files), len(followers),
                    len(following), len(not_following_back)
                )

                # --------------------------------
                # Send results to HTML
                # --------------------------------

                return render_template(
                    "index.html",

                    results=not_following_back,

                    followers_count=len(followers),

                    following_count=len(following),

                    result_count=len(not_following_back)
                )

        except zipfile.BadZipFile:

            return render_template(
                "index.html",
                error="The uploaded file is not a valid ZIP file."
            )

        except json.JSONDecodeError:

            return render_template(
                "index.html",
                error="Could not read Instagram's JSON data."
            )

        except Exception as e:

            logger.exception("Unexpected error while processing upload")

            return render_template(
                "index.html",
                error=f"Something went wrong: {str(e)}"
            )

        finally:

            # Delete uploaded ZIP after processing
            if os.path.exists(zip_path):

                os.remove(zip_path)

    # --------------------------------
    # Normal GET request
    # --------------------------------

    return render_template("index.html")


if __name__ == "__main__":
    # debug mode is OFF by default. Only turn it on locally by running:
    #   FLASK_DEBUG=1 python app.py
    # Never enable it on a publicly reachable deployment — the Werkzeug
    # debugger allows remote code execution if left on.
    debug_mode = os.environ.get("FLASK_DEBUG") == "1"
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=debug_mode)