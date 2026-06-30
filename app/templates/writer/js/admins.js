(async () => {
  const tbody = document.getElementById('adminsBody');
  const modal = document.getElementById('modal');
  const form = document.getElementById('adminForm');
  const toast = document.getElementById('toast');
  const editId = document.getElementById('editId');
  const passwordHint = document.getElementById('passwordHint');

  function showToast(msg, type = 'success') {
    toast.textContent = msg;
    toast.className = `toast ${type}`;
    setTimeout(() => { toast.className = 'toast hidden'; }, 3000);
  }

  function getSelectedRoles() {
    return Array.from(document.querySelectorAll('input[name="role"]:checked'))
      .map(el => el.value);
  }

  function setSelectedRoles(roles) {
    document.querySelectorAll('input[name="role"]').forEach(el => {
      el.checked = roles.includes(el.value);
    });
  }

  function formatDate(iso) {
    return new Date(iso).toLocaleDateString('en-US', { year: 'numeric', month: 'short', day: 'numeric' });
  }

  function openEdit(id, email, roles) {
    document.getElementById('modalTitle').textContent = 'Edit Admin';
    editId.value = id;
    document.getElementById('adminEmail').value = email;
    document.getElementById('adminPassword').value = '';
    passwordHint.style.display = '';
    setSelectedRoles(roles);
    modal.classList.remove('hidden');
  }

  async function deleteAdmin(id, email) {
    if (!confirm(`Delete ${email}? This cannot be undone.`)) return;
    const res = await fetch(`/api/writer/admins/${id}`, {
      method: 'DELETE', credentials: 'include',
    });
    const json = await res.json();
    if (json.status === 'SUCCESS') {
      showToast('Admin deleted');
      await loadAdmins();
    } else {
      showToast(json.code || 'Error', 'error');
    }
  }

  async function loadAdmins() {
    const res = await fetch('/api/writer/admins', { credentials: 'include' });
    const { data } = await res.json();
    if (!data || !data.length) {
      tbody.innerHTML = '<tr><td colspan="4"><p class="empty-state">No admins found.</p></td></tr>';
      return;
    }
    tbody.innerHTML = data.map(a => `
      <tr>
        <td>${a.email}</td>
        <td>${a.roles.map(r => `<span class="role-badge">${r}</span>`).join('')}</td>
        <td>${formatDate(a.created_at)}</td>
        <td>
          <button class="btn-secondary" data-action="edit" data-id="${a.id}" data-email="${a.email}" data-roles="${encodeURIComponent(JSON.stringify(a.roles))}">Edit</button>
          <button class="btn-delete" data-action="delete" data-id="${a.id}" data-email="${a.email}">Delete</button>
        </td>
      </tr>
    `).join('');
  }

  tbody.addEventListener('click', e => {
    const btn = e.target.closest('button[data-action]');
    if (!btn) return;
    const { action, id, email, roles } = btn.dataset;
    if (action === 'delete') {
      deleteAdmin(Number(id), email);
    } else if (action === 'edit') {
      openEdit(Number(id), email, JSON.parse(decodeURIComponent(roles)));
    }
  });

  document.getElementById('addAdminBtn').addEventListener('click', () => {
    document.getElementById('modalTitle').textContent = 'Add Admin';
    editId.value = '';
    form.reset();
    passwordHint.style.display = 'none';
    modal.classList.remove('hidden');
  });

  document.getElementById('cancelBtn').addEventListener('click', () => {
    modal.classList.add('hidden');
  });

  document.getElementById('modalBackdrop').addEventListener('click', () => {
    modal.classList.add('hidden');
  });

  form.addEventListener('submit', async (e) => {
    e.preventDefault();
    const id = editId.value;
    const email = document.getElementById('adminEmail').value;
    const password = document.getElementById('adminPassword').value;
    const roles = getSelectedRoles();

    if (!roles.length) {
      showToast('Select at least one role', 'error');
      return;
    }

    let res;
    if (id) {
      const body = { email, roles };
      if (password) body.password = password;
      res = await fetch(`/api/writer/admins/${id}`, {
        method: 'PATCH', credentials: 'include',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(body),
      });
    } else {
      res = await fetch('/api/writer/admins', {
        method: 'POST', credentials: 'include',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email, password, roles }),
      });
    }

    const json = await res.json();
    if (json.status === 'SUCCESS') {
      modal.classList.add('hidden');
      showToast(id ? 'Admin updated' : 'Admin created');
      await loadAdmins();
    } else {
      showToast(json.code || 'Error', 'error');
    }
  });

  document.getElementById('logoutBtn').addEventListener('click', async () => {
    await fetch('/api/writer/logout', { method: 'POST', credentials: 'include' });
    window.location.href = '/writer/login';
  });

  await loadAdmins();
})();
