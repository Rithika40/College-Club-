const titles = {
  dashboard: ["Dashboard", "Overview of club activity"],
  clubs: ["Clubs", "Create and manage college clubs"],
  members: ["Members", "Add, search, and update club members"],
  events: ["Events", "Plan events and register members"],
  attendance: ["Attendance", "Mark and review event attendance"],
  announcements: ["Announcements", "Post and view club notices"],
  reports: ["Reports", "Club activity and attendance summaries"],
  profile: ["Account", "Update your profile details"],
};

const modal = document.getElementById("modal");
const modalForm = document.getElementById("modal-form");
const modalTitle = document.getElementById("modal-title");
const modalError = document.getElementById("modal-error");
let cache = { clubs: [], members: [], events: [] };

function toast(msg) {
  const el = document.getElementById("toast");
  el.textContent = msg;
  el.classList.add("show");
  setTimeout(() => el.classList.remove("show"), 2200);
}

function showError(el, msg) {
  el.textContent = msg;
  el.classList.add("show");
}

function escapeHtml(str) {
  return String(str ?? "").replace(/[&<>"']/g, (c) => ({
    "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;"
  }[c]));
}

function requireAuth() {
  if (!CCMS.token() || CCMS.idleExpired()) {
    CCMS.clearSession();
    window.location.replace("/");
    return false;
  }
  return true;
}

function field(label, name, type = "text", value = "", extra = "") {
  if (type === "select") {
    return `<div class="form-group"><label>${label}</label><select name="${name}" ${extra}>${value}</select></div>`;
  }
  if (type === "textarea") {
    return `<div class="form-group"><label>${label}</label><textarea name="${name}" ${extra}>${escapeHtml(value)}</textarea></div>`;
  }
  return `<div class="form-group"><label>${label}</label><input name="${name}" type="${type}" value="${escapeHtml(value)}" ${extra}></div>`;
}

function clubOptions(selected) {
  const blank = `<option value="">No club</option>`;
  return blank + cache.clubs.map((c) =>
    `<option value="${c.id}" ${String(c.id) === String(selected) ? "selected" : ""}>${escapeHtml(c.name)}</option>`
  ).join("");
}

function memberOptions() {
  return `<option value="">Select member</option>` + cache.members.map((m) =>
    `<option value="${m.id}">${escapeHtml(m.name)}</option>`
  ).join("");
}

function eventOptions() {
  return `<option value="">Select event</option>` + cache.events.map((e) =>
    `<option value="${e.id}">${escapeHtml(e.name)}</option>`
  ).join("");
}

function openModal(title, html, onSubmit) {
  modalTitle.textContent = title;
  modalError.classList.remove("show");
  modalForm.innerHTML = html + `<div class="modal-actions">
    <button type="button" class="btn btn-ghost" id="cancel-modal">Cancel</button>
    <button type="submit" class="btn btn-primary">Save</button>
  </div>`;
  modal.classList.remove("hidden");
  document.getElementById("cancel-modal").onclick = closeModal;
  modalForm.onsubmit = async (e) => {
    e.preventDefault();
    modalError.classList.remove("show");
    const data = Object.fromEntries(new FormData(modalForm).entries());
    try {
      await onSubmit(data);
      closeModal();
    } catch (err) {
      showError(modalError, err.message);
    }
  };
}

function closeModal() {
  modal.classList.add("hidden");
}

async function refreshLookups() {
  const [clubs, members, events] = await Promise.all([
    CCMS.api("/clubs"),
    CCMS.api("/members"),
    CCMS.api("/events"),
  ]);
  cache = { clubs, members, events };
}

function go(section) {
  document.querySelectorAll(".nav-btn").forEach((b) => b.classList.toggle("active", b.dataset.section === section));
  document.querySelectorAll(".view").forEach((v) => v.classList.toggle("hidden", v.id !== section));
  const [t, s] = titles[section];
  document.getElementById("page-title").textContent = t;
  document.getElementById("page-sub").textContent = s;
  document.getElementById("sidebar").classList.remove("open");
  loadSection(section);
}

