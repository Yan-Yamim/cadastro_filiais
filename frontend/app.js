const CONFIG = {
    API_BASE_URL: 'http://localhost:8000',
};

const DOM = {
	form: document.querySelector('#registration-form'),
	activityList: document.querySelector('#activity-list'),
	activityTemplate: document.querySelector('#activity-template'),
	feedback: document.querySelector('#feedback'),
	submitButton: document.querySelector('#submit-button'),
	addActivityBtn: document.querySelector('#add-activity'),
	birthDate: document.querySelector('#data_nascimento'),
	addressFields: Array.from(document.querySelectorAll('.address-field')),
};


const setupBirthDateLimit = () => {
	const today = new Date();
	const localDate = new Date(today.getTime() - today.getTimezoneOffset() * 60000);
	DOM.birthDate.max = localDate.toISOString().slice(0, 10);
};


const addActivityRow = () => {
	const clone = DOM.activityTemplate.content.cloneNode(true);
	DOM.activityList.appendChild(clone);
};


const updateConditionalRequirements = () => {
	const addressHasValues = DOM.addressFields.some((field) => field.value.trim() !== '');
	DOM.addressFields.slice(0, 4).forEach((field) => {
		field.required = addressHasValues;
	});

	const rows = DOM.activityList.querySelectorAll('.activity-card');
	rows.forEach((row) => {
		const channel = row.querySelector('.activity-channel');
		const description = row.querySelector('.activity-description');
		const hasValue = Boolean(channel.value.trim() || description.value.trim());

		channel.required = hasValue;
		description.required = hasValue;
	});
};


const showFeedback = (message, type = 'info') => {
	DOM.feedback.textContent = message;
	DOM.feedback.className = `alert alert-${type}`;
	DOM.feedback.classList.remove('d-none');
	DOM.feedback.scrollIntoView({ behavior: 'smooth', block: 'center' });
};


const setSubmitting = (isSubmitting) => {
	const label = DOM.submitButton.querySelector('.button-label');
	const spinner = DOM.submitButton.querySelector('.spinner-border');

	DOM.submitButton.disabled = isSubmitting;
	label.textContent = isSubmitting ? 'Salvando...' : 'Salvar cadastro';
	spinner.classList.toggle('d-none', !isSubmitting);
};


const buildPayload = () => {
	const hasAddress = DOM.addressFields.some((field) => field.value.trim() !== '');

	const activities = Array.from(DOM.activityList.querySelectorAll('.activity-card'))
		.map((row) => ({
			canal: row.querySelector('.activity-channel').value.trim(),
			descricao: row.querySelector('.activity-description').value.trim(),
		}))
		.filter((act) => act.canal && act.descricao);

	const payload = {
		nome_completo: document.querySelector('#nome_completo').value.trim(),
		data_nascimento: DOM.birthDate.value,
		telefone: document.querySelector('#telefone').value.trim(),
		is_active: document.querySelector('#is_active').checked,
		atividades: activities,
	};

	if (hasAddress) {
		payload.endereco = Object.fromEntries(
			DOM.addressFields.map((field) => [field.id, field.value.trim()])
		);
	}

	return payload;
};


DOM.activityList.addEventListener('click', (event) => {
	if (event.target.classList.contains('remove-activity')) {
		event.target.closest('.activity-card').remove();
		updateConditionalRequirements();
	}
});

DOM.addActivityBtn.addEventListener('click', addActivityRow);
DOM.form.addEventListener('input', updateConditionalRequirements);
DOM.form.addEventListener('change', updateConditionalRequirements);

DOM.form.addEventListener('submit', async (event) => {
	event.preventDefault();
	updateConditionalRequirements();

	if (!DOM.form.reportValidity()) return;

	DOM.feedback.classList.add('d-none');
	setSubmitting(true);

	try {
		const payload = buildPayload();
		const response = await fetch('http://localhost:8000/cadastro', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload),
        });

		const result = await response.json();

		if (!response.ok) {
			const details = Array.isArray(result.detail)
				? result.detail.map((item) => item.msg).join(' ')
				: result.detail;
			throw new Error(details || 'Não foi possível salvar o cadastro.');
		}

		showFeedback(`Cadastro de ${result.nome_completo} salvo com sucesso!`, 'success');

		DOM.form.reset();
		DOM.activityList.replaceChildren();
		addActivityRow();
		updateConditionalRequirements();
	} catch (error) {
		showFeedback(error.message || 'Erro ao se comunicar com o servidor.', 'danger');
	} finally {
		setSubmitting(false);
	}
});

setupBirthDateLimit();
addActivityRow();