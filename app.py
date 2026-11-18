
import streamlit as st
from supabase import create_client

st.set_page_config(page_title="Feedback", page_icon="📝")
st.markdown("""
<style>
.stApp {
    background-color: #f8f5ff;
    color: #29213d;
}

h1, h2, h3 {
    color: #6d28d9 !important;
}

.stTextInput input,
.stTextArea textarea {
    background-color: #211936;
    color: white;
    border: 1px solid #7045a5;
    border-radius: 10px;
}

.stButton button,
.stFormSubmitButton button {
    background-color: #7c3aed;
    color: white;
    border: none;
    border-radius: 10px;
    padding: 10px 22px;
}

.stButton button:hover,
.stFormSubmitButton button:hover {
    background-color: #9333ea;
    color: white;
}
</style>
""", unsafe_allow_html=True)

st.title("💜 Feedback Dashboard")

st.markdown("""
<div style="
    background: linear-gradient(135deg, #251442, #4c1d95);
    padding: 22px;
    border-radius: 15px;
    margin-bottom: 25px;
">
    <h3 style="color:white;">Welcome to your Feedback Space!</h3>
    <p style="color:#e9d5ff;">
        Share your thoughts, suggestions and experiences with us.
        Your feedback helps us improve.
    </p>
</div>
""", unsafe_allow_html=True)

# Connect to Supabase
try:
    url = st.secrets["SUPABASE_URL"]
    key = st.secrets["SUPABASE_PUBLISHABLE_KEY"]

    if "_supabase" not in st.session_state:
        st.session_state["_supabase"] = create_client(url, key)

    db = st.session_state["_supabase"]

    if "access_token" in st.session_state:
        db.postgrest.auth(st.session_state.access_token)

except Exception as e:
    st.error(f"Supabase connection error: {e}")
    st.stop()

# Check login
if "user" not in st.session_state:
    st.session_state.user = None

if st.session_state.user is None:

    st.markdown("""
    <div style="
        background: linear-gradient(135deg, #251442, #4c1d95);
        padding: 25px;
        border-radius: 16px;
        text-align: center;
        margin-bottom: 25px;
    ">
        <h2 style="color: white;">💜 Welcome Back!</h2>
        <p style="color: #e9d5ff;">
            Sign in to access your Feedback Dashboard
        </p>
    </div>
    """, unsafe_allow_html=True)

    st.subheader("🔐 Sign In to Continue")

    email = st.text_input("📧 Email Address")
    password = st.text_input("🔑 Password", type="password")

    if st.button("Sign in"):
        try:
            response = db.auth.sign_in_with_password({
                "email": email.strip(),
                "password": password
            })

            st.session_state.user = response.user
            st.session_state.access_token = response.session.access_token

            db.postgrest.auth(response.session.access_token)

            st.rerun()

        except Exception as e:
            st.error(f"Login failed: {e}")

    st.stop()

# Signed-in user
st.success(f"Signed in as {st.session_state.user.email}")

if st.button("Sign out"):
    db.auth.sign_out()
    st.session_state.user = None
    st.session_state.pop("access_token", None)
    st.session_state.pop("_supabase", None)
    st.rerun()

# Feedback form
st.markdown("""
<div style="
    background-color: #211936;
    padding: 18px;
    border-radius: 14px;
    border-left: 5px solid #9333ea;
    margin-top: 20px;
">
    <h3 style="color: #c4a7ff;">📝 Submit Your Feedback</h3>
    <p style="color: #ddd6fe;">
        Tell us what you think. Your opinion matters!
    </p>
</div>
""", unsafe_allow_html=True)

with st.form("feedback_form"):
    name = st.text_input("Your name", max_chars=100)
    message = st.text_area("Your message", max_chars=2000)

    submitted = st.form_submit_button("Save Feedback")

    if submitted:
        if not name.strip() or not message.strip():
            st.warning("Please enter both your name and message.")
        else:
            try:
                db.table("app_feedback").insert({
                    "name": name.strip(),
                    "message": message.strip()
                }).execute()

                st.success("Feedback saved successfully!")

            except Exception as e:
                st.error(f"Could not save feedback: {e}")

# Display feedback
st.markdown("""
<div style="
    background-color: #211936;
    padding: 18px;
    border-radius: 14px;
    border-left: 5px solid #a855f7;
    margin-top: 25px;
">
    <h3 style="color: #c4a7ff;">💬 Recent Feedback</h3>
    <p style="color: #ddd6fe;">
        Here are your latest submitted messages.
    </p>
</div>
""", unsafe_allow_html=True)
try:
    result = (
        db.table("app_feedback")
        .select("id, name, message, created_at")
        .order("created_at", desc=True)
        .limit(50)
        .execute()
    )

    st.metric("📊 Your Total Feedback", len(result.data))
    search_text = st.text_input(
    "🔍 Search Feedback",
    placeholder="Search by name or message..."
)
    filtered_data = [
    item for item in result.data
    if search_text.strip().lower() in item["name"].lower()
    or search_text.strip().lower() in item["message"].lower()
]
    if filtered_data:
        for item in filtered_data:
            with st.container(border=True):
                st.markdown(f"#### 👤 {item['name']}")
                st.write(item["message"])
                st.caption(item["created_at"])

                with st.expander("✏️ Edit Feedback"):
                    with st.form(key=f"edit_form_{item['id']}"):
                        edited_name = st.text_input(
                            "Update your name",
                            value=item["name"]
                        )

                        edited_message = st.text_area(
                            "Update your message",
                            value=item["message"]
                        )

                        save_edit = st.form_submit_button("Save Changes")

                        if save_edit:
                            if not edited_name.strip() or not edited_message.strip():
                                st.warning("Please fill in both fields.")
                            else:
                                try:
                                    db.table("app_feedback").update({
                                        "name": edited_name.strip(),
                                        "message": edited_message.strip()
                                    }).eq("id", item["id"]).execute()

                                    st.success("Feedback updated successfully!")
                                    st.rerun()

                                except Exception as e:
                                    st.error(f"Could not update feedback: {e}")

                if st.button("🗑️ Delete", key=f"delete_{item['id']}"):
                    try:
                        db.table("app_feedback").delete().eq(
                            "id", item["id"]
                        ).execute()

                        st.success("Feedback deleted successfully!")
                        st.rerun()

                    except Exception as e:
                        st.error(f"Could not delete feedback: {e}")

    else:
        st.info("No feedback submitted yet.")

    

except Exception as e:
    st.error(f"Could not load feedback: {e}")
#Footer
st.markdown("""
<div style="
    text-align: center;
    padding: 20px;
    margin-top: 35px;
    color: #888888;
    border-top: 1px solid #dddddd;
">
    <p>Made with 💜 | Feedback Management System</p>
    <p>Share your thoughts. Help us improve.</p>
</div>
""", unsafe_allow_html=True)
