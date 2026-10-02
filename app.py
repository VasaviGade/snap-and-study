import time

import streamlit as st
from google import genai
from google.genai import types
from prompts import SYSTEM_PROMPT, SUMMARY_PROMPT

import smtplib
from email.mime.text import MIMEText


# =========================================================
# GEMINI CLIENT 
# =========================================================

client = genai.Client(
    api_key=st.secrets["GEMINI_API_KEY"]
)


# =========================================================
# GEMINI REQUEST WITH RETRY 
# =========================================================

def generate_with_retry(contents, config=None):

    max_attempts = 3

    for attempt in range(max_attempts):

        try:

            response = client.models.generate_content(
                model="gemini-3.5-flash",
                contents=contents,
                config=config
            )

            return response

        except Exception as e:

            error_text = str(e)

            # Retry only temporary server errors

            if "503" in error_text or "UNAVAILABLE" in error_text:

                if attempt < max_attempts - 1:

                    wait_time = 2 ** attempt

                    time.sleep(wait_time)

                else:

                    raise e

            else:

                raise e


# =========================================================
# EMAIL FUNCTION TO SEND STUDY SUMMARY
# =========================================================

def send_email(to_email, subject, body):

    sender_email = st.secrets["GMAIL_ADDRESS"]
    app_password = st.secrets["GMAIL_APP_PASSWORD"]

    message = MIMEText(body)

    message["Subject"] = subject
    message["From"] = sender_email
    message["To"] = to_email

    with smtplib.SMTP(
        "smtp.gmail.com",
        587,
        timeout=30
    ) as server:

        server.ehlo()

        server.starttls()

        server.ehlo()

        server.login(
            sender_email,
            app_password
        )

        server.sendmail(
            sender_email,
            to_email,
            message.as_string()
        )


# =========================================================
# SESSION STATE
# =========================================================

if "name" not in st.session_state:
    st.session_state.name = ""

if "email" not in st.session_state:
    st.session_state.email = ""

if "started" not in st.session_state:
    st.session_state.started = False

if "messages" not in st.session_state:
    st.session_state.messages = []


# =========================================================
# APP TITLE
# =========================================================

st.title("📚 Snap & Study")

st.write(
    "Your AI study buddy for questions, diagrams, and notes."
)


# =========================================================
# ONBOARDING
# =========================================================

if not st.session_state.started:

    st.subheader("Let's get started! 👋")

    name = st.text_input(
        "👤 Your Name",
        value=st.session_state.name
    )

    email = st.text_input(
        "📧 Your Email",
        value=st.session_state.email
    )

    if st.button("🚀 Start Studying"):

        if name.strip() and email.strip():

            st.session_state.name = name.strip()
            st.session_state.email = email.strip()
            st.session_state.started = True

            st.rerun()

        else:

            st.warning(
                "Please enter your name and email."
            )


# =========================================================
# STUDY SCREEN
# =========================================================

else:

    st.success(
        f"Welcome back, {st.session_state.name}! 🎓"
    )


    # -----------------------------------------------------
    # CONVERSATION HISTORY
    # -----------------------------------------------------

    if st.session_state.messages:

        st.subheader("💬 Your Study Conversation")

        for message in st.session_state.messages:

            if message["role"] == "user":

                st.chat_message("user").write(
                    message["content"]
                )

            else:

                st.chat_message("assistant").write(
                    message["content"]
                )


    # -----------------------------------------------------
    # IMAGE UPLOAD
    # -----------------------------------------------------

    st.subheader("📸 Upload your study material")

    uploaded_image = st.file_uploader(
        "Upload a question, diagram, or notes",
        type=["jpg", "jpeg", "png"],
        key="study_image"
    )


    # -----------------------------------------------------
    # IMAGE + QUESTION
    # -----------------------------------------------------

    if uploaded_image:

        st.image(
            uploaded_image,
            caption="Your uploaded image"
        )

        image_bytes = uploaded_image.getvalue()

        mime_type = uploaded_image.type

        question = st.text_input(
            "✏️ What would you like me to explain?",
            key="study_question"
        )


        # -------------------------------------------------
        # EXPLAIN WITH AI
        # -------------------------------------------------

        if st.button(
            "🧠 Explain with AI",
            key="explain_button"
        ):

            if question.strip():

                with st.spinner(
                    "Analyzing your study material..."
                ):

                    try:

                        image_part = types.Part.from_bytes(
                            data=image_bytes,
                            mime_type=mime_type
                        )


                        response = generate_with_retry(
                            contents=[
                                image_part,
                                question
                            ],
                            config=types.GenerateContentConfig(
                                system_instruction=SYSTEM_PROMPT
                            )
                        )


                        # ---------------------------------
                        # SAVE CONVERSATION
                        # ---------------------------------

                        st.session_state.messages.append(
                            {
                                "role": "user",
                                "content": question
                            }
                        )

                        st.session_state.messages.append(
                            {
                                "role": "assistant",
                                "content": response.text
                            }
                        )


                        # ---------------------------------
                        # DISPLAY ANSWER
                        # ---------------------------------

                        st.subheader(
                            "🤖 Snap & Study Explanation"
                        )

                        st.write(
                            response.text
                        )


                    except Exception as e:

                        st.error(
                            "❌ Gemini is temporarily unavailable."
                        )

                        st.write(
                            f"Gemini error: {e}"
                        )

            else:

                st.warning(
                    "Please enter a question."
                )


    # =====================================================
    # EMAIL SUMMARY
    # =====================================================

    if st.session_state.messages:

        st.divider()

        st.subheader(
            "📧 Save Your Study Summary"
        )

        st.write(
            f"Summary will be sent to: "
            f"**{st.session_state.email}**"
        )


        if st.button(
            "📨 Send Study Summary",
            key="email_button"
        ):

            # ---------------------------------------------
            # BUILD CONVERSATION TEXT
            # ---------------------------------------------

            conversation_text = ""

            for message in st.session_state.messages:

                if message["role"] == "user":

                    conversation_text += (
                        "Student: "
                        + message["content"]
                        + "\n\n"
                    )

                else:

                    conversation_text += (
                        "AI Study Assistant: "
                        + message["content"]
                        + "\n\n"
                    )


            # ---------------------------------------------
            # CREATE SUMMARY
            # ---------------------------------------------

            with st.spinner(
                "Creating your study summary..."
            ):

                try:

                    summary_response = generate_with_retry(
                        contents=[
                            SUMMARY_PROMPT
                            + conversation_text
                        ]
                    )

                    summary = summary_response.text


                except Exception:

                    # If Gemini is temporarily unavailable,
                    # email the conversation itself.

                    summary = (
                        "Your Snap & Study Conversation\n\n"
                        "Gemini was temporarily unavailable "
                        "while creating the summary.\n\n"
                        "Here is your study conversation:\n\n"
                        + conversation_text
                    )


                    st.warning(
                        "Gemini was temporarily unavailable. "
                        "Your conversation will be emailed instead."
                    )


            # ---------------------------------------------
            # SEND EMAIL
            # ---------------------------------------------

            with st.spinner(
                "Sending your email..."
            ):

                try:

                    send_email(
                        st.session_state.email,
                        "📚 Your Snap & Study Summary",
                        summary
                    )

                    st.success(
                        "✅ Your study summary has been sent!"
                    )

                    st.info(
                        f"Please check: "
                        f"{st.session_state.email}"
                    )


                except Exception as e:

                    st.error(
                        "❌ Email could not be sent."
                    )

                    st.write(
                        f"Email error: {e}"
                    )