async function loadSection(section) {
  try {
    if (section === "dashboard") await renderDashboard();
    if (section === "clubs") await renderClubs();
    if (section === "members") await renderMembers();
    if (section === "events") await renderEvents();
    if (section === "attendance") await renderAttendance();
    if (section === "announcements") await renderAnnouncements();
    if (section === "reports") await renderReports();
    if (section === "profile") await renderProfile();
  } catch (err) {
    if (err.status === 401) {
      CCMS.clearSession();
      window.location.replace("/");
      return;
    }
    document.getElementById(section).innerHTML = `<div class="card"><p class="empty">${escapeHtml(err.message)}</p></div>`;
  }
}

async function renderDashboard() {
  const data = await CCMS.api("/dashboard");
  const s = data.stats;
  document.getElementById("dashboard").innerHTML = `
    <div class="metrics">
      <div class="metric"><span>Clubs</span><strong>${s.clubs}</strong></div>
      <div class="metric"><span>Members</span><strong>${s.members}</strong></div>
      <div class="metric"><span>Events</span><strong>${s.events}</strong></div>
      <div class="metric"><span>Registrations</span><strong>${s.registrations}</strong></div>
    </div>
    <div class="grid-2">
      <div class="card">
        <h3>Upcoming events</h3>
        ${data.upcoming_events.length ? data.upcoming_events.map((e) => `
          <div class="feed-item">
            <h4>${escapeHtml(e.name)}</h4>
            <p>${escapeHtml(e.description)}</p>
            <div class="meta">${escapeHtml(e.event_date)} · ${escapeHtml(e.club_name || "General")}</div>
          </div>`).join("") : `<p class="empty">No events yet.</p>`}
      </div>
      <div class="card">
        <h3>Latest announcements</h3>
        ${data.recent_announcements.length ? data.recent_announcements.map((a) => `
          <div class="feed-item">
            <h4>${escapeHtml(a.title)}</h4>
            <p>${escapeHtml(a.content)}</p>
            <div class="meta">${escapeHtml(a.author)} · ${escapeHtml((a.created_at || "").slice(0, 10))}</div>
          </div>`).join("") : `<p class="empty">No announcements yet.</p>`}
      </div>
    </div>`;
}

async function renderClubs(q = "") {
  await refreshLookups();
  const rows = q ? await CCMS.api(`/clubs?q=${encodeURIComponent(q)}`) : cache.clubs;
  document.getElementById("clubs").innerHTML = `
    <div class="action-bar">
      <input class="search" id="club-q" placeholder="Search clubs..." value="${escapeHtml(q)}">
      <button class="btn btn-primary" id="add-club">+ New club</button>
    </div>
    <div class="card">
      <table>
        <thead><tr><th>Name</th><th>Description</th><th>Members</th><th>Events</th><th></th></tr></thead>
        <tbody>
          ${rows.length ? rows.map((c) => `<tr>
            <td><strong>${escapeHtml(c.name)}</strong></td>
            <td>${escapeHtml(c.description)}</td>
            <td>${c.member_count}</td>
            <td>${c.event_count}</td>
            <td>
              <button class="btn btn-ghost btn-sm" data-edit="${c.id}">Edit</button>
              <button class="btn btn-danger btn-sm" data-del="${c.id}">Delete</button>
            </td>
          </tr>`).join("") : `<tr><td colspan="5" class="empty">No clubs found.</td></tr>`}
        </tbody>
      </table>
    </div>`;
  document.getElementById("club-q").oninput = (e) => renderClubs(e.target.value);
  document.getElementById("add-club").onclick = () => clubForm();
  document.querySelectorAll("[data-edit]").forEach((btn) => {
    btn.onclick = () => clubForm(cache.clubs.find((c) => String(c.id) === btn.dataset.edit));
  });
  document.querySelectorAll("[data-del]").forEach((btn) => {
    btn.onclick = async () => {
      if (!confirm("Delete this club?")) return;
      await CCMS.api(`/clubs/${btn.dataset.del}`, { method: "DELETE" });
      toast("Club deleted");
      renderClubs(document.getElementById("club-q").value);
    };
  });
}

