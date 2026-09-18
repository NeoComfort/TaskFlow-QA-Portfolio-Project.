const taskForm = document.querySelector("#task-form");
const taskList = document.querySelector("#tasks");
const taskCount = document.querySelector("#task-count");
const filter = document.querySelector("#filter");
const message = document.querySelector("#form-message");
const apiStatus = document.querySelector(".api-status");
const apiStatusText = document.querySelector("#api-status-text");

const statusLabels = {
  todo: "To do",
  in_progress: "In progress",
  done: "Done",
};

function escapeHtml(value) {
  const node = document.createElement("span");
  node.textContent = value;
  return node.innerHTML;
}

async function checkHealth() {
  try {
    const response = await fetch("/health");
    if (!response.ok) throw new Error("API unavailable");
    apiStatus.className = "api-status online";
    apiStatusText.textContent = "API online";
  } catch {
    apiStatus.className = "api-status offline";
    apiStatusText.textContent = "API unavailable";
  }
}

async function loadTasks() {
  const query = filter.value ? `?status=${filter.value}` : "";
  try {
    const response = await fetch(`/tasks${query}`);
    const tasks = await response.json();
    taskCount.textContent = `${tasks.length} task${tasks.length === 1 ? "" : "s"}`;
    taskList.innerHTML = tasks.length
      ? tasks.map((task) => `
          <article class="task">
            <div>
              <h3>${escapeHtml(task.title)}</h3>
              <p>${escapeHtml(task.description || "No description provided.")}</p>
            </div>
            <span class="badge ${task.status}">${statusLabels[task.status]}</span>
          </article>`).join("")
      : '<p class="empty">No tasks here yet. Add your first task to begin.</p>';
  } catch {
    taskList.innerHTML = '<p class="empty">Could not load tasks. Check that the API is running.</p>';
  }
}

taskForm.addEventListener("submit", async (event) => {
  event.preventDefault();
  message.textContent = "";
  message.classList.remove("error");
  const formData = new FormData(taskForm);
  const payload = Object.fromEntries(formData.entries());

  try {
    const response = await fetch("/tasks", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });
    const body = await response.json();
    if (!response.ok) throw new Error(body.error || "Could not create task.");
    message.textContent = `Task #${body.id} created successfully.`;
    taskForm.reset();
    await loadTasks();
  } catch (error) {
    message.textContent = error.message;
    message.classList.add("error");
  }
});

filter.addEventListener("change", loadTasks);
checkHealth();
loadTasks();
