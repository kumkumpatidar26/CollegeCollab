// ===============================
// Login
// ===============================

const loginForm = document.getElementById("loginForm");

loginForm.addEventListener("submit", async function (e) {

    e.preventDefault();

    const loginAlert = document.getElementById("loginAlert");
    if (loginAlert) loginAlert.classList.add("hidden");

    const username = document.getElementById("collegeId").value;
    const password = document.getElementById("password").value;

    try {

        const response = await fetch("/api/token/", {

            method: "POST",

            headers: {
                "Content-Type": "application/json"
            },

            body: JSON.stringify({
                username: username,
                password: password
            })

        });

        const data = await response.json();

        if (!response.ok) {

            if (loginAlert) {
                showAuthAlert(loginAlert, data.detail || "Invalid username or password.", "danger");
            } else {
                alert("Invalid username or password.");
            }
            return;

        }

        // JWT tokens save karna
        localStorage.setItem("access_token", data.access);
        localStorage.setItem("refresh_token", data.refresh);

        // Login page hide
        document.getElementById("loginPage")
            .classList.add("hidden");

        // Dashboard show
        document.getElementById("dashboard")
            .classList.remove("hidden");

        // Username temporarily display
        document.getElementById("userName").textContent = username;

        // Profile API se actual information
        await loadProfile();

        // Events load karna
        loadEvents();

        // Dashboard statistics
        loadDashboardStats();

        // Colleges
        loadColleges();

        // My registrations
        loadMyRegistrations();

    } catch (error) {

        console.error(error);

        alert("Something went wrong. Please try again.");

    }

});


// ===============================
// ===============================
// Signup & Authentication Toggle
// ===============================

const showSignupLink = document.getElementById("showSignupLink");
const showLoginLink = document.getElementById("showLoginLink");
const loginCard = document.getElementById("loginCard");
const signupCard = document.getElementById("signupCard");
const signupForm = document.getElementById("signupForm");
const signupRoleInput = document.getElementById("signupRole");
const btnRoleStudent = document.getElementById("btnRoleStudent");
const btnRoleOrganizer = document.getElementById("btnRoleOrganizer");
const studentFields = document.getElementById("studentFields");
const organizerFields = document.getElementById("organizerFields");
const signupAlert = document.getElementById("signupAlert");
const loginAlert = document.getElementById("loginAlert");

function showAuthAlert(element, message, type = "danger") {
    if (!element) return;
    element.className = `auth-alert auth-alert-${type}`;
    element.innerHTML = message;
    element.classList.remove("hidden");
}

function setSignupRole(role) {
    if (signupRoleInput) {
        signupRoleInput.value = role;
    }

    if (role === "student") {
        if (btnRoleStudent) btnRoleStudent.classList.add("active");
        if (btnRoleOrganizer) btnRoleOrganizer.classList.remove("active");
        if (studentFields) studentFields.classList.remove("hidden");
        if (organizerFields) organizerFields.classList.add("hidden");
    } else {
        if (btnRoleOrganizer) btnRoleOrganizer.classList.add("active");
        if (btnRoleStudent) btnRoleStudent.classList.remove("active");
        if (studentFields) studentFields.classList.add("hidden");
        if (organizerFields) organizerFields.classList.remove("hidden");
    }
}

if (btnRoleStudent) {
    btnRoleStudent.addEventListener("click", () => setSignupRole("student"));
}

if (btnRoleOrganizer) {
    btnRoleOrganizer.addEventListener("click", () => setSignupRole("organizer"));
}

if (showSignupLink) {
    showSignupLink.addEventListener("click", function (e) {
        e.preventDefault();
        if (loginCard) loginCard.classList.add("hidden");
        if (signupCard) signupCard.classList.remove("hidden");
        if (signupAlert) signupAlert.classList.add("hidden");
        loadSignupColleges();
    });
}

if (showLoginLink) {
    showLoginLink.addEventListener("click", function (e) {
        e.preventDefault();
        if (signupCard) signupCard.classList.add("hidden");
        if (loginCard) loginCard.classList.remove("hidden");
        if (loginAlert) loginAlert.classList.add("hidden");
    });
}