function clubForm(club) {
  openModal(club ? "Edit club" : "New club",
    field("Club name", "name", "text", club?.name || "", "required minlength='2'") +
    field("Description", "description", "textarea", club?.description || "", "required"),
    async (data) => {
      await CCMS.api(club ? `/clubs/${club.id}` : "/clubs", {
        method: club ? "PUT" : "POST",
        body: JSON.stringify(data),
      });
      toast(club ? "Club updated" : "Club created");
      await renderClubs();
    }
  );
}

async function renderMembers(q = "") {
  await refreshLookups();
  const rows = q ? await CCMS.api(`/members?q=${encodeURIComponent(q)}`) : cache.members;
  document.getElementById("members").innerHTML = `
    <div class="action-bar">
      <input class="search" id="member-q" placeholder="Search by name, email, or role..." value="${escapeHtml(q)}">
      <button class="btn btn-primary" id="add-member">+ Add member</button>
    </div>
    <div class="card">
      <table>
        <thead><tr><th>Name</th><th>Email</th><th>Role</th><th>Club</th><th></th></tr></thead>
        <tbody>
          ${rows.length ? rows.map((m) => `<tr>
            <td><strong>${escapeHtml(m.name)}</strong></td>
            <td>${escapeHtml(m.email)}</td>
            <td><span class="badge">${escapeHtml(m.role)}</span></td>
            <td>${escapeHtml(m.club_name || "—")}</td>
            <td>
              <button class="btn btn-ghost btn-sm" data-edit="${m.id}">Edit</button>
              <button class="btn btn-danger btn-sm" data-del="${m.id}">Delete</button>
            </td>
          </tr>`).join("") : `<tr><td colspan="5" class="empty">No members found.</td></tr>`}
        </tbody>
      </table>
    </div>`;
  document.getElementById("member-q").oninput = (e) => renderMembers(e.target.value);
  document.getElementById("add-member").onclick = () => memberForm();
  document.querySelectorAll("[data-edit]").forEach((btn) => {
    btn.onclick = () => memberForm(cache.members.find((m) => String(m.id) === btn.dataset.edit));
  });
  document.querySelectorAll("[data-del]").forEach((btn) => {
    btn.onclick = async () => {
      if (!confirm("Delete this member?")) return;
      await CCMS.api(`/members/${btn.dataset.del}`, { method: "DELETE" });
      toast("Member deleted");
      renderMembers(document.getElementById("member-q").value);
    };
  });
}

function memberForm(member) {
  openModal(member ? "Edit member" : "Add member",
    field("Full name", "name", "text", member?.name || "", "required minlength='2'") +
    field("Email", "email", "email", member?.email || "", "required") +
    field("Role", "role", "text", member?.role || "Member", "required") +
    field("Club", "club_id", "select", clubOptions(member?.club_id)),
    async (data) => {
      const body = {
        name: data.name,
        email: data.email,
        role: data.role,
        club_id: data.club_id ? Number(data.club_id) : null,
      };
      await CCMS.api(member ? `/members/${member.id}` : "/members", {
        method: member ? "PUT" : "POST",
        body: JSON.stringify(body),
      });
      toast(member ? "Member updated" : "Member added");
      await renderMembers();
    }
  );
}

