<script>
  import { onMount } from 'svelte'
  import { auth, storage } from './firebase'
  import { createUserWithEmailAndPassword, signInWithEmailAndPassword, signOut } from 'firebase/auth'
  import { ref as sref, uploadBytes, getDownloadURL } from 'firebase/storage'

  let view = 'login' // 'register' | 'login' | 'upload'
  let name = ''
  let email = ''
  let password = ''
  let confirmPassword = ''
  let user = null
  let file = null
  let downloadUrl = ''

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
    // Send to Flask backend for processing
    const form = new FormData()
    form.append('file', file, file.name)
    const resp = await fetch('http://localhost:5000/process', { method: 'POST', body: form })
    if (!resp.ok) return alert('Processing failed')
    const blob = await resp.blob()
    // prepare filename like sample_gray.png
    const origName = file.name
    const dot = origName.lastIndexOf('.')
    const base = dot === -1 ? origName : origName.slice(0, dot)
    const ext = dot === -1 ? '.png' : origName.slice(dot)
    const processedName = `${base}_gray${ext}`
    // upload to firebase storage
    const storageRef = sref(storage, `users/${user.uid}/${processedName}`)
    await uploadBytes(storageRef, blob)
    downloadUrl = await getDownloadURL(storageRef)
    alert('Processed and uploaded. You can download the processed image now.')
  }

  function onFileChange(e) {
    file = e.target.files[0]
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
    max-width: 500px;
    margin: 60px auto;
    padding: 0 20px;
  }

  h2 {
    color: #4a148c;
    text-align: center;
    font-size: 2rem;
    margin: 0 0 30px 0;
    text-shadow: 0 2px 6px rgba(0,0,0,0.06);
  }

  .container {
    background: white;
    padding: 40px;
    border-radius: 16px;
    box-shadow: 0 20px 60px rgba(0,0,0,0.3);
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
      <button on:click={handleUpload}>Process & Upload</button>
      {#if downloadUrl}
        <div class="success-message">
          <p>✓ Image processed and uploaded successfully!</p>
          <a href={downloadUrl} target="_blank" rel="noreferrer" class="download-link">Download Processed Image</a>
        </div>
      {/if}
    {/if}
  </div>
</main>
