/* ================= ADD BOOK ================= */
function add_book() {
    const form = document.getElementById('bookForm');

    // Hide alerts
    const succ_msg = document.getElementById('book_succ_msg');
    const error_msg = document.getElementById('book_error_msg');
    succ_msg.classList.add('d-none');
    error_msg.classList.add('d-none');

    // Trigger Bootstrap validation
    if (!form.checkValidity()) {
        form.classList.add('was-validated');
        return;
    }

    // UI loading
    document.getElementById('bookSpinner').classList.remove('d-none');
    document.getElementById('bookBtnText').textContent = 'Saving...';

    fetch('/books/add', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
            title: form.title_name.value.trim(),
            author_name: form.author_name.value.trim(),
            category_id: form.category_id.value,
            description: form.description.value.trim()
        })
    })
        .then(r => r.json())
        .then(data => {
            if (data.success) {
                succ_msg.textContent = data.message;
                succ_msg.classList.remove('d-none');

                form.reset();
                form.classList.remove('was-validated');

                // Optional extras (your code)
                document.getElementById('edition-tab')?.click();

                const select = document.querySelector(
                    '#editionForm select[name="book_id"]'
                );
                if (select) {
                    select.add(new Option(data.title, data.book_id, true, true));
                }

                setTimeout(() => succ_msg.classList.add('d-none'), 1500);
            } else {
                error_msg.textContent = data.message;
                error_msg.classList.remove('d-none');
            }
        })
        .catch(() => {
            error_msg.textContent = 'Network error. Please try again.';
            error_msg.classList.remove('d-none');
        })
        .finally(() => {
            document.getElementById('bookSpinner').classList.add('d-none');
            document.getElementById('bookBtnText').textContent = 'Add Book';
        });
}


/* ================= ADD EDITION ================= */
function add_edition() {
    const form = document.getElementById('editionForm');

    const succ_msg = document.getElementById('edition_succ_msg');
    const error_msg = document.getElementById('edition_error_msg');

    // Hide alerts
    succ_msg.classList.add('d-none');
    error_msg.classList.add('d-none');

    // Trigger Bootstrap validation
    if (!form.checkValidity()) {
        form.classList.add('was-validated');
        return;
    }

    // Loading UI
    document.getElementById('editionSpinner').classList.remove('d-none');
    document.getElementById('editionBtnText').textContent = 'Saving...';

    fetch('/editions/add', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
            book_id: form.book_id.value,
            edition_number: form.edition_number.value.trim(),
            publisher: form.publisher.value.trim(),
            publication_year: form.publication_year.value || null
        })
    })
        .then(r => r.json())
        .then(data => {
            if (data.success) {
                succ_msg.textContent = data.message;
                succ_msg.classList.remove('d-none');

                form.reset();
                form.classList.remove('was-validated');

                document.getElementById('copies-tab')?.click();

                const select = document.querySelector(
                    '#copiesForm select[name="edition_id"]'
                );
                if (select) {
                    select.add(
                        new Option(
                            `${data.edition_number} - ${data.title}`,
                            data.edition_id,
                            true,
                            true
                        )
                    );
                }

                setTimeout(() => succ_msg.classList.add('d-none'), 1500);
            } else {
                error_msg.textContent = data.message;
                error_msg.classList.remove('d-none');
            }
        })
        .catch(() => {
            error_msg.textContent = 'Network error. Please try again.';
            error_msg.classList.remove('d-none');
        })
        .finally(() => {
            document.getElementById('editionSpinner').classList.add('d-none');
            document.getElementById('editionBtnText').textContent = 'Add Edition';
        });
}


/* ================= ADD COPIES ================= */
function add_book_copies() {
    const form = document.getElementById('copiesForm');

    const succ_msg = document.getElementById('copies_succ_msg');
    const error_msg = document.getElementById('copies_error_msg');

    // Hide alerts
    succ_msg.classList.add('d-none');
    error_msg.classList.add('d-none');

    // Trigger Bootstrap validation
    if (!form.checkValidity()) {
        form.classList.add('was-validated');
        return;
    }

    // Loading UI
    document.getElementById('copiesSpinner').classList.remove('d-none');
    document.getElementById('copiesBtnText').textContent = 'Saving...';

    fetch('/book_copies/add', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
            edition_id: form.edition_id.value,
            copies_count: form.copies_count.value
        })
    })
        .then(r => r.json())
        .then(data => {
            if (data.success) {
                succ_msg.textContent = data.message;
                succ_msg.classList.remove('d-none');

                form.reset();
                form.classList.remove('was-validated');

                setTimeout(() => succ_msg.classList.add('d-none'), 1500);
            } else {
                error_msg.textContent = data.message;
                error_msg.classList.remove('d-none');
            }
        })
        .catch(() => {
            error_msg.textContent = 'Network error. Please try again.';
            error_msg.classList.remove('d-none');
        })
        .finally(() => {
            document.getElementById('copiesSpinner').classList.add('d-none');
            document.getElementById('copiesBtnText').textContent = 'Add Copies';
        });
}