async function renderEvents(q = "") {
  await refreshLookups();
  const [events, regs] = await Promise.all([
    q ? CCMS.api(`/events?q=${encodeURIComponent(q)}`) : Promise.resolve(cache.events),
    CCMS.api("/registrations"),
  ]);
  document.getElementById("events").innerHTML = `
    <div class="action-bar">
      <input class="search" id="event-q" placeholder="Search events..." value="${escapeHtml(q)}">
      <button class="btn btn-primary" id="add-event">+ New event</button>
      <button class="btn btn-ghost" id="add-reg">Register member</button>
    </div>
    <div class="card">
      <h3>Events</h3>
      <table>
        <thead><tr><th>Event</th><th>Date</th><th>Club</th><th>Registered</th><th></th></tr></thead>
        <tbody>
          ${events.length ? events.map((e) => `<tr>
            <td><strong>${escapeHtml(e.name)}</strong><div class="meta">${escapeHtml(e.description)}</div></td>
            <td>${escapeHtml(e.event_date)}</td>
            <td>${escapeHtml(e.club_name || "—")}</td>
            <td>${e.registration_count}</td>
            <td>
              <button class="btn btn-ghost btn-sm" data-edit="${e.id}">Edit</button>
              <button class="btn btn-danger btn-sm" data-del="${e.id}">Delete</button>
            </td>
          </tr>`).join("") : `<tr><td colspan="5" class="empty">No events found.</td></tr>`}
        </tbody>
      </table>
    </div>
    <div class="card">
      <h3>Event registrations</h3>
      <table>
        <thead><tr><th>Event</th><th>Member</th><th>Registered</th><th></th></tr></thead>
        <tbody>
          ${regs.length ? regs.map((r) => `<tr>
            <td>${escapeHtml(r.event_name)}</td>
            <td>${escapeHtml(r.member_name)}</td>
            <td>${escapeHtml((r.registered_at || "").replace("T", " ").slice(0, 16))}</td>
            <td><button class="btn btn-danger btn-sm" data-unreg="${r.id}">Remove</button></td>
          </tr>`).join("") : `<tr><td colspan="4" class="empty">No registrations yet.</td></tr>`}
        </tbody>
      </table>
    </div>`;
  document.getElementById("event-q").oninput = (e) => renderEvents(e.target.value);
  document.getElementById("add-event").onclick = () => eventForm();
  document.getElementById("add-reg").onclick = () => openModal("Register a member",
    field("Event", "event_id", "select", eventOptions(), "required") +
    field("Member", "member_id", "select", memberOptions(), "required"),
    async (data) => {
      await CCMS.api("/registrations", {
        method: "POST",
        body: JSON.stringify({ event_id: Number(data.event_id), member_id: Number(data.member_id) }),
      });
      toast("Member registered");
      await renderEvents();
    }
  );
  document.querySelectorAll("[data-edit]").forEach((btn) => {
    btn.onclick = () => eventForm(cache.events.find((e) => String(e.id) === btn.dataset.edit));
  });
  document.querySelectorAll("[data-del]").forEach((btn) => {
    btn.onclick = async () => {
      if (!confirm("Delete this event?")) return;
      await CCMS.api(`/events/${btn.dataset.del}`, { method: "DELETE" });
      toast("Event deleted");
      renderEvents(document.getElementById("event-q").value);
    };
  });
  document.querySelectorAll("[data-unreg]").forEach((btn) => {
    btn.onclick = async () => {
      await CCMS.api(`/registrations/${btn.dataset.unreg}`, { method: "DELETE" });
      toast("Registration removed");
      renderEvents(document.getElementById("event-q").value);
    };
  });
}

function eventForm(event) {
  openModal(event ? "Edit event" : "New event",
    field("Event name", "name", "text", event?.name || "", "required minlength='2'") +
    field("Date", "event_date", "date", event?.event_date || "", "required") +
    field("Description", "description", "textarea", event?.description || "", "required") +
    field("Club", "club_id", "select", clubOptions(event?.club_id)),
    async (data) => {
      const body = {
        name: data.name,
        event_date: data.event_date,
        description: data.description,
        club_id: data.club_id ? Number(data.club_id) : null,
      };
      await CCMS.api(event ? `/events/${event.id}` : "/events", {
        method: event ? "PUT" : "POST",
        body: JSON.stringify(body),
      });
      toast(event ? "Event updated" : "Event created");
      await renderEvents();
    }
  );
}