let signupCollegesLoaded = false;
async function loadSignupColleges() {
    if (signupCollegesLoaded) return;
    const select = document.getElementById("signupCollege");
    if (!select) return;

    try {
        const response = await fetch("/api/colleges/");
        if (!response.ok) throw new Error("Failed to load colleges");
        const colleges = await response.json();

        select.innerHTML = '<option value="" disabled selected>Select your college</option>';

        if (colleges.length === 0) {
            select.innerHTML = '<option value="" disabled selected>No colleges available</option>';
            return;
        }

        colleges.forEach(col => {
            const opt = document.createElement("option");
            opt.value = col.id;
            opt.textContent = `${col.name} (${col.code || col.city})`;
            select.appendChild(opt);
        });

        signupCollegesLoaded = true;
    } catch (err) {
        console.error("Error loading colleges for signup:", err);
        select.innerHTML = '<option value="" disabled selected>Could not load colleges</option>';
    }
}

if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", loadSignupColleges);
} else {
    loadSignupColleges();
}

function formatApiErrors(data) {
    if (!data) return "Registration failed. Please check your inputs.";
    if (typeof data === "string") return data;
    if (data.detail) return data.detail;
    if (data.non_field_errors && Array.isArray(data.non_field_errors)) {
        return data.non_field_errors.join("<br>");
    }

    const messages = [];
    for (const [field, errors] of Object.entries(data)) {
        const fieldName = field.charAt(0).toUpperCase() + field.slice(1).replace(/_/g, " ");
        if (Array.isArray(errors)) {
            messages.push(`<strong>${fieldName}:</strong> ${errors.join(", ")}`);
        } else if (typeof errors === "object") {
            messages.push(`<strong>${fieldName}:</strong> ${JSON.stringify(errors)}`);
        } else {
            messages.push(`<strong>${fieldName}:</strong> ${errors}`);
        }
    }
    return messages.length > 0 ? messages.join("<br>") : "Registration failed.";
}

if (signupForm) {
    signupForm.addEventListener("submit", async function (e) {
        e.preventDefault();
        if (signupAlert) signupAlert.classList.add("hidden");

        const role = signupRoleInput ? signupRoleInput.value : "student";
        const username = document.getElementById("signupUsername").value.trim();
        const email = document.getElementById("signupEmail").value.trim();
        const password = document.getElementById("signupPassword").value;
        const collegeSelect = document.getElementById("signupCollege");
        const collegeValue = collegeSelect ? collegeSelect.value : "";

        // Client validation
        if (!username) {
            showAuthAlert(signupAlert, "Username is required.");
            return;
        }

        if (!email) {
            showAuthAlert(signupAlert, "Email address is required.");
            return;
        }

        const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        if (!emailRegex.test(email)) {
            showAuthAlert(signupAlert, "Please enter a valid email address.");
            return;
        }

        if (!password) {
            showAuthAlert(signupAlert, "Password is required.");
            return;
        }

        if (password.length < 8) {
            showAuthAlert(signupAlert, "Password must be at least 8 characters long.");
            return;
        }

        if (!collegeValue) {
            showAuthAlert(signupAlert, "Please select your college.");
            return;
        }

        const payload = {
            username: username,
            email: email,
            password: password,
            role: role,
            college: parseInt(collegeValue, 10)
        };

        if (role === "student") {
            const mobile = document.getElementById("signupMobile").value.trim();
            const course = document.getElementById("signupCourse").value.trim();
            const yearStr = document.getElementById("signupYear").value.trim();

            if (!mobile) {
                showAuthAlert(signupAlert, "Please enter your mobile number.");
                return;
            }

            if (!course) {
                showAuthAlert(signupAlert, "Please enter your course / branch.");
                return;
            }

            if (!yearStr) {
                showAuthAlert(signupAlert, "Please enter your academic year.");
                return;
            }

            const yearNum = parseInt(yearStr, 10);
            if (isNaN(yearNum) || yearNum < 1 || yearNum > 8) {
                showAuthAlert(signupAlert, "Please enter a valid academic year (1-8).");
                return;
            }

            payload.mobile = mobile;
            payload.course = course;
            payload.year = yearNum;
        } else if (role === "organizer") {
            const designation = document.getElementById("signupDesignation").value.trim();
            if (!designation) {
                showAuthAlert(signupAlert, "Please enter your designation.");
                return;
            }
            payload.designation = designation;
        }

        const submitBtn = document.getElementById("signupSubmitBtn");
        if (submitBtn) {
            submitBtn.disabled = true;
            submitBtn.textContent = "Registering...";
        }

        try {
            const response = await fetch("/api/accounts/register/", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json"
                },
                body: JSON.stringify(payload)
            });

            const data = await response.json();

            if (!response.ok) {
                showAuthAlert(signupAlert, formatApiErrors(data), "danger");
                if (submitBtn) {
                    submitBtn.disabled = false;
                    submitBtn.textContent = "Register Account →";
                }
                return;
            }

            // Success
            signupForm.reset();
            setSignupRole("student");

            if (submitBtn) {
                submitBtn.disabled = false;
                submitBtn.textContent = "Register Account →";
            }

            // Switch to Login view with success message
            if (signupCard) signupCard.classList.add("hidden");
            if (loginCard) loginCard.classList.remove("hidden");

            const collegeIdInput = document.getElementById("collegeId");
            if (collegeIdInput) {
                collegeIdInput.value = username;
            }

            const passwordInput = document.getElementById("password");
            if (passwordInput) {
                passwordInput.value = "";
                passwordInput.focus();
            }

            showAuthAlert(loginAlert, "🎉 Account created successfully! Please enter your password to log in.", "success");

        } catch (error) {
            console.error("Signup network error:", error);
            showAuthAlert(signupAlert, "Network error occurred. Please try again.", "danger");
            if (submitBtn) {
                submitBtn.disabled = false;
                submitBtn.textContent = "Register Account →";
            }
        }
    });
}


