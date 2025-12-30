<script>
  import { onMount } from 'svelte'
  import { auth } from './firebase'
  import { createUserWithEmailAndPassword, signInWithEmailAndPassword, signOut } from 'firebase/auth'

  let view = 'login' // 'register' | 'login' | 'upload'
  let name = ''
  let email = ''
  let password = ''
  let confirmPassword = ''
  let user = null
  let file = null
  let downloadUrl = ''
  let isProcessing = false
  let statusMessage = ''
  let lastError = ''
  let isObjectUrl = false
  let grayUrl = ''
  let blurUrl = ''
  let edgesUrl = ''
  let grayName = ''
  let blurName = ''
  let edgesName = ''

  onMount(() => {
    auth.onAuthStateChanged(u => {
      user = u
      view = u ? 'upload' : 'login'
    })
  })

  async function register() {
    if (password !== confirmPassword) return alert('Passwords do not match')
    try {
      await createUserWithEmailAndPassword(auth, email, password)
      alert('Registered successfully! You can now login.')
      view = 'login'
    } catch (e) {
      alert(e.message)
    }
  }

  async function login() {
    try {
      await signInWithEmailAndPassword(auth, email, password)
    } catch (e) {
      alert(e.message)
    }
  }

  async function logout() {
    await signOut(auth)
    user = null
    view = 'login'
  }

  async function handleUpload() {
    if (!user) return alert('Login required')
    if (!file) return alert('Select file')
    isProcessing = true
    statusMessage = 'Uploading to server for processing...'
    // Send to Flask backend for processing
    const form = new FormData()
    form.append('file', file, file.name)
    let resp
    try {
      resp = await fetch(`${import.meta.env.VITE_API_URL}/process`, { method: 'POST', body: form })
    } catch (err) {
      isProcessing = false
      statusMessage = ''
      return alert('Processing request failed: ' + err.message)
    }
    if (!resp.ok) {
      isProcessing = false
      statusMessage = ''
      return alert('Processing failed')
    }
    statusMessage = 'Receiving processed images...'
    let data
    try {
      data = await resp.json()
    } catch (err) {
      isProcessing = false
      statusMessage = ''
      lastError = 'Invalid response from server'
      return
    }

    // set URLs and suggested filenames
    grayUrl = data.gray
    blurUrl = data.blur
    edgesUrl = data.edges
    grayName = data.gray_name || 'gray.png'
    blurName = data.blur_name || 'blur.png'
    edgesName = data.edges_name || 'edges.png'
    isProcessing = false
    statusMessage = ''
  }

  function onFileChange(e) {
    file = e.target.files[0]
  }

  // helper for downloading data URLs
  function downloadDataUrl(dataUrl, filename) {
    try {
      const a = document.createElement('a')
      a.href = dataUrl
      a.download = filename
      document.body.appendChild(a)
      a.click()
      a.remove()
    } catch (e) {
      alert('Download failed')
    }
  }
</script>

<style>
  :global(body) {
    margin: 0;
    padding: 0;
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    min-height: 100vh;
    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
  }

  main {
    width: 100%;
    padding: 36px 48px;
    box-sizing: border-box;
    display: flex;
    justify-content: center;
  }

  h2 {
    color: #4a148c;
    text-align: center;
    font-size: 2.25rem;
    margin: 0 0 18px 0;
    text-shadow: 0 3px 10px rgba(0,0,0,0.06);
  }

  .container {
    background: white;
    padding: 36px;
    border-radius: 14px;
    box-shadow: 0 18px 60px rgba(12,18,48,0.12);
    width: calc(100% - 96px);
    max-width: 1400px;
    margin: 0 auto;
  }

  label {
    display: block;
    margin-top: 18px;
    font-weight: 600;
    color: #444;
    font-size: 0.95rem;
    letter-spacing: 0.2px;
  }

  /* Apply uniform styling to all form controls */
  input,
  textarea,
  select {
    width: 100%;
    padding: 14px 16px;
    margin-top: 8px;
    border: 2px solid #e9e9ef;
    border-radius: 10px;
    font-size: 1rem;
    box-sizing: border-box;
    transition: all 0.25s ease;
    background-color: #fbfbfe;
    color: #222;
  }

  input[type="file"] {
    padding: 10px 12px;
  }

  input:focus,
  textarea:focus,
  select:focus {
    outline: none;
    border-color: #7c5cff;
    box-shadow: 0 6px 20px rgba(124,92,255,0.12);
    background-color: #fff;
  }

  button {
    width: 100%;
    padding: 12px;
    margin-top: 24px;
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    color: white;
    border: none;
    border-radius: 8px;
    font-size: 1rem;
    font-weight: 600;
    cursor: pointer;
    transition: all 0.3s ease;
  }

  button:hover {
    transform: translateY(-2px);
    box-shadow: 0 10px 20px rgba(102, 126, 234, 0.3);
  }

  button:active {
    transform: translateY(0);
  }

  p {
    text-align: center;
    color: #666;
    margin-top: 20px;
    font-size: 0.95rem;
  }

  a {
    color: #667eea;
    text-decoration: none;
    font-weight: 600;
    cursor: pointer;
  }

  a:hover {
    text-decoration: underline;
  }

  .user-info {
    display: flex;
    justify-content: space-between;
    align-items: center;
    background: #f5f5f5;
    padding: 12px 16px;
    border-radius: 8px;
    margin-bottom: 20px;
    font-size: 0.95rem;
    color: #333;
  }

  .user-info button {
    width: auto;
    padding: 8px 16px;
    margin-top: 0;
    font-size: 0.85rem;
  }

  .file-input-wrapper {
    position: relative;
    margin-top: 20px;
  }

  .success-message {
    background: #e8f5e9;
    border-left: 4px solid #4caf50;
    color: #2e7d32;
    padding: 12px 16px;
    border-radius: 4px;
    margin-top: 20px;
    font-size: 0.95rem;
  }

  .download-link {
    display: inline-block;
    background: #4caf50;
    color: white;
    padding: 10px 20px;
    border-radius: 6px;
    text-decoration: none;
    margin-top: 10px;
    transition: all 0.3s ease;
  }

  .download-link:hover {
    background: #45a049;
    transform: translateY(-2px);
  }

  .spinner {
    width: 44px;
    height: 44px;
    margin: 0 auto;
    border-radius: 50%;
    border: 5px solid rgba(0,0,0,0.08);
    border-top-color: #7c5cff;
    animation: spin 1s linear infinite;
  }

  @keyframes spin {
    to { transform: rotate(360deg); }
  }