async function renderAttendance() {
  await refreshLookups();
  const rows = await CCMS.api("/attendance");
  document.getElementById("attendance").innerHTML = `
    <div class="card">
      <h3>Mark attendance</h3>
      <form id="att-form" class="grid-2">
        ${field("Event", "event_id", "select", eventOptions(), "required")}
        ${field("Member", "member_id", "select", memberOptions(), "required")}
        ${field("Status", "status", "select", `<option value="present">Present</option><option value="absent">Absent</option>`)}
        <div class="form-group" style="display:flex;align-items:flex-end">
          <button class="btn btn-primary" type="submit">Save attendance</button>
        </div>
      </form>
      <div id="att-error" class="alert alert-error"></div>
    </div>
    <div class="card">
      <h3>Attendance records</h3>
      <table>
        <thead><tr><th>Event</th><th>Member</th><th>Status</th><th>Marked</th></tr></thead>
        <tbody>
          ${rows.length ? rows.map((a) => `<tr>
            <td>${escapeHtml(a.event_name)}</td>
            <td>${escapeHtml(a.member_name)}</td>
            <td><span class="badge ${a.status === "present" ? "badge-ok" : "badge-no"}">${escapeHtml(a.status)}</span></td>
            <td>${escapeHtml((a.marked_at || "").replace("T", " ").slice(0, 16))}</td>
          </tr>`).join("") : `<tr><td colspan="4" class="empty">No attendance records yet.</td></tr>`}
        </tbody>
      </table>
    </div>`;
  document.getElementById("att-form").onsubmit = async (e) => {
    e.preventDefault();
    const err = document.getElementById("att-error");
    err.classList.remove("show");
    const data = Object.fromEntries(new FormData(e.target).entries());
    try {
      await CCMS.api("/attendance", {
        method: "POST",
        body: JSON.stringify({
          event_id: Number(data.event_id),
          member_id: Number(data.member_id),
          status: data.status,
        }),
      });
      toast("Attendance saved");
      renderAttendance();
    } catch (ex) {
      showError(err, ex.message);
    }
  };
}

async function renderAnnouncements() {
  await refreshLookups();
  const rows = await CCMS.api("/announcements");
  document.getElementById("announcements").innerHTML = `
    <div class="card">
      <h3>Post a notice</h3>
      <form id="ann-form">
        ${field("Title", "title", "text", "", "required minlength='2'")}
        ${field("Content", "content", "textarea", "", "required minlength='2'")}
        ${field("Club (optional)", "club_id", "select", clubOptions())}
        <button class="btn btn-primary" type="submit">Publish</button>
      </form>
      <div id="ann-error" class="alert alert-error"></div>
    </div>
    <div class="card">
      <h3>All notices</h3>
      ${rows.length ? rows.map((a) => `
        <div class="feed-item">
          <h4>${escapeHtml(a.title)}</h4>
          <p>${escapeHtml(a.content)}</p>
          <div class="meta">${escapeHtml(a.author)} · ${escapeHtml(a.club_name || "All clubs")} · ${escapeHtml((a.created_at || "").slice(0, 10))}
            <button class="btn btn-danger btn-sm" data-del="${a.id}" style="margin-left:8px">Delete</button>
          </div>
        </div>`).join("") : `<p class="empty">No announcements yet.</p>`}
    </div>`;
  document.getElementById("ann-form").onsubmit = async (e) => {
    e.preventDefault();
    const err = document.getElementById("ann-error");
    err.classList.remove("show");
    const data = Object.fromEntries(new FormData(e.target).entries());
    try {
      await CCMS.api("/announcements", {
        method: "POST",
        body: JSON.stringify({
          title: data.title,
          content: data.content,
          club_id: data.club_id ? Number(data.club_id) : null,
        }),
      });
      toast("Announcement posted");
      renderAnnouncements();
    } catch (ex) {
      showError(err, ex.message);
    }
  };
  document.querySelectorAll("[data-del]").forEach((btn) => {
    btn.onclick = async () => {
      await CCMS.api(`/announcements/${btn.dataset.del}`, { method: "DELETE" });
      toast("Notice deleted");
      renderAnnouncements();
    };
  });
}