// ===============================
// Load Profile
// ===============================

async function loadProfile() {

    const token = localStorage.getItem("access_token");

    if (!token) {
        return;
    }

    try {

        const response = await fetch(
            "/api/accounts/profile/",
            {
                headers: {
                    "Authorization": `Bearer ${token}`
                }
            }
        );

        const profile = await response.json();

        // Actual username
        document.getElementById("userName").textContent =
            profile.username;

        // Actual college
        document.getElementById("profileCollege").textContent =
            profile.college || "Not Available";

        // Actual role
        document.getElementById("profileRole").textContent =
            profile.role || "Not Available";

        // Save user information
        localStorage.setItem(
            "user_role",
            profile.role
        );

        localStorage.setItem(
            "user_id",
            profile.id
        );

        localStorage.setItem(
            "college_id",
            profile.college_id
        );

        // Show create event for organizer
        if (profile.role === "organizer") {

            document.getElementById("createEvent")
                .classList.remove("hidden");

        }

    } catch (error) {

        console.error(
            "Error loading profile:",
            error
        );

    }

}


// ===============================
// Load Events from Django API
// ===============================

async function loadEvents() {

    try {

        const response = await fetch("/api/events/");
        const events = await response.json();

        const eventContainer = document.getElementById("eventContainer");
        if (!eventContainer) return;
        eventContainer.innerHTML = "";

        if (!Array.isArray(events) || events.length === 0) {
            eventContainer.innerHTML = `
                <div class="events-empty-state">
                    <i class="bi bi-calendar-x"></i>
                    <h4>No Events Found</h4>
                    <p>There are no campus events scheduled at this moment.</p>
                </div>
            `;
            return;
        }

        const token = localStorage.getItem("access_token");
        const role = localStorage.getItem("user_role");
        const currentUserId = Number(localStorage.getItem("user_id"));

        // If student, preload their registrations in one request
        let myRegistrations = [];
        if (role === "student" && token) {
            try {
                const regRes = await fetch("/api/registrations/my/", {
                    headers: { "Authorization": `Bearer ${token}` }
                });
                if (regRes.ok) {
                    myRegistrations = await regRes.json();
                }
            } catch (err) {
                console.error("Error prefetching my registrations:", err);
            }
        }

        for (const event of events) {
            let registrationText = `Capacity: <strong>${event.capacity}</strong> Seats`;
            let actionButton = "";

            // Organizer actions
            if (role === "organizer") {
                try {
                    const registrationResponse = await fetch(
                        `/api/registrations/event/${event.id}/`,
                        {
                            headers: {
                                "Authorization": `Bearer ${token}`
                            }
                        }
                    );

                    if (registrationResponse.ok) {
                        const registrationData = await registrationResponse.json();
                        registrationText = `Registered: <strong>${registrationData.registered_count}</strong> / ${event.capacity}`;
                    }
                } catch (error) {
                    console.error("Error loading registration count:", error);
                }

                if (event.organizer == currentUserId) {
                    actionButton = `
                        <div class="event-actions">
                            <button class="btn-event-action btn-event-edit" onclick="editEvent(${event.id})">
                                <i class="bi bi-pencil-square"></i> Edit
                            </button>
                            <button class="btn-event-action btn-event-delete" onclick="deleteEvent(${event.id})">
                                <i class="bi bi-trash3"></i> Delete
                            </button>
                        </div>
                    `;
                } else {
                    actionButton = `
                        <div class="event-actions">
                            <span class="badge-role-other">
                                <i class="bi bi-shield-check"></i> Organized by Colleague
                            </span>
                        </div>
                    `;
                }
            }
            // Student actions
            else if (role === "student") {
                const myRegistration = myRegistrations.find(
                    reg => reg.event === event.id
                );

                if (myRegistration) {
                    actionButton = `
                        <div class="event-actions">
                            <button class="btn-event-action btn-event-cancel" onclick="cancelRegistration(${myRegistration.id})">
                                <i class="bi bi-x-circle"></i> Cancel Registration
                            </button>
                        </div>
                    `;
                } else {
                    actionButton = `
                        <div class="event-actions">
                            <button class="btn-event-action btn-event-register" onclick="registerEvent(${event.id})">
                                <i class="bi bi-ticket-perforated-fill"></i> Register Now
                            </button>
                        </div>
                    `;
                }
            }
            // Public / guest
            else {
                actionButton = `
                    <div class="event-actions">
                        <button class="btn-event-action btn-event-register" onclick="registerEvent(${event.id})">
                            <i class="bi bi-ticket-perforated"></i> Register
                        </button>
                    </div>
                `;
            }

            const eventCard = document.createElement("div");
            eventCard.className = "event-card";

            const eventStatus = (event.status || "upcoming").toLowerCase();
            const timeString = (event.start_time && event.end_time)
                ? `${event.date} • ${event.start_time.slice(0, 5)} - ${event.end_time.slice(0, 5)}`
                : `${event.date}`;

            eventCard.innerHTML = `
                <div class="event-card-top">
                    <span class="event-status-badge status-${eventStatus}">
                        ${eventStatus}
                    </span>
                    <span class="event-college-pill" title="${event.college_name || 'College'}">
                        <i class="bi bi-building"></i> ${event.college_name || 'College'}
                    </span>
                </div>

                <div class="event-card-body">
                    <h3 class="event-card-title">${event.title}</h3>
                    <p class="event-card-desc">${event.description}</p>

                    <div class="event-meta-grid">
                        <div class="event-meta-item">
                            <i class="bi bi-calendar3"></i>
                            <div>
                                <span class="meta-label">Date & Time</span>
                                <span class="meta-value">${timeString}</span>
                            </div>
                        </div>
                        <div class="event-meta-item">
                            <i class="bi bi-geo-alt-fill"></i>
                            <div>
                                <span class="meta-label">Venue</span>
                                <span class="meta-value">${event.venue}</span>
                            </div>
                        </div>
                        <div class="event-meta-item">
                            <i class="bi bi-people-fill"></i>
                            <div>
                                <span class="meta-label">Participation</span>
                                <span class="meta-value">${registrationText}</span>
                            </div>
                        </div>
                    </div>
                </div>

                <div class="event-card-footer">
                    ${actionButton}
                </div>
            `;

            eventContainer.appendChild(eventCard);
        }

    } catch (error) {
        console.error("Error loading events:", error);
    }

}


