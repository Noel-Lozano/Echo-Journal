from flask import Blueprint, render_template_string, request, session, jsonify
from app.models.profile import Profile
from app import db

profile_bp = Blueprint("profile", __name__)

PROFILE_HTML = """
<!doctype html>
<title>Profile</title>
<h2>Your Profile</h2>
<textarea id="profileText" rows="10" cols="50" placeholder="Type something...">{{ text }}</textarea>

<script>
const textarea = document.getElementById("profileText");

textarea.addEventListener("input", () => {
    fetch("/profile", {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify({ text: textarea.value })
    })
    .then(res => res.json())
});
</script>
"""

@profile_bp.route("/profile", methods=["GET", "POST"])
def profile():
    user_id = session.get("user_id")
    if not user_id:
        return "Not logged in", 401

    profile = Profile.query.filter_by(user_id=user_id).first()

    if request.method == "POST":
        data = request.get_json()
        text = data.get("text", "")
        if profile:
            profile.text = text
        else:
            profile = Profile(user_id=user_id, text=text)
            db.session.add(profile)
        db.session.commit()
        return jsonify({"status": "success"})

    return render_template_string(PROFILE_HTML, text=profile.text if profile else "")