async function renderReports() {
  const data = await CCMS.api("/reports");
  document.getElementById("reports").innerHTML = `
    <div class="metrics">
      <div class="metric"><span>Clubs</span><strong>${data.totals.clubs}</strong></div>
      <div class="metric"><span>Members</span><strong>${data.totals.members}</strong></div>
      <div class="metric"><span>Events</span><strong>${data.totals.events}</strong></div>
      <div class="metric"><span>Present marks</span><strong>${data.totals.present_marks}</strong></div>
    </div>
    <div class="card">
      <h3>Activity by club</h3>
      <table>
        <thead><tr><th>Club</th><th>Members</th><th>Events</th><th>Announcements</th></tr></thead>
        <tbody>
          ${data.by_club.length ? data.by_club.map((r) => `<tr>
            <td>${escapeHtml(r.club)}</td><td>${r.members}</td><td>${r.events}</td><td>${r.announcements}</td>
          </tr>`).join("") : `<tr><td colspan="4" class="empty">No club data.</td></tr>`}
        </tbody>
      </table>
    </div>
    <div class="card">
      <h3>Attendance by event</h3>
      <table>
        <thead><tr><th>Event</th><th>Date</th><th>Club</th><th>Registered</th><th>Present</th><th>Rate</th></tr></thead>
        <tbody>
          ${data.by_event.length ? data.by_event.map((r) => `<tr>
            <td>${escapeHtml(r.event)}</td>
            <td>${escapeHtml(r.date)}</td>
            <td>${escapeHtml(r.club)}</td>
            <td>${r.registrations}</td>
            <td>${r.present}</td>
            <td>${r.attendance_rate}%</td>
          </tr>`).join("") : `<tr><td colspan="6" class="empty">No event data.</td></tr>`}
        </tbody>
      </table>
      <p class="meta">Generated ${escapeHtml(data.generated_at)}</p>
    </div>`;
}

async function renderProfile() {
  const me = await CCMS.api("/auth/me");
  document.getElementById("profile").innerHTML = `
    <div class="card" style="max-width:520px">
      <h3>Profile</h3>
      <form id="profile-form">
        ${field("Username", "username", "text", me.username, "disabled")}
        ${field("Full name", "full_name", "text", me.full_name, "required minlength='2'")}
        ${field("Email", "email", "email", me.email, "required")}
        ${field("New password (optional)", "password", "password", "", "minlength='6' placeholder='Leave blank to keep current'")}
        <button class="btn btn-primary" type="submit">Save profile</button>
      </form>
      <div id="profile-msg" class="alert"></div>
    </div>`;
  document.getElementById("profile-form").onsubmit = async (e) => {
    e.preventDefault();
    const msg = document.getElementById("profile-msg");
    msg.className = "alert";
    const data = Object.fromEntries(new FormData(e.target).entries());
    try {
      const body = { full_name: data.full_name, email: data.email };
      if (data.password) body.password = data.password;
      const updated = await CCMS.api("/auth/profile", { method: "PUT", body: JSON.stringify(body) });
      const session = CCMS.currentUser() || {};
      CCMS.setSession({ token: CCMS.token(), user: { ...session, ...updated } });
      paintUser();
      msg.textContent = "Profile saved.";
      msg.classList.add("show", "alert-ok");
    } catch (ex) {
      msg.textContent = ex.message;
      msg.classList.add("show", "alert-error");
    }
  };
}

function paintUser() {
  const u = CCMS.currentUser();
  const label = u ? `${u.full_name || u.username} (${u.username})` : "User";
  document.getElementById("sidebar-user").textContent = label;
  document.getElementById("header-user").textContent = u?.username || "User";
}

async function boot() {
  if (!requireAuth()) return;
  paintUser();
  document.querySelectorAll(".nav-btn").forEach((btn) => btn.addEventListener("click", () => go(btn.dataset.section)));
  document.getElementById("logout-btn").onclick = () => {
    CCMS.clearSession();
    window.location.replace("/");
  };
  document.getElementById("menu-btn").onclick = () => document.getElementById("sidebar").classList.toggle("open");
  modal.addEventListener("click", (e) => { if (e.target === modal) closeModal(); });
  setInterval(() => {
    if (CCMS.idleExpired()) {
      CCMS.clearSession();
      window.location.replace("/");
    }
  }, 30000);
  ["click", "keydown", "mousemove"].forEach((ev) => document.addEventListener(ev, CCMS.touchActivity, { passive: true }));
  try {
    await CCMS.api("/auth/me");
    go("dashboard");
  } catch {
    CCMS.clearSession();
    window.location.replace("/");
  }
}

boot();
