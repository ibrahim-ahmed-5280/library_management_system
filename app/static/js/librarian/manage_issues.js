function insert_issue() {
    // Elements
    const memberEl = document.getElementById('new_issue_member');
    const editionEl = document.getElementById('new_issue_edition');
    const dueDateEl = document.getElementById('new_issue_due_date');

    const successMsg = document.getElementById('new_issue_succ_msg');
    const errorMsg = document.getElementById('new_issue_err_msg');

    const spinner = document.getElementById('new_issue_spinner');
    const btnText = document.getElementById('new_issue_btn_text');

    // Reset UI
    successMsg.classList.add('d-none');
    errorMsg.classList.add('d-none');

    memberEl.classList.remove('is-invalid');
    editionEl.classList.remove('is-invalid');
    dueDateEl.classList.remove('is-invalid');

    let hasError = false;

    // Today (no time)
    const today = new Date();
    today.setHours(0, 0, 0, 0);

    // Member validation
    if (!memberEl.value) {
        memberEl.classList.add('is-invalid');
        document.getElementById('new_issue_member_error').innerText =
            'Member is required';
        hasError = true;
    }

    // Edition validation
    if (!editionEl.value) {
        editionEl.classList.add('is-invalid');
        document.getElementById('new_issue_edition_error').innerText =
            'Edition is required';
        hasError = true;
    }

    // Due date validation
    if (!dueDateEl.value) {
        dueDateEl.classList.add('is-invalid');
        document.getElementById('new_issue_due_date_error').innerText =
            'Due date is required';
        hasError = true;
    } else {
        const dueDate = new Date(dueDateEl.value);
        dueDate.setHours(0, 0, 0, 0);

        if (dueDate <= today) {
            dueDateEl.classList.add('is-invalid');
            document.getElementById('new_issue_due_date_error').innerText =
                'Due date must be greater than today';
            hasError = true;
        }
    }

    if (hasError) return;

    // Show loading
    spinner.classList.remove('d-none');
    btnText.innerText = 'Processing...';

    // Payload
    const payload = {
        member_id: memberEl.value,
        edition_id: editionEl.value,
        due_date: dueDateEl.value
    };

    // Send request
    fetch('/issue_books/insert', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(payload)
    })
        .then(res => res.json())
        .then(data => {
            spinner.classList.add('d-none');
            btnText.innerText = 'Add Issue';

            if (data.success) {
                successMsg.innerText = data.message;
                successMsg.classList.remove('d-none');
                setTimeout(function () {
                    location.reload();
                }, 1000); // <-- Set your desired delay here
                document.getElementById('newIssueForm').reset();
            } else {
                errorMsg.innerText = data.message;
                errorMsg.classList.remove('d-none');
            }
        })
        .catch(err => {
            spinner.classList.add('d-none');
            btnText.innerText = 'Add Issue';
            errorMsg.innerText = 'Server error. Please try again.';
            errorMsg.classList.remove('d-none');
            console.error(err);
        });
}

function update_issue(issueId) {
    // Elements
    const memberEl = document.getElementById(`edit_issue_member${issueId}`);
    const editionEl = document.getElementById(`edit_issue_edition${issueId}`);
    const dueDateEl = document.getElementById(`edit_issue_due_date${issueId}`);

    const successMsg = document.getElementById(`edit_issue_succ_msg${issueId}`);
    const errorMsg = document.getElementById(`edit_issue_err_msg${issueId}`);

    const spinner = document.getElementById(`edit_spinner_${issueId}`);
    const btnText = document.getElementById(`text_btn${issueId}`);

    // Reset UI
    successMsg.classList.add('d-none');
    errorMsg.classList.add('d-none');

    memberEl.classList.remove('is-invalid');
    editionEl.classList.remove('is-invalid');
    dueDateEl.classList.remove('is-invalid');

    let hasError = false;

    // Today (no time)
    const today = new Date();
    today.setHours(0, 0, 0, 0);

    // Member validation
    if (!memberEl.value) {
        memberEl.classList.add('is-invalid');
        document.getElementById(`edit_issue_member_error${issueId}`).innerText =
            'Member is required';
        hasError = true;
    }

    // Edition validation
    if (!editionEl.value) {
        editionEl.classList.add('is-invalid');
        document.getElementById(`edit_issue_edition_error${issueId}`).innerText =
            'Edition is required';
        hasError = true;
    }

    // Due date validation
    if (!dueDateEl.value) {
        dueDateEl.classList.add('is-invalid');
        document.getElementById(`edit_issue_due_date_error${issueId}`).innerText =
            'Due date is required';
        hasError = true;
    } else {
        const dueDate = new Date(dueDateEl.value);
        dueDate.setHours(0, 0, 0, 0);

        if (dueDate <= today) {
            dueDateEl.classList.add('is-invalid');
            document.getElementById(`edit_issue_due_date_error${issueId}`).innerText =
                'Due date must be greater than today';
            hasError = true;
        }
    }

    if (hasError) return;

    // Show loading
    spinner.classList.remove('d-none');
    btnText.innerText = 'Processing...';

    // Payload
    const payload = {
        issue_id: issueId,
        member_id: memberEl.value,
        edition_id: editionEl.value,
        due_date: dueDateEl.value
    };

    // Send request
    fetch('/issue_books/update', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(payload)
    })
        .then(res => res.json())
        .then(data => {
            spinner.classList.add('d-none');
            btnText.innerText = 'Update Issue';

            if (data.success) {
                successMsg.innerText = data.message;
                successMsg.classList.remove('d-none');
                setTimeout(function () {
                    location.reload();
                }, 1000); // <-- Set your desired delay herem/mvc
                // Optionally, update the UI table row with new values
            } else {
                errorMsg.innerText = data.message;
                errorMsg.classList.remove('d-none');
            }
        })
        .catch(err => {
            spinner.classList.add('d-none');
            btnText.innerText = 'Update Issue';
            errorMsg.innerText = 'Server error. Please try again.';
            errorMsg.classList.remove('d-none');
            console.error(err);
        });
}
