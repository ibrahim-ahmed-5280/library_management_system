function clearErrors(form) {
    form.querySelectorAll('.error-message').forEach(el => el.textContent = '');
    form.querySelectorAll('.is-invalid').forEach(el => el.classList.remove('is-invalid'));
}

function showError(input, errorId, message) {
    input.classList.add('is-invalid');
    document.getElementById(errorId).textContent = message;
}

function isValidText(value, min, max, pattern) {
    if (value.length < min || value.length > max) return false;
    return pattern.test(value);
}

/* ================= ADD BOOK ================= */
function add_book() {
    const form = document.getElementById('bookForm');
    clearErrors(form);

    const title = form.title_name;
    const author = form.author_name;
    const category = form.category_id;

    let hasError = false;

    // Trim values once
    const titleValue = title.value.trim();
    const authorValue = author.value.trim();

    // Success and error messages
    succ_msg = document.getElementById('book_succ_msg');
    error_msg = document.getElementById('book_error_msg');
    succ_msg.style.display = 'none';
    error_msg.style.display = 'none';

    /* -------- Book Title Validation -------- */
    if (!titleValue) {
        showError(title, 'title_error', 'Book title is required.');
        hasError = true;
    } else if (titleValue.length < 3) {
        showError(title, 'title_error', 'Book title must be at least 3 characters.');
        hasError = true;
    } else if (titleValue.length > 150) {
        showError(title, 'title_error', 'Book title must not exceed 150 characters.');
        hasError = true;
    }

    /* -------- Author Name Validation -------- */
    const authorRegex = /^[A-Za-z.\s]+$/;

    if (!authorValue) {
        showError(author, 'author_error', 'Author name is required.');
        hasError = true;
    } else if (authorValue.length < 3) {
        showError(author, 'author_error', 'Author name must be at least 3 characters.');
        hasError = true;
    } else if (authorValue.length > 100) {
        showError(author, 'author_error', 'Author name must not exceed 100 characters.');
        hasError = true;
    } else if (!authorRegex.test(authorValue)) {
        showError(author, 'author_error', 'Author name can contain letters, spaces, and dots only.');
        hasError = true;
    }

    /* -------- Category Validation -------- */
    if (!category.value) {
        showError(category, 'category_error', 'Please select a category.');
        hasError = true;
    }

    if (hasError) return;

    /* -------- UI Loading State -------- */
    document.getElementById('bookSpinner').classList.remove('d-none');
    document.getElementById('bookBtnText').textContent = 'Saving...';

    fetch('/books/add', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
            title: titleValue,
            author_name: authorValue,
            category_id: category.value,
            description: form.description.value.trim()
        })
    })
        .then(r => r.json())
        .then(data => {
            if (data.success) {
                succ_msg.style.display = 'block';
                succ_msg.textContent = data.message;
                setTimeout(() => {
                    // location.reload();
                    succ_msg.style.display = 'none';
                    form.reset();
                }, 1000);
                succ_msg.style.display = 'none';
                document.getElementById('edition-tab').click();

                const select = document.querySelector(
                    '#editionForm select[name="book_id"]'
                )
                select.add(new Option(data.title, data.book_id, true, true));

            } else {
                error_msg.style.display = 'block';
                error_msg.textContent = data.message;
            }
        })
        .catch(() => {
            error_msg.style.display = 'block';
            error_msg.textContent = 'Network error. Please try again.';
        })
        .finally(() => {
            document.getElementById('bookSpinner').classList.add('d-none');
            document.getElementById('bookBtnText').textContent = 'Add Book';
        });
}

