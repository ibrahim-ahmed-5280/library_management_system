function clearErrors(form) {
    form.querySelectorAll('.invalid-feedback').forEach(el => el.textContent = '');
    form.querySelectorAll('.is-invalid').forEach(el => el.classList.remove('is-invalid'));
}

function showError(input, errorId, message) {
    input.classList.add('is-invalid');
    document.getElementById(errorId).textContent = message;
}

// ---------- Due date validation ----------
function isDueDateValid(dateStr) {
    const today = new Date();
    today.setHours(0,0,0,0);
    const dueDate = new Date(dateStr);
    return dueDate >= today;
}

// ---------- Insert New Issue ----------
function insert_issue() {
    const member = document.getElementById('new_issue_member');
    const edition = document.getElementById('new_issue_edition');
    const due_date = document.getElementById('new_issue_due_date');
    const form = document.getElementById('newIssueForm');

    clearErrors(form);
    let hasError = false;

    if (!member.value) { showError(member, 'new_issue_member_error', 'Select a member.'); hasError = true; }
    if (!edition.value) { showError(edition, 'new_issue_edition_error', 'Select an edition.'); hasError = true; }
    if (!due_date.value) { showError(due_date, 'new_issue_due_date_error', 'Set a due date.'); hasError = true; }
    else if (!isDueDateValid(due_date.value)) {
        showError(due_date, 'new_issue_due_date_error', 'Due date cannot be in the past.');
        hasError = true;
    }
    if (hasError) return;

    const spinner = document.getElementById('new_issue_spinner');
    const btnText = document.getElementById('new_issue_btn_text');
    spinner.classList.remove('d-none'); btnText.textContent = 'Adding...';

    fetch('/issue_books/insert', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
            member_id: member.value,
            edition_id: edition.value,
            due_date: due_date.value
        })
    })
    .then(r => r.json())
    .then(data => {
        const succ_msg = document.getElementById('new_issue_succ_msg');
        const error_msg = document.getElementById('new_issue_err_msg');
        succ_msg.classList.add('d-none'); error_msg.classList.add('d-none');

        if (data.success) {
            succ_msg.textContent = data.message; succ_msg.classList.remove('d-none');
            setTimeout(() => { form.reset(); succ_msg.classList.add('d-none'); location.reload(); }, 1000);
        } else {
            error_msg.textContent = data.message; error_msg.classList.remove('d-none');
        }
    })
    .finally(() => { spinner.classList.add('d-none'); btnText.textContent = 'Add Issue'; });
}

// ---------- Open Edit Modal ----------
function openEditModal(issue_id) {
    const issue = issuesData.find(i => i.request_id === issue_id);
    if (!issue) return;

    document.getElementById('edit_issue_id').value = issue.request_id;

    // Populate members
    const memberSelect = document.getElementById('edit_issue_member');
    memberSelect.innerHTML = '';
    membersData.forEach(m => {
        memberSelect.innerHTML += `<option value="${m.user_id}" ${m.user_id===issue.member_id?'selected':''}>${m.name}</option>`;
    });

    // Populate editions
    const editionSelect = document.getElementById('edit_issue_edition');
    editionSelect.innerHTML = '';
    booksWithEditions.forEach(be => {
        const selected = be.edition.edition_id === issue.edition_id ? 'selected' : '';
        editionSelect.innerHTML += `<option value="${be.edition.edition_id}" ${selected}>${be.edition.edition_number} - ${be.book.title}</option>`;
    });

    document.getElementById('edit_issue_due_date').value = issue.due_date;
    document.getElementById('edit_issue_status').value = issue.status;

    const editModal = new bootstrap.Modal(document.getElementById('editIssueModal'));
    editModal.show();
}

// ---------- Update Issue ----------
function update_issue() {
    const issue_id = document.getElementById('edit_issue_id').value;
    const member = document.getElementById('edit_issue_member');
    const edition = document.getElementById('edit_issue_edition');
    const due_date = document.getElementById('edit_issue_due_date');
    const status = document.getElementById('edit_issue_status');
    const form = document.getElementById('editIssueForm');

    clearErrors(form);
    let hasError = false;

    if (!member.value) { showError(member, 'edit_issue_member_error', 'Select a member.'); hasError = true; }
    if (!edition.value) { showError(edition, 'edit_issue_edition_error', 'Select an edition.'); hasError = true; }
    if (!due_date.value) { showError(due_date, 'edit_issue_due_date_error', 'Set a due date.'); hasError = true; }
    else if (!isDueDateValid(due_date.value)) {
        showError(due_date, 'edit_issue_due_date_error', 'Due date cannot be in the past.');
        hasError = true;
    }
    if (!status.value) { showError(status, 'edit_issue_status_error', 'Select a status.'); hasError = true; }
    if (hasError) return;

    fetch('/issue_books/update', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
            request_id: issue_id,
            member_id: member.value,
            edition_id: edition.value,
            due_date: due_date.value,
            status: status.value
        })
    })
    .then(r => r.json())
    .then(data => {
        const succ_msg = document.getElementById('edit_issue_succ_msg');
        const error_msg = document.getElementById('edit_issue_err_msg');
        succ_msg.classList.add('d-none'); error_msg.classList.add('d-none');

        if (data.success) {
            succ_msg.textContent = data.message; succ_msg.classList.remove('d-none');
            setTimeout(() => location.reload(), 1000);
        } else {
            error_msg.textContent = data.message; error_msg.classList.remove('d-none');
        }
    });
}
