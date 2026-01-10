function clearErrors(form) {
    form.querySelectorAll('.invalid-feedback').forEach(el => el.textContent = '');
    form.querySelectorAll('.is-invalid').forEach(el => el.classList.remove('is-invalid'));
}

function showError(input, errorId, message) {
    input.classList.add('is-invalid');
    document.getElementById(errorId).textContent = message;
}

function update_book(book_id, author_id) {
    const title = document.getElementById(`book_title${book_id}`);
    const author = document.getElementById(`book_author${book_id}`);
    const category = document.getElementById(`book_category${book_id}`);
    const form = document.getElementById(`book_form${book_id}`);

    clearErrors(form);

    let hasError = false;
    const titleValue = title.value.trim();
    const authorValue = author.value.trim();
    const categoryValue = category.value;

    const succ_msg = document.getElementById(`book_succ_msg${book_id}`);
    const error_msg = document.getElementById(`book_err_msg${book_id}`);
    succ_msg.style.display = 'none';
    error_msg.style.display = 'none';

    // --- Validation ---
    if (!titleValue) {
        showError(title, `book_title_error${book_id}`, 'Book title is required.');
        hasError = true;
    } else if (titleValue.length < 3 || titleValue.length > 150) {
        showError(title, `book_title_error${book_id}`, 'Book title must be 3–150 characters.');
        hasError = true;
    }

    /* -------- Author Name Validation -------- */
    const authorRegex = /^[A-Za-z.\s]+$/;

    if (!authorValue) {
        showError(author, `book_author_error${book_id}`, 'Author name is required.');
        hasError = true;
    } else if (authorValue.length < 3) {
        showError(author, `book_author_error${book_id}`, 'Author name must be at least 3 characters.');
        hasError = true;
    } else if (authorValue.length > 100) {
        showError(author, `book_author_error${book_id}`, 'Author name must not exceed 100 characters.');
        hasError = true;
    } else if (!authorRegex.test(authorValue)) {
        showError(author, `book_author_error${book_id}`, 'Author name can contain letters, spaces, and dots only.');
        hasError = true;
    }

    if (!categoryValue) {
        showError(category, `book_category_error${book_id}`, 'Please select a category.');
        hasError = true;
    }

    if (hasError) return;

    // --- UI Loading ---
    const spinner = document.getElementById(`book_spinner${book_id}`);
    const btnText = document.getElementById(`book_btn_text${book_id}`);
    spinner.classList.remove('d-none');
    btnText.textContent = 'Saving...';

    fetch('/books/update', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
            book_id: book_id,
            title: titleValue,
            author_name: authorValue,
            category_id: categoryValue,
            author_id: author_id
        })
    })
        .then(r => r.json())
        .then(data => {
            if (data.success) {
                succ_msg.style.display = 'block';
                succ_msg.textContent = data.message;

                // Update table row
                document.getElementById(`book_title_cell_${book_id}`).textContent = titleValue;
                document.getElementById(`book_author_cell_${book_id}`).textContent = data.author_name;
                document.getElementById(`book_category_cell_${book_id}`).textContent = data.category_name || 'Uncategorized';

                // Close modal after 1s
                setTimeout(() => {
                    succ_msg.style.display = 'none';
                    const modalEl = document.getElementById(`updateBookModal${book_id}`);
                    const modal = bootstrap.Modal.getInstance(modalEl);
                    if (modal) modal.hide();
                }, 1000);

            } else {
                error_msg.style.display = 'block';
                error_msg.textContent = data.message;

                if (data.error === 'title') {
                    showError(title, `book_title_error${book_id}`, data.message);
                }
                else if (data.error === 'author') {
                    showError(author, `book_author_error${book_id}`, data.message);
                }
                else if (data.error === 'category') {
                    showError(category, `book_category_error${book_id}`, data.message);
                }
            }
        })
        .catch(() => {
            error_msg.style.display = 'block';
            error_msg.textContent = 'Network error. Please try again.';
        })
        .finally(() => {
            spinner.classList.add('d-none');
            btnText.textContent = 'Update Book';
        });
}

function update_edition(edition_id) {

    const form = document.getElementById(`edition_form${edition_id}`);
    clearErrors(form);

    const editionNumber = document.getElementById(`edition_number${edition_id}`);
    const publisher = document.getElementById(`edition_publisher${edition_id}`);
    const year = document.getElementById(`edition_year${edition_id}`);

    const succ_msg = document.getElementById(`edition_succ_msg${edition_id}`);
    const error_msg = document.getElementById(`edition_err_msg${edition_id}`);

    succ_msg.classList.add('d-none');
    error_msg.classList.add('d-none');

    let hasError = false;

    /* ---------- Edition Number ---------- */
    const editionPattern = /^[A-Za-z0-9 .\-]+$/;

    if (!editionNumber.value.trim()) {
        showError(
            editionNumber,
            `edition_number_error${edition_id}`,
            'Edition number is required.'
        );
        hasError = true;
    } else if (
        editionNumber.value.trim().length < 2 ||
        editionNumber.value.trim().length > 30 ||
        !editionPattern.test(editionNumber.value.trim())
    ) {
        showError(
            editionNumber,
            `edition_number_error${edition_id}`,
            'Edition must be 2–30 characters (letters, numbers, . -).'
        );
        hasError = true;
    }

    /* ---------- Publisher ---------- */
    /* ---------- Publisher (REQUIRED) ---------- */
    const publisherValue = publisher.value.trim();
    const publisherPattern = /^[A-Za-z0-9 .'\-&]+$/;

    if (!publisherValue) {
        showError(
            publisher,
            `edition_publisher_error${edition_id}`,
            'Publisher is required.'
        );
        hasError = true;
    } else if (
        publisherValue.length < 2 ||
        publisherValue.length > 100 ||
        !publisherPattern.test(publisherValue)
    ) {
        showError(
            publisher,
            `edition_publisher_error${edition_id}`,
            'Publisher must be 2–100 valid characters.'
        );
        hasError = true;
    }


    /* ---------- Publication Year ---------- */
    if (year.value) {
        const currentYear = new Date().getFullYear();
        const y = parseInt(year.value);

        if (isNaN(y) || y < 1450 || y > currentYear) {
            showError(
                year,
                `edition_year_error${edition_id}`,
                `Year must be between 1450 and ${currentYear}.`
            );
            hasError = true;
        }
    }

    if (hasError) return;

    /* ---------- Submit ---------- */
    fetch('/editions/update', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
            edition_id: edition_id,
            edition_number: editionNumber.value.trim(),
            publisher: publisher.value.trim(),
            publication_year: year.value || null
        })
    })
        .then(r => r.json())
        .then(data => {
            if (data.success) {
                succ_msg.textContent = data.message;
                succ_msg.classList.remove('d-none');

                setTimeout(() => {
                    const modalEl = document.getElementById(`updateEditionModal${edition_id}`);
                    const modal = bootstrap.Modal.getInstance(modalEl);
                    if (modal) modal.hide();
                }, 1000);
            } else {
                error_msg.textContent = data.message;
                error_msg.classList.remove('d-none');
            }
        })
        .catch(() => {
            error_msg.textContent = 'Network error. Please try again.';
            error_msg.classList.remove('d-none');
        });
}