// ===============================
// Load Dashboard Statistics
// ===============================

async function loadDashboardStats() {

    try {

        // Events API
        const eventResponse =
            await fetch("/api/events/");

        const events =
            await eventResponse.json();

        // Colleges API
        const collegeResponse =
            await fetch("/api/colleges/");

        const colleges =
            await collegeResponse.json();

        // Total events
        document.getElementById("eventCount").textContent =
            events.length;

        // Total colleges
        document.getElementById("collegeCount").textContent =
            colleges.length;

        // Active / upcoming events
        const activeEvents =
            events.filter(
                event =>
                    event.status === "upcoming" ||
                    event.status === "ongoing"
            );

        document.getElementById("activeEventCount")
            .textContent =
            activeEvents.length;

    } catch (error) {

        console.error(
            "Error loading dashboard statistics:",
            error
        );

    }

}


// ===============================
// Load My Registrations
// ===============================

async function loadMyRegistrations() {

    const token =
        localStorage.getItem("access_token");
    const role =
        localStorage.getItem("user_role");

    if (!token) {
        return;
    }

    try {

        const isOrganizer = role === "organizer";
        const response =
            await fetch(
                isOrganizer
                    ? "/api/notifications/"
                    : "/api/registrations/my/",
                {
                    headers: {
                        "Authorization":
                            `Bearer ${token}`
                    }
                }
            );

        if (!response.ok) {
            throw new Error(`Failed to load notifications (${response.status}).`);
        }

        const registrations =
            await response.json();

        const notificationContainer =
            document.getElementById(
                "notificationContainer"
            );

        notificationContainer.innerHTML = "";

        if (registrations.length === 0) {

            notificationContainer.innerHTML = `
                <div class="notification">

                    <div>📧</div>

                    <div>

                        <strong>
                            ${isOrganizer ? "No Event Registrations Yet" : "No Registrations Yet"}
                        </strong>

                        <p>
                            ${isOrganizer
                                ? "No students have registered for your events yet."
                                : "You have not registered for any event yet."}
                        </p>

                        <small>
                            CollegeCollab
                        </small>

                    </div>

                </div>
            `;

            return;

        }

        const escapeHtml = value => String(value ?? "").replace(/[&<>"']/g, character => ({
            "&": "&amp;",
            "<": "&lt;",
            ">": "&gt;",
            '"': "&quot;",
            "'": "&#39;"
        })[character]);

        registrations.forEach(
            registration => {

                const notification =
                    document.createElement("div");

                notification.className =
                    "notification";

                notification.innerHTML = `
                    <div>📧</div>

                    <div>

                        <strong>
                            ${isOrganizer ? "New Event Registration" : "Registration Confirmed"}
                        </strong>

                        <p>
                            ${isOrganizer
                                ? `<strong>${escapeHtml(registration.student_name)}</strong> registered for <strong>${escapeHtml(registration.event_title)}</strong>.`
                                : `You are registered for <strong>${escapeHtml(registration.event_title)}</strong>.`}
                        </p>

                        <small>
                            ${isOrganizer
                                ? new Date(registration.registered_at).toLocaleString()
                                : `${escapeHtml(registration.event_college)} • ${escapeHtml(registration.event_date)} • ${escapeHtml(registration.event_venue)}`}
                        </small>

                    </div>
                `;

                notificationContainer
                    .appendChild(notification);

            }
        );

    } catch (error) {

        console.error(
            "Error loading notifications:",
            error
        );

    }

}