/* ================= ADD EDITION ================= */
function add_edition() {
    const form = document.getElementById('editionForm');
    clearErrors(form);

    let hasError = false;

    const bookId = form.book_id;
    const editionNumber = form.edition_number;
    const publisher = form.publisher;
    const year = form.publication_year;

    // Success and error messages
    succ_msg = document.getElementById('edition_succ_msg');
    error_msg = document.getElementById('edition_error_msg');
    succ_msg.style.display = 'none';
    error_msg.style.display = 'none';

    // ---------- Book ----------
    if (!bookId.value) {
        showError(bookId, 'book_id_error', 'Please select a book.');
        hasError = true;
    }

    // ---------- Edition Number ----------
    const editionPattern = /^[A-Za-z0-9 .\-]+$/;
    if (!editionNumber.value.trim()) {
        showError(editionNumber, 'edition_number_error', 'Edition number is required.');
        hasError = true;
    } else if (!isValidText(editionNumber.value.trim(), 2, 30, editionPattern)) {
        showError(
            editionNumber,
            'edition_number_error',
            'Edition must be 2–30 characters (letters, numbers, . -).'
        );
        hasError = true;
    }

    // ---------- Publisher ----------
    if (publisher.value.trim()) {
        const publisherPattern = /^[A-Za-z0-9 .'\-&]+$/;
        if (!isValidText(publisher.value.trim(), 2, 100, publisherPattern)) {
            showError(
                publisher,
                'publisher_error',
                'Publisher must be 2–100 valid characters.'
            );
            hasError = true;
        }
    }

    // ---------- Publication Year ----------
    if (year.value) {
        const currentYear = new Date().getFullYear();
        const y = parseInt(year.value);

        if (isNaN(y) || y < 1450 || y > currentYear) {
            showError(
                year,
                'publication_year_error',
                `Year must be between 1450 and ${currentYear}.`
            );
            hasError = true;
        }
    }

    if (hasError) return;

    // ---------- UI Loading ----------
    document.getElementById('editionSpinner').classList.remove('d-none');
    document.getElementById('editionBtnText').textContent = 'Saving...';

    // ---------- Submit ----------
    fetch('/editions/add', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
            book_id: bookId.value,
            edition_number: editionNumber.value.trim(),
            publisher: publisher.value.trim(),
            publication_year: year.value || null
        })
    })
        .then(r => r.json())
        .then(data => {
            if (data.success) {
                succ_msg.style.display = 'block';
                succ_msg.textContent = data.message;
                setTimeout(() => {
                    // location.reload();
                    form.reset();
                    succ_msg.style.display = 'none';
                }, 1000);
                document.getElementById('copies-tab').click();

                const select = document.querySelector(
                    '#copiesForm select[name="edition_id"]'
                );
                select.add(new Option(data.edition_number + " - " + data.title, data.edition_id, true, true));
            } else {
                error_msg.textContent = data.message;
                error_msg.style.display = 'block';
            }
        })
        .finally(() => {
            document.getElementById('editionSpinner').classList.add('d-none');
            document.getElementById('editionBtnText').textContent = 'Add Edition';
        });
}

/* ================= ADD COPIES ================= */
function add_book_copies() {
    const form = document.getElementById('copiesForm');
    clearErrors(form);

    let hasError = false;

    if (!form.edition_id.value) {
        showError(form.edition_id, 'edition_id_error', 'Select an edition.');
        hasError = true;
    }
    if (!form.copies_count.value || form.copies_count.value < 1) {
        showError(form.copies_count, 'copies_count_error', 'Minimum 1 copy required.');
        hasError = true;
    }
    if (hasError) return;

    // Success and error messages
    succ_msg = document.getElementById('copies_succ_msg');
    error_msg = document.getElementById('copies_error_msg');
    succ_msg.style.display = 'none';
    error_msg.style.display = 'none';

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
                succ_msg.style.display = 'block';
                setTimeout(() => {
                    // location.reload();
                    succ_msg.style.display = 'none';
                    form.reset();
                }, 1000);
            } else {
                error_msg.style.display = 'block';
                error_msg.textContent = data.message;
            }
        })
        .finally(() => {
            document.getElementById('copiesSpinner').classList.add('d-none');
            document.getElementById('copiesBtnText').textContent = 'Add Copies';
        });
}
