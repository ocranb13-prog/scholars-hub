"""
app.py
------
Scholars HUB corporate website.

Serves the public marketing pages (server-rendered with Jinja2 so the
navbar/footer live in one place) and exposes two small JSON APIs that
write lead data into Firebase Firestore:

    POST /api/contact        -> collection "contact_messages"
    POST /api/book-service   -> collection "service_bookings"

There are no user accounts, sessions, or authentication anywhere in
this app - it is a lead-generation / brochure site, not a portal.
"""

import os
import smtplib
import ssl
from datetime import datetime, timezone
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from dotenv import load_dotenv
from flask import Flask, render_template, request, jsonify

from firebase_config import db

load_dotenv()  # reads a local .env file if present (see .env.example)

app = Flask(__name__)

# ---------------------------------------------------------------------
# Email notifications
# ---------------------------------------------------------------------
# Whenever someone submits the Contact form or the Book a Service form,
# we save it to Firestore (as before) AND email the team so a booking
# or message doesn't just sit unnoticed in the database. Configure the
# SMTP_* variables below via a .env file - see backend/.env.example.
SMTP_HOST = os.environ.get("SMTP_HOST")
SMTP_PORT = int(os.environ.get("SMTP_PORT", "587"))
SMTP_USERNAME = os.environ.get("SMTP_USERNAME")
SMTP_PASSWORD = os.environ.get("SMTP_PASSWORD")
SMTP_FROM = os.environ.get("SMTP_FROM", SMTP_USERNAME)
NOTIFY_EMAIL = os.environ.get("NOTIFY_EMAIL", "scholarshub26@outlook.com")


def send_notification_email(subject, body_lines):
    """
    Best-effort email notification to NOTIFY_EMAIL.

    This must never break a form submission: the Firestore write already
    succeeded by the time this is called, so if SMTP isn't configured or
    sending fails for any reason, we just log a warning and move on.
    """
    if not (SMTP_HOST and SMTP_USERNAME and SMTP_PASSWORD):
        app.logger.warning(
            "Skipping email '%s' - SMTP_HOST/SMTP_USERNAME/SMTP_PASSWORD "
            "are not configured. See backend/.env.example.",
            subject,
        )
        return

    msg = MIMEMultipart()
    msg["From"] = SMTP_FROM
    msg["To"] = NOTIFY_EMAIL
    msg["Subject"] = subject
    msg.attach(MIMEText("\n".join(body_lines), "plain"))

    try:
        context = ssl.create_default_context()
        with smtplib.SMTP(SMTP_HOST, SMTP_PORT, timeout=10) as server:
            server.starttls(context=context)
            server.login(SMTP_USERNAME, SMTP_PASSWORD)
            server.sendmail(SMTP_FROM, [NOTIFY_EMAIL], msg.as_string())
    except Exception as exc:  # noqa: BLE001 - never let email break the request
        app.logger.warning("Failed to send notification email '%s': %s", subject, exc)

# ---------------------------------------------------------------------
# Static content used across the site (kept here so every page/template
# can render the same service list without repeating it by hand).
# ---------------------------------------------------------------------