// ===============================
// Register for Event
// ===============================

async function registerEvent(eventId) {

    const token =
        localStorage.getItem("access_token");

    if (!token) {

        alert("Please login first.");

        return;

    }

    try {

        const response =
            await fetch(
                "/api/registrations/",
                {
                    method: "POST",

                    headers: {
                        "Content-Type":
                            "application/json",

                        "Authorization":
                            `Bearer ${token}`
                    },

                    body: JSON.stringify({
                        event: eventId
                    })
                }
            );

        const data =
            await response.json();

        if (!response.ok) {

            alert(
                data.detail ||
                data.non_field_errors?.[0] ||
                "Registration failed."
            );

            return;

        }

        alert(
            "Event registered successfully!"
        );

        // Notification refresh
        loadMyRegistrations();

        // Events refresh
        loadEvents();

    } catch (error) {

        console.error(error);

        alert(
            "Something went wrong."
        );

    }

}


// ===============================
// Cancel Registration
// ===============================

async function cancelRegistration(
    registrationId
) {

    const token =
        localStorage.getItem("access_token");

    if (!token) {

        alert("Please login first.");

        return;

    }

    try {

        const response =
            await fetch(
                `/api/registrations/${registrationId}/cancel/`,
                {
                    method: "DELETE",

                    headers: {
                        "Authorization":
                            `Bearer ${token}`
                    }
                }
            );

        if (!response.ok) {

            alert(
                "Registration could not be cancelled."
            );

            return;

        }

        alert(
            "Registration cancelled successfully! ✅"
        );

        loadEvents();

        loadMyRegistrations();

    } catch (error) {

        console.error(error);

        alert(
            "Something went wrong."
        );

    }

}


