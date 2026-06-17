(async () => {
  const toast = document.getElementById('toast');

  function showToast(msg, type = 'success') {
    toast.textContent = msg;
    toast.className = `toast ${type}`;
    setTimeout(() => { toast.className = 'toast hidden'; }, 3000);
  }

  const res = await fetch('/api/writer/settings', { credentials: 'include' });
  const { data } = await res.json();
  if (!data) return;

  document.getElementById('blog_name').value = data.blog_name || '';
  document.getElementById('blog_description').value = data.blog_description || '';
  document.getElementById('blog_author').value = data.blog_author || '';
  document.getElementById('blog_tagline').value = data.blog_tagline || '';
  document.getElementById('footer_text').value = data.footer_text || '';
  document.getElementById('posts_per_page').value = data.posts_per_page || '10';
  document.getElementById('allow_indexing').checked = data.allow_indexing !== 'false';
  if (data.og_image_id) {
    document.getElementById('og_image_hint').textContent = `Current image ID: ${data.og_image_id}`;
  }

  document.getElementById('og_image').addEventListener('change', async (e) => {
    const file = e.target.files[0];
    if (!file) return;
    const reader = new FileReader();
    reader.onload = async () => {
      const uploadRes = await fetch('/api/writer/upload-image', {
        method: 'POST',
        credentials: 'include',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ data_url: reader.result }),
      });
      const uploadData = await uploadRes.json();
      if (uploadData.data?.url) {
        const imageId = uploadData.data.url.split('/').pop();
        await fetch('/api/writer/settings', {
          method: 'PATCH',
          credentials: 'include',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ og_image_id: imageId }),
        });
        document.getElementById('og_image_hint').textContent = `Current image ID: ${imageId}`;
        showToast('Social image updated');
      }
    };
    reader.readAsDataURL(file);
  });

  document.getElementById('identityForm').addEventListener('submit', async (e) => {
    e.preventDefault();
    const body = {
      blog_name: document.getElementById('blog_name').value,
      blog_description: document.getElementById('blog_description').value,
      blog_author: document.getElementById('blog_author').value,
      blog_tagline: document.getElementById('blog_tagline').value,
    };
    const r = await fetch('/api/writer/settings', {
      method: 'PATCH',
      credentials: 'include',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(body),
    });
    const json = await r.json();
    json.status === 'SUCCESS'
      ? showToast('Identity settings saved')
      : showToast(json.code || 'Error', 'error');
  });

  document.getElementById('readerForm').addEventListener('submit', async (e) => {
    e.preventDefault();
    const body = {
      footer_text: document.getElementById('footer_text').value,
      posts_per_page: parseInt(document.getElementById('posts_per_page').value),
      allow_indexing: document.getElementById('allow_indexing').checked,
    };
    const r = await fetch('/api/writer/settings', {
      method: 'PATCH',
      credentials: 'include',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(body),
    });
    const json = await r.json();
    json.status === 'SUCCESS'
      ? showToast('Reader settings saved')
      : showToast(json.code || 'Error', 'error');
  });

  document.getElementById('logoutBtn').addEventListener('click', async () => {
    await fetch('/api/writer/logout', { method: 'POST', credentials: 'include' });
    window.location.href = '/writer/login';
  });
})();