SERVICES = [
    {
        "slug": "entrepreneurship-education",
        "category": "Entrepreneurship & Leadership",
        "icon": "fa-lightbulb",
        "title": "Entrepreneurship Education",
        "summary": "Practical training in business development and startup skills for students turning ideas into ventures.",
    },
    {
        "slug": "leadership-development",
        "category": "Entrepreneurship & Leadership",
        "icon": "fa-people-arrows",
        "title": "Leadership Development",
        "summary": "Hands-on leadership training that prepares students to lead teams, projects, and communities.",
    },
    {
        "slug": "innovation-problem-solving",
        "category": "Entrepreneurship & Leadership",
        "icon": "fa-diagram-project",
        "title": "Innovation & Problem Solving",
        "summary": "Structured innovation sprints that help students tackle real-world challenges with creative solutions.",
    },
    {
        "slug": "business-incubation",
        "category": "Entrepreneurship & Leadership",
        "icon": "fa-seedling",
        "title": "Business Incubation",
        "summary": "Guided support for early-stage student businesses, from first idea through to launch.",
    },
    {
        "slug": "networking-mentorship",
        "category": "Entrepreneurship & Leadership",
        "icon": "fa-handshake",
        "title": "Networking & Mentorship",
        "summary": "Connecting students with experienced professionals and entrepreneurs for guidance and growth.",
    },
    {
        "slug": "community-impact-projects",
        "category": "Entrepreneurship & Leadership",
        "icon": "fa-hands-holding-child",
        "title": "Community Impact Projects",
        "summary": "Student-led projects designed to create measurable, positive change in local communities.",
    },
    {
        "slug": "website-design-development",
        "category": "Digital & Creative",
        "icon": "fa-code",
        "title": "Website Design & Development",
        "summary": "Professional, responsive websites built for businesses, schools, and organizations.",
    },
    {
        "slug": "graphic-design",
        "category": "Digital & Creative",
        "icon": "fa-palette",
        "title": "Graphic Design",
        "summary": "Brand identities, print, and digital design work that gives ideas a professional look.",
    },
    {
        "slug": "programming",
        "category": "Digital & Creative",
        "icon": "fa-laptop-code",
        "title": "Programming",
        "summary": "Custom software, tools, and applications built around real business needs.",
    },
    {
        "slug": "ai-tools",
        "category": "Digital & Creative",
        "icon": "fa-robot",
        "title": "Artificial Intelligence Tools",
        "summary": "Practical AI training and implementation to help students and businesses work smarter.",
    },
    {
        "slug": "digital-marketing",
        "category": "Digital & Creative",
        "icon": "fa-bullhorn",
        "title": "Digital Marketing",
        "summary": "Strategy and execution for reaching audiences and growing a brand online.",
    },
    {
        "slug": "social-media-management",
        "category": "Digital & Creative",
        "icon": "fa-hashtag",
        "title": "Social Media Management",
        "summary": "Consistent, on-brand management of an organization's digital presence.",
    },
    {
        "slug": "content-creation",
        "category": "Digital & Creative",
        "icon": "fa-camera-retro",
        "title": "Content Creation",
        "summary": "Photography, videography, and promotional content that tells a brand's story.",
    },
    {
        "slug": "cv-writing",
        "category": "Career Development",
        "icon": "fa-file-lines",
        "title": "CV Writing",
        "summary": "Professionally written CVs that help students stand out to employers.",
    },
    {
        "slug": "career-coaching",
        "category": "Career Development",
        "icon": "fa-compass",
        "title": "Career Coaching",
        "summary": "One-on-one guidance to help students plan and pursue the right career path.",
    },
    {
        "slug": "interview-preparation",
        "category": "Career Development",
        "icon": "fa-comments",
        "title": "Interview Preparation",
        "summary": "Mock interviews and coaching that build confidence for the real thing.",
    },
    {
        "slug": "building-construction",
        "category": "Technical & Engineering",
        "icon": "fa-helmet-safety",
        "title": "Building & Construction",
        "summary": "Construction consulting and hands-on project support from planning to delivery.",
    },
    {
        "slug": "robotics-automation",
        "category": "Technical & Engineering",
        "icon": "fa-microchip",
        "title": "Robotics & Automation",
        "summary": "Robotics education, automation builds, IoT projects, and STEM innovation programs.",
    },
    {
        "slug": "electrical-works",
        "category": "Technical & Engineering",
        "icon": "fa-bolt",
        "title": "Electrical Works",
        "summary": "Electrical installation, maintenance, and consultancy carried out to a professional standard.",
    },
    {
        "slug": "mechanical-services",
        "category": "Technical & Engineering",
        "icon": "fa-gears",
        "title": "Mechanical Services",
        "summary": "Mechanical engineering support and technical services for student and client projects.",
    },
    {
        "slug": "fashion-designing",
        "category": "Technical & Engineering",
        "icon": "fa-scissors",
        "title": "Fashion Designing",
        "summary": "Creative fashion design and tailoring services with an eye for quality finishing.",
    },
]

SERVICE_TITLES = [s["title"] for s in SERVICES]

CORE_VALUES = [
    ("Innovation", "fa-lightbulb"),
    ("Leadership", "fa-people-group"),
    ("Integrity", "fa-shield-halved"),
    ("Excellence", "fa-medal"),
    ("Collaboration", "fa-handshake"),
    ("Creativity", "fa-wand-magic-sparkles"),
    ("Community Impact", "fa-earth-africa"),
    ("Professionalism", "fa-briefcase"),
]

WHY_CHOOSE_US = [
    "Student-centered approach",
    "Experienced mentors",
    "Practical, hands-on learning",
    "Industry-focused training",
    "Professional service delivery",
    "Innovative solutions",
    "Strong community impact",
    "Commitment to excellence",
]