// ===============================
// Create Event - Organizer
// ===============================

const createEventForm =
    document.getElementById(
        "createEventForm"
    );

if (createEventForm) {

    createEventForm.addEventListener(
        "submit",
        async function (e) {

            e.preventDefault();

            const token =
                localStorage.getItem(
                    "access_token"
                );

            const role =
                localStorage.getItem(
                    "user_role"
                );

            // Only organizer
            if (role !== "organizer") {

                alert(
                    "Only organizers can create events."
                );

                return;

            }

            try {

                const collegeId =
                    Number(
                        localStorage.getItem(
                            "college_id"
                        )
                    );

                const response =
                    await fetch(
                        "/api/events/",
                        {
                            method: "POST",

                            headers: {
                                "Content-Type":
                                    "application/json",

                                "Authorization":
                                    `Bearer ${token}`
                            },

                            body: JSON.stringify({

                                title:
                                    document.getElementById(
                                        "eventTitle"
                                    ).value,

                                description:
                                    document.getElementById(
                                        "eventDescription"
                                    ).value,

                                college:
                                    collegeId,

                                venue:
                                    document.getElementById(
                                        "eventVenue"
                                    ).value,

                                date:
                                    document.getElementById(
                                        "eventDate"
                                    ).value,

                                start_time:
                                    document.getElementById(
                                        "eventStartTime"
                                    ).value,

                                end_time:
                                    document.getElementById(
                                        "eventEndTime"
                                    ).value,

                                capacity:
                                    Number(
                                        document.getElementById(
                                            "eventCapacity"
                                        ).value
                                    ),

                                status:
                                    "upcoming"

                            })

                        }
                    );

                const data =
                    await response.json();

                if (!response.ok) {

                    console.error(data);

                    alert(
                        data.detail ||
                        data.non_field_errors?.[0] ||
                        "Event creation failed."
                    );

                    return;

                }

                alert(
                    "Event created successfully! 🎉"
                );

                // Form clear
                createEventForm.reset();

                // Events refresh
                loadEvents();

                // Dashboard statistics
                loadDashboardStats();

            } catch (error) {

                console.error(
                    "Error creating event:",
                    error
                );

                alert(
                    "Something went wrong."
                );

            }

        }
    );

}


// ===============================
// Delete Event
// ===============================

async function deleteEvent(eventId) {

    const token =
        localStorage.getItem(
            "access_token"
        );

    const confirmDelete =
        confirm(
            "Are you sure you want to delete this event?"
        );

    if (!confirmDelete) {
        return;
    }

    try {

        const response =
            await fetch(
                `/api/events/${eventId}/`,
                {
                    method: "DELETE",

                    headers: {
                        "Authorization":
                            `Bearer ${token}`
                    }
                }
            );

        if (!response.ok) {

            const data =
                await response.json();

            alert(
                data.detail ||
                "Event could not be deleted."
            );

            return;

        }

        alert(
            "Event deleted successfully! 🗑️"
        );

        // Events refresh
        loadEvents();

        // Statistics refresh
        loadDashboardStats();

    } catch (error) {

        console.error(
            "Error deleting event:",
            error
        );

        alert(
            "Something went wrong."
        );

    }

}


// ===============================
// Edit Event
// ===============================

