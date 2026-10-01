/* Scholars HUB — firebase-forms.js
 * Saves the Contact and Book-a-Service forms straight to Firestore.
 * No backend needed. Load it on a page with:
 *   <script type="module" src="js/firebase-forms.js"></script>
 */
import { initializeApp } from "https://www.gstatic.com/firebasejs/12.16.0/firebase-app.js";
import { getAnalytics } from "https://www.gstatic.com/firebasejs/12.16.0/firebase-analytics.js";
import {
  getFirestore,
  collection,
  addDoc,
  serverTimestamp,
} from "https://www.gstatic.com/firebasejs/12.16.0/firebase-firestore.js";

const firebaseConfig = {
  apiKey: "AIzaSyA9dFM00Q0vbbzgElJW2iXYfgsq-qI9rn4",
  authDomain: "chatbot-e1297.firebaseapp.com",
  databaseURL: "https://chatbot-e1297-default-rtdb.firebaseio.com",
  projectId: "chatbot-e1297",
  storageBucket: "chatbot-e1297.firebasestorage.app",
  messagingSenderId: "538304203055",
  appId: "1:538304203055:web:c42821beb1460073e6b9da",
  measurementId: "G-LW7X688MGL"
};

const app = initializeApp(firebaseConfig);
const db = getFirestore(app);

// Analytics can be blocked by ad-blockers; it must never break the forms.
try { getAnalytics(app); } catch (err) { console.warn("Analytics unavailable:", err); }

// ---------------------------------------------------------------------
// Form definitions
// ---------------------------------------------------------------------
// maxLen values must match the limits in firestore.rules.
const FORMS = {
  bookingForm: {
    collection: "service_bookings",
    status: "pending",
    fields: {
      full_name:        { label: "Full Name",           required: true,  maxLen: 100 },
      email:            { label: "Email",               required: true,  maxLen: 150 },
      phone:            { label: "Phone Number",        required: true,  maxLen: 30 },
      service_required: { label: "Service Required",    required: true,  maxLen: 100 },
      preferred_date:   { label: "Preferred Date",      required: true,  maxLen: 20 },
      additional_info:  { label: "Additional Information", required: false, maxLen: 1000 },
    },
    success: "Your service request has been received. Our team will confirm shortly.",
  },
  contactForm: {
    collection: "contact_messages",
    status: "new",
    fields: {
      full_name: { label: "Full Name",    required: true, maxLen: 100 },
      email:     { label: "Email",        required: true, maxLen: 150 },
      phone:     { label: "Phone Number", required: true, maxLen: 30 },
      subject:   { label: "Subject",      required: true, maxLen: 150 },
      message:   { label: "Message",      required: true, maxLen: 3000 },
    },
    success: "Thank you - your message has been received. We'll be in touch soon.",
  },
};

const EMAIL_RE = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;

function attachForm(formId, cfg) {
  const form = document.getElementById(formId);
  if (!form) return;

  const statusBox = form.querySelector(".form-status");
  const submitBtn = form.querySelector('button[type="submit"]');

  const showStatus = (ok, text) => {
    if (!statusBox) return;
    statusBox.className = "form-status " + (ok ? "is-success" : "is-error");
    statusBox.textContent = text;
  };

  // Booking form: don't allow dates in the past.
  const dateInput = form.querySelector('input[type="date"]');
  if (dateInput) {
    const t = new Date();
    const pad = (n) => String(n).padStart(2, "0");
    dateInput.min = `${t.getFullYear()}-${pad(t.getMonth() + 1)}-${pad(t.getDate())}`;
  }

  form.addEventListener("submit", async (e) => {
    e.preventDefault();

    // Collect + validate
    const data = {};
    const problems = [];
    for (const [name, rule] of Object.entries(cfg.fields)) {
      const el = form.elements[name];
      const value = el ? String(el.value || "").trim() : "";
      if (rule.required && !value) { problems.push(rule.label); continue; }
      if (value.length > rule.maxLen) {
        showStatus(false, `${rule.label} is too long (max ${rule.maxLen} characters).`);
        return;
      }
      data[name] = value;
    }
    if (problems.length) {
      showStatus(false, "Please fill in: " + problems.join(", ") + ".");
      return;
    }
    if (!EMAIL_RE.test(data.email)) {
      showStatus(false, "Please enter a valid email address.");
      return;
    }

    if (submitBtn) { submitBtn.disabled = true; submitBtn.textContent = "Sending..."; }
    if (statusBox) { statusBox.className = "form-status"; statusBox.textContent = ""; }

    try {
      await addDoc(collection(db, cfg.collection), {
        ...data,
        submitted_at: serverTimestamp(),
        status: cfg.status,
      });
      showStatus(true, cfg.success);
      form.reset();
    } catch (err) {
      console.error("Could not save to Firestore:", err);
      if (err && err.code === "permission-denied") {
        showStatus(false, "We couldn't save your request right now. Please call us on 0598712336.");
      } else {
        showStatus(false, "Network error - please check your connection and try again.");
      }
    } finally {
      if (submitBtn) { submitBtn.disabled = false; submitBtn.textContent = submitBtn.dataset.label || "Submit"; }
    }
  });
}

for (const [formId, cfg] of Object.entries(FORMS)) attachForm(formId, cfg);
