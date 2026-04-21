// ------------------ Employee Chat Logic (existing) ------------------
async function askQuestion(query){
  const res = await fetch('/ask', {
    method:'POST',
    headers:{'Content-Type':'application/json'},
    body: JSON.stringify({query})
  });
  return res.json();
}

window.addEventListener('DOMContentLoaded', ()=>{
  const askBtn = document.getElementById('askBtn');
  const queryInput = document.getElementById('query');
  const chatBox = document.getElementById('chat-box');
  const loader = document.getElementById('loader');
  
  if(askBtn){
    askBtn.addEventListener('click', async ()=>{
      const q = queryInput.value.trim();
      if(!q) return;
      chatBox.innerHTML += `<p><strong>You:</strong> ${q}</p>`;
      loader.style.display = 'block'; // 🔹 Show loader
      
      try {
        const data = await askQuestion(q);
        loader.style.display = 'none'; // 🔹 Hide loader
        if(!data) return;

        if(data.answer){
          chatBox.innerHTML += `<p><strong>Assistant:</strong> ${data.answer}</p>`;
          if(data.sources)
            chatBox.innerHTML += `<p class="muted"><em>Sources:</em><br>${data.sources.join('<br>')}</p>`;
        } else {
          chatBox.innerHTML += `<p><strong>Error:</strong> ${data.error}</p>`;
        }

      } catch(err){
        loader.style.display = 'none'; // Hide loader even if error
        chatBox.innerHTML += `<p><strong>Error:</strong> Something went wrong.</p>`;
      }
      
      queryInput.value = '';
      chatBox.scrollTop = chatBox.scrollHeight;
    });
  }

  // ------------------ HR Chat Logic (new, additive) ------------------
  const hrForm = document.getElementById('hr-chat-form');
  const hrBox = document.getElementById('hr-chat-box');
  const loaderHTML = `<div class="loader"><div class="spinner"></div><p>Assistant is thinking...</p></div>`;

  if(hrForm){
    hrForm.addEventListener('submit', async (e)=>{
      e.preventDefault();
      const formData = new FormData(hrForm);
      const query = formData.get('query').trim();
      const file = formData.get('file');
      
      // Only show alert if both are empty
      if(!query && (!file || !file.name)){
        alert('Please type a question or attach a file.');
        return;
      }

      // Show what HR asked/uploaded
      if(query) hrBox.innerHTML += `<p><strong>You:</strong> ${query}</p>`;
      if(file && file.name) hrBox.innerHTML += `<p><strong>📎 Uploaded:</strong> ${file.name}</p>`;

      hrBox.innerHTML += loaderHTML;

      try {
        const res = await fetch('/ask', {
          method:'POST',
          body: formData
        });

        const contentType = res.headers.get('content-type') || '';
        if(contentType.includes('text/html')){
          alert("Please login to continue.");
          window.location.href = '/login';
          return;
        }

        const data = await res.json();
        hrBox.querySelector('.loader')?.remove();

        if(data.answer){
          hrBox.innerHTML += `<p><strong>Assistant:</strong> ${data.answer}</p>`;
          if(data.sources?.length)
            hrBox.innerHTML += `<p class="muted"><em>Sources:</em><br>${data.sources.join('<br>')}</p>`;
        } else {
          hrBox.innerHTML += `<p><strong>Error:</strong> ${data.error}</p>`;
        }

      } catch(err){
        hrBox.querySelector('.loader')?.remove();
        hrBox.innerHTML += `<p><strong>Error:</strong> Something went wrong.</p>`;
      }

      hrForm.reset();
      hrBox.scrollTop = hrBox.scrollHeight;
    });
  }
});