PROJECTS = [
    {
        "title": "Campus Startup Bootcamp",
        "category": "Entrepreneurship Programs",
        "year": 2025,
        "description": "A 6-week bootcamp guiding 40 students from business idea to a pitch-ready venture.",
    },
    {
        "title": "Young Innovators Robotics Club",
        "category": "Robotics Projects",
        "year": 2025,
        "description": "Weekly robotics and IoT sessions culminating in a student-built automated irrigation system.",
    },
    {
        "title": "Cape Coast Community Library Renovation",
        "category": "Construction Projects",
        "year": 2024,
        "description": "Consulting and project support for the renovation of a community reading space.",
    },
    {
        "title": "SME Websites Drive",
        "category": "Website Development",
        "year": 2025,
        "description": "Delivered responsive websites for five local small businesses in a single semester.",
    },
    {
        "title": "Leadership in Practice Fellowship",
        "category": "Student Projects",
        "year": 2024,
        "description": "A cohort program pairing students with mentors for a term-long leadership project.",
    },
    {
        "title": "Clean Water Access Outreach",
        "category": "Community Outreach",
        "year": 2024,
        "description": "A student-led outreach project improving access to clean water in a nearby community.",
    },
]

BLOG_POSTS = [
    {
        "title": "Five Habits of Student Entrepreneurs Who Actually Launch",
        "author": "Scholars HUB Team",
        "date": "June 2026",
        "category": "Entrepreneurship",
        "excerpt": "Most student business ideas never leave the notebook. Here is what separates the ones that do.",
    },
    {
        "title": "Why Leadership Is a Skill You Practice, Not a Title You Wait For",
        "author": "Scholars HUB Team",
        "date": "May 2026",
        "category": "Leadership",
        "excerpt": "You don't need a position to start leading. A look at how our fellows build leadership habits early.",
    },
    {
        "title": "Turning a Class Project Into a Real Product",
        "author": "Scholars HUB Team",
        "date": "April 2026",
        "category": "Innovation",
        "excerpt": "How one student team took a semester assignment and shipped it as a working tool.",
    },
    {
        "title": "What Employers in Ghana Actually Look for on a CV",
        "author": "Scholars HUB Team",
        "date": "March 2026",
        "category": "Career Development",
        "excerpt": "Notes from our career coaching sessions on the details that get CVs shortlisted.",
    },
]

GALLERY_ITEMS = [
    {"title": "Entrepreneurship Workshop", "category": "Workshops", "icon": "fa-chalkboard-user"},
    {"title": "Leadership Training Session", "category": "Training Sessions", "icon": "fa-people-arrows"},
    {"title": "Team Strategy Day", "category": "Team Activities", "icon": "fa-people-group"},
    {"title": "Community Clean-Up Drive", "category": "Community Projects", "icon": "fa-hands-holding-child"},
    {"title": "Startup Pitch Night", "category": "Student Events", "icon": "fa-microphone"},
    {"title": "Robotics Build Session", "category": "Engineering Projects", "icon": "fa-robot"},
    {"title": "CV & Interview Clinic", "category": "Workshops", "icon": "fa-file-lines"},
    {"title": "Digital Skills Bootcamp", "category": "Training Sessions", "icon": "fa-laptop-code"},
    {"title": "Mentor Meet-and-Greet", "category": "Team Activities", "icon": "fa-handshake"},
    {"title": "School Outreach Program", "category": "Community Projects", "icon": "fa-earth-africa"},
    {"title": "Graduation & Awards Night", "category": "Student Events", "icon": "fa-award"},
    {"title": "Construction Site Visit", "category": "Engineering Projects", "icon": "fa-helmet-safety"},
]

TESTIMONIALS = [
    {
        "quote": "Scholars HUB gave me the confidence and the practical skills to actually start my business, not just plan one.",
        "name": "A. Mensah",
        "role": "Entrepreneurship Program Alumna",
    },
    {
        "quote": "The mentorship I received completely changed how I think about leadership. It wasn't theory - it was practice.",
        "name": "K. Owusu",
        "role": "Student, Leadership Cohort",
    },
    {
        "quote": "Our organization worked with Scholars HUB on a website project and the professionalism was outstanding.",
        "name": "Partner Organization",
        "role": "Cape Coast",
    },
]


PROJECT_CATEGORY_ICONS = {
    "Entrepreneurship Programs": "fa-lightbulb",
    "Student Projects": "fa-user-graduate",
    "Engineering Projects": "fa-gears",
    "Robotics Projects": "fa-robot",
    "Construction Projects": "fa-helmet-safety",
    "Website Development": "fa-code",
    "Community Outreach": "fa-hands-holding-child",
}


def now_iso():
    return datetime.now(timezone.utc).isoformat()


# ---------------------------------------------------------------------
# Page routes
# ---------------------------------------------------------------------

@app.route("/")
def home():
    return render_template(
        "index.html",
        active="home",
        core_values=CORE_VALUES,
        why_us=WHY_CHOOSE_US,
        services=SERVICES[:6],
        testimonials=TESTIMONIALS,
    )