async function editEvent(eventId) {

    const token =
        localStorage.getItem(
            "access_token"
        );

    const newTitle =
        prompt(
            "Enter new event title:"
        );

    if (
        newTitle === null ||
        newTitle.trim() === ""
    ) {
        return;
    }

    const newDescription =
        prompt(
            "Enter new description:"
        );

    if (
        newDescription === null ||
        newDescription.trim() === ""
    ) {
        return;
    }

    const newVenue =
        prompt(
            "Enter new venue:"
        );

    if (
        newVenue === null ||
        newVenue.trim() === ""
    ) {
        return;
    }

    const newCapacity =
        prompt(
            "Enter new capacity:"
        );

    if (
        newCapacity === null ||
        newCapacity.trim() === ""
    ) {
        return;
    }

    try {

        const response =
            await fetch(
                `/api/events/${eventId}/`,
                {
                    method: "PATCH",

                    headers: {
                        "Content-Type":
                            "application/json",

                        "Authorization":
                            `Bearer ${token}`
                    },

                    body: JSON.stringify({

                        title:
                            newTitle,

                        description:
                            newDescription,

                        venue:
                            newVenue,

                        capacity:
                            Number(newCapacity)

                    })

                }
            );

        const data =
            await response.json();

        if (!response.ok) {

            alert(
                data.detail ||
                "Event could not be updated."
            );

            return;

        }

        alert(
            "Event updated successfully! ✏️"
        );

        loadEvents();

    } catch (error) {

        console.error(
            "Error updating event:",
            error
        );

        alert(
            "Something went wrong."
        );

    }

}


// ===============================
// Event Search & Filter
// ===============================

const searchInput =
    document.getElementById("search");

const categorySelect =
    document.getElementById("category");

if (searchInput) {

    searchInput.addEventListener(
        "input",
        function () {

            filterEvents();

        }
    );

}

if (categorySelect) {

    categorySelect.addEventListener(
        "change",
        function () {

            filterEvents();

        }
    );

}


function filterEvents() {

    const searchText =
        searchInput.value
            .toLowerCase()
            .trim();

    const selectedCategory =
        categorySelect.value;

    const eventCards =
        document.querySelectorAll(
            ".event-card"
        );

    eventCards.forEach(
        card => {

            const eventText =
                card.textContent
                    .toLowerCase();

            const matchesSearch =
                eventText.includes(
                    searchText
                );

            let matchesCategory = true;

            if (
                selectedCategory !== "All"
            ) {

                matchesCategory =
                    eventText.includes(
                        selectedCategory
                            .toLowerCase()
                    );

            }

            if (
                matchesSearch &&
                matchesCategory
            ) {

                card.style.display = "";

            } else {

                card.style.display = "none";

            }

        }
    );

}


// ===============================
// Load Colleges
// ===============================

async function loadColleges() {

    try {

        const response =
            await fetch(
                "/api/colleges/"
            );

        const colleges =
            await response.json();

        const collegeContainer =
            document.getElementById(
                "collegeContainer"
            );

        if (!collegeContainer) {
            return;
        }

        collegeContainer.innerHTML = "";

        if (colleges.length === 0) {

            collegeContainer.innerHTML = `
                <p>
                    No colleges available.
                </p>
            `;

            return;

        }

        colleges.forEach(
            college => {

                const collegeCard =
                    document.createElement(
                        "div"
                    );

                collegeCard.className =
                    "event-card";

                collegeCard.innerHTML = `
                    <h3>
                        ${college.name}
                    </h3>

                    <p>
                        <strong>Code:</strong>
                        ${college.code}
                    </p>

                    <p>
                        <strong>City:</strong>
                        ${college.city}
                    </p>

                    ${
                        college.email
                        ? `
                            <p>
                                <strong>Email:</strong>
                                ${college.email}
                            </p>
                        `
                        : ""
                    }
                `;

                collegeContainer.appendChild(
                    collegeCard
                );

            }
        );

    } catch (error) {

        console.error(
            "Error loading colleges:",
            error
        );

    }

}


// ===============================
// Logout
// ===============================

const logoutBtn =
    document.getElementById(
        "logoutbtn"
    );

if (logoutBtn) {

    logoutBtn.addEventListener(
        "click",
        function () {

            localStorage.removeItem(
                "access_token"
            );

            localStorage.removeItem(
                "refresh_token"
            );

            localStorage.removeItem(
                "user_role"
            );

            localStorage.removeItem(
                "user_id"
            );

            localStorage.removeItem(
                "college_id"
            );

            document.getElementById(
                "collegeId"
            ).value = "";

            document.getElementById(
                "password"
            ).value = "";

            location.reload();

        }
    );

}