</style>

<main>
  <div class="container">
    {#if view === 'register'}
      <h2>Create Account</h2>
      <label>Name<input type="text" bind:value={name} /></label>
      <label>Email<input type="email" bind:value={email} /></label>
      <label>Password<input type="password" bind:value={password} /></label>
      <label>Confirm Password<input type="password" bind:value={confirmPassword} /></label>
      <button on:click={register}>Register</button>
      <p>Already have an account? <a href="#" on:click={(e)=>{e.preventDefault(); view='login'}}>Login here</a></p>
    {:else if view === 'login'}
      <h2>Welcome Back</h2>
      <label>Email<input type="email" bind:value={email} /></label>
      <label>Password<input type="password" bind:value={password} /></label>
      <button on:click={login}>Login</button>
      <p>Don't have an account? <a href="#" on:click={(e)=>{e.preventDefault(); view='register'}}>Register here</a></p>
    {:else}
      <h2>Process Image</h2>
      <div class="user-info">
        <span>Logged in as <strong>{user && user.email}</strong></span>
        <button on:click={logout}>Logout</button>
      </div>
      <div class="file-input-wrapper">
        <label>Select Image to Process</label>
        <input type="file" accept="image/*" on:change={onFileChange} />
      </div>
      <button on:click={handleUpload} disabled={isProcessing}>Process & Upload</button>
      {#if isProcessing}
        <div style="margin-top:18px; text-align:center">
          <div class="spinner" aria-hidden="true"></div>
          <p style="margin-top:8px; color:#555">{statusMessage || 'Processing... Please wait.'}</p>
        </div>
      {/if}
      {#if lastError}
        <div style="margin-top:12px; background:#fff3f3; border-left:4px solid #f44336; padding:10px; border-radius:6px; color:#611;">
          <strong>Error:</strong> {lastError}
        </div>
      {/if}
      {#if grayUrl || blurUrl || edgesUrl}
        <div class="success-message">
          <p>✓ Image processed successfully!</p>
          <div style="display:flex; flex-direction:column; gap:18px; margin-top:12px; align-items:center">
            {#if grayUrl}
              <div style="width:100%; max-width:420px; text-align:center">
                <h4 style="margin:8px 0">Grayscale</h4>
                <img src={grayUrl} alt="Gray" style="width:100%; border-radius:8px; box-shadow:0 8px 30px rgba(0,0,0,0.15)" />
                <button style="margin-top:8px" on:click={() => downloadDataUrl(grayUrl, grayName)}>Download Grayscale</button>
              </div>
            {/if}
            {#if blurUrl}
              <div style="width:100%; max-width:420px; text-align:center">
                <h4 style="margin:8px 0">Blur</h4>
                <img src={blurUrl} alt="Blur" style="width:100%; border-radius:8px; box-shadow:0 8px 30px rgba(0,0,0,0.15)" />
                <button style="margin-top:8px" on:click={() => downloadDataUrl(blurUrl, blurName)}>Download Blur</button>
              </div>
            {/if}
            {#if edgesUrl}
              <div style="width:100%; max-width:420px; text-align:center">
                <h4 style="margin:8px 0">Edges</h4>
                <img src={edgesUrl} alt="Edges" style="width:100%; border-radius:8px; box-shadow:0 8px 30px rgba(0,0,0,0.15)" />
                <button style="margin-top:8px" on:click={() => downloadDataUrl(edgesUrl, edgesName)}>Download Edges</button>
              </div>
            {/if}
          </div>
        </div>
      {/if}
    {/if}
  </div>
</main>