@app.route("/about")
def about():
    return render_template(
        "about.html",
        active="about",
        core_values=CORE_VALUES,
        why_us=WHY_CHOOSE_US,
    )


@app.route("/services")
def services():
    categories = []
    for s in SERVICES:
        if s["category"] not in categories:
            categories.append(s["category"])
    grouped = {c: [s for s in SERVICES if s["category"] == c] for c in categories}
    return render_template(
        "services.html", active="services", grouped_services=grouped
    )


@app.route("/projects")
def projects():
    categories = sorted({p["category"] for p in PROJECTS})
    return render_template(
        "projects.html",
        active="projects",
        projects=PROJECTS,
        project_categories=categories,
        project_icons=PROJECT_CATEGORY_ICONS,
    )


@app.route("/gallery")
def gallery():
    categories = sorted({g["category"] for g in GALLERY_ITEMS})
    return render_template(
        "gallery.html", active="gallery", gallery_items=GALLERY_ITEMS, gallery_categories=categories
    )


@app.route("/blog")
def blog():
    return render_template("blog.html", active="blog", posts=BLOG_POSTS)


@app.route("/contact")
def contact():
    return render_template(
        "contact.html", active="contact", service_titles=SERVICE_TITLES
    )


@app.route("/book-service")
def book_service():
    return render_template(
        "book-service.html", active="book", service_titles=SERVICE_TITLES
    )


# ---------------------------------------------------------------------
# JSON APIs -> Firestore
# ---------------------------------------------------------------------

@app.route("/api/contact", methods=["POST"])
def api_contact():
    data = request.get_json(silent=True) or request.form

    required = ["full_name", "email", "phone", "subject", "message"]
    missing = [f for f in required if not str(data.get(f, "")).strip()]
    if missing:
        return jsonify(
            {"success": False, "error": f"Missing required field(s): {', '.join(missing)}"}
        ), 400

    doc = {
        "full_name": data.get("full_name", "").strip(),
        "email": data.get("email", "").strip(),
        "phone": data.get("phone", "").strip(),
        "subject": data.get("subject", "").strip(),
        "message": data.get("message", "").strip(),
        "submitted_at": now_iso(),
        "status": "new",
    }

    try:
        db.collection("contact_messages").add(doc)
    except Exception as exc:  # noqa: BLE001 - surface a clean error to the client
        return jsonify({"success": False, "error": f"Could not save message: {exc}"}), 500

    send_notification_email(
        subject=f"New contact message - {doc['full_name']}",
        body_lines=[
            "You have a new message from the Scholars HUB contact form.",
            "",
            f"Name: {doc['full_name']}",
            f"Email: {doc['email']}",
            f"Phone: {doc['phone']}",
            f"Subject: {doc['subject']}",
            "",
            "Message:",
            doc["message"],
            "",
            f"Submitted: {doc['submitted_at']}",
        ],
    )

    return jsonify({"success": True, "message": "Thank you - your message has been received. We'll be in touch soon."})


@app.route("/api/book-service", methods=["POST"])
def api_book_service():
    data = request.get_json(silent=True) or request.form

    required = ["full_name", "email", "phone", "service_required", "preferred_date"]
    missing = [f for f in required if not str(data.get(f, "")).strip()]
    if missing:
        return jsonify(
            {"success": False, "error": f"Missing required field(s): {', '.join(missing)}"}
        ), 400

    doc = {
        "full_name": data.get("full_name", "").strip(),
        "email": data.get("email", "").strip(),
        "phone": data.get("phone", "").strip(),
        "service_required": data.get("service_required", "").strip(),
        "preferred_date": data.get("preferred_date", "").strip(),
        "additional_info": data.get("additional_info", "").strip(),
        "submitted_at": now_iso(),
        "status": "pending",
    }

    try:
        db.collection("service_bookings").add(doc)
    except Exception as exc:  # noqa: BLE001
        return jsonify({"success": False, "error": f"Could not save booking: {exc}"}), 500

    send_notification_email(
        subject=f"New service booking - {doc['service_required']} ({doc['full_name']})",
        body_lines=[
            "You have a new service booking from the Scholars HUB website.",
            "",
            f"Name: {doc['full_name']}",
            f"Email: {doc['email']}",
            f"Phone: {doc['phone']}",
            f"Service requested: {doc['service_required']}",
            f"Preferred date: {doc['preferred_date']}",
            f"Additional info: {doc['additional_info'] or '-'}",
            "",
            f"Submitted: {doc['submitted_at']}",
        ],
    )

    return jsonify(
        {"success": True, "message": "Your service request has been received. Our team will confirm shortly."}
    )


if __name__ == "__main__":
    app.run(debug=True)
