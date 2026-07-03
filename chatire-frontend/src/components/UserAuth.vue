<template>
  <div class="auth-page">
    <!-- Animated ambient blobs -->
    <div class="blob blob-1"></div>
    <div class="blob blob-2"></div>
    <div class="blob blob-3"></div>

    <!-- Inline toast -->
    <transition name="toast-slide">
      <div v-if="toast.visible" :class="['toast-bar', `toast-${toast.type}`]">
        <span class="toast-icon">{{ toast.type === 'error' ? '✕' : '✓' }}</span>
        {{ toast.message }}
      </div>
    </transition>

    <!-- Auth Card -->
    <div class="auth-card">
      <!-- Logo -->
      <div class="auth-logo">
        <span class="logo-gradient">Chatire</span>
        <div class="logo-tagline">Real-time chat, reinvented.</div>
      </div>

      <!-- Tabs -->
      <div class="auth-tabs">
        <button
          :class="['tab-btn', activeTab === 'signup' ? 'tab-active' : '']"
          @click="activeTab = 'signup'"
        >Sign Up</button>
        <button
          :class="['tab-btn', activeTab === 'signin' ? 'tab-active' : '']"
          @click="activeTab = 'signin'"
        >Sign In</button>
        <div class="tab-indicator" :style="{ transform: activeTab === 'signin' ? 'translateX(100%)' : 'translateX(0%)' }"></div>
      </div>

      <!-- Sign Up Form -->
      <transition name="form-fade" mode="out-in">
        <form v-if="activeTab === 'signup'" key="signup" @submit.prevent="signUp" class="auth-form">
          <div class="field-group">
            <label>Email Address</label>
            <input v-model="email" type="email" id="email" placeholder="you@example.com" required autocomplete="email" />
          </div>
          <div class="field-row">
            <div class="field-group">
              <label>Username</label>
              <input v-model="username" type="text" id="username" placeholder="username" required autocomplete="username" />
            </div>
            <div class="field-group">
              <label>Password</label>
              <input v-model="password" type="password" id="password" placeholder="••••••••" required autocomplete="new-password" />
            </div>
          </div>
          <div class="toc-row">
            <input type="checkbox" id="toc" required />
            <label for="toc">I accept the <span class="toc-link">Terms &amp; Conditions</span></label>
          </div>
          <button type="submit" class="auth-btn" :disabled="loading">
            <span v-if="loading" class="btn-spinner"></span>
            <span v-else>Create Account</span>
          </button>
        </form>

        <!-- Sign In Form -->
        <form v-else key="signin" @submit.prevent="signIn" class="auth-form">
          <div class="field-group">
            <label>Username</label>
            <input v-model="username" type="text" id="signin-username" placeholder="username" required autocomplete="username" />
          </div>
          <div class="field-group">
            <label>Password</label>
            <input v-model="password" type="password" id="signin-password" placeholder="••••••••" required autocomplete="current-password" />
          </div>
          <button type="submit" class="auth-btn" :disabled="loading">
            <span v-if="loading" class="btn-spinner"></span>
            <span v-else>Sign In</span>
          </button>
        </form>
      </transition>
    </div>
  </div>
</template>

<script>
  const $ = window.jQuery

  export default {

    data () {
      return {
        email: '',
        username: '',
        password: '',
        activeTab: 'signup',
        loading: false,
        toast: { message: '', type: 'error', visible: false }
      }
    },

    methods: {
      showToast (message, type = 'error') {
        this.toast = { message, type, visible: true }
        setTimeout(() => { this.toast.visible = false }, 3500)
      },

      signUp () {
        console.log('signUp method triggered with payload:', { username: this.username, email: this.email })
        const payload = {
          username: this.username,
          password: this.password,
          email: this.email
        }
        this.loading = true
        $.post(`${process.env.API_URL}/auth/users/`, payload, (data) => {
          console.log('signUp succeeded:', data)
          this.loading = false
          this.showToast('Account created! Signing you in…', 'success')
          setTimeout(() => this.signIn(), 800)
        })
        .fail((response) => {
          console.error('signUp failed:', response)
          this.loading = false
          try {
            const err = JSON.parse(response.responseText)
            const msg = Object.values(err).flat().join(' ')
            this.showToast(msg, 'error')
          } catch (e) {
            this.showToast('Sign up failed. Please try again.', 'error')
          }
        })
      },

      signIn () {
        console.log('signIn method triggered with username:', this.username)
        const credentials = { username: this.username, password: this.password }
        this.loading = true

        $.post(`${process.env.API_URL}/auth/jwt/create/`, credentials, (data) => {
          console.log('signIn succeeded with tokens:', data)
          this.loading = false
          sessionStorage.setItem('authToken', data.access)
          sessionStorage.setItem('refreshToken', data.refresh)
          sessionStorage.setItem('username', this.username)

          const redirect = this.$route.query.redirect || '/chats'
          this.$router.push(redirect)
        })
        .fail((response) => {
          console.error('signIn failed:', response)
          this.loading = false
          this.showToast('Invalid credentials. Please try again.', 'error')
        })
      }
    }

  }
</script>

<style scoped>
/* ─── Page Layout ─────────────────────────────────────────── */
.auth-page {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: #0a0a0f;
  position: relative;
  overflow: hidden;
}

/* ─── Animated Ambient Blobs ─────────────────────────────── */
.blob {
  position: absolute;
  border-radius: 50%;
  filter: blur(90px);
  opacity: 0.18;
  animation: blobFloat linear infinite;
}
.blob-1 {
  width: 500px; height: 500px;
  background: #6c63ff;
  top: -150px; left: -150px;
  animation-duration: 18s;
}
.blob-2 {
  width: 400px; height: 400px;
  background: #ff6584;
  bottom: -100px; right: -100px;
  animation-duration: 14s;
  animation-direction: reverse;
}
.blob-3 {
  width: 300px; height: 300px;
  background: #43d9ad;
  top: 50%; left: 60%;
  animation-duration: 22s;
}
@keyframes blobFloat {
  0%   { transform: translate(0, 0) scale(1); }
  33%  { transform: translate(30px, -40px) scale(1.05); }
  66%  { transform: translate(-20px, 20px) scale(0.95); }
  100% { transform: translate(0, 0) scale(1); }
}

/* ─── Toast ──────────────────────────────────────────────── */
.toast-bar {
  position: fixed;
  top: 24px;
  left: 50%;
  transform: translateX(-50%);
  z-index: 9999;
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 13px 24px;
  border-radius: 12px;
  font-size: 14px;
  font-weight: 500;
  backdrop-filter: blur(20px);
  box-shadow: 0 8px 32px rgba(0,0,0,0.4);
  white-space: nowrap;
}
.toast-error  { background: rgba(255, 80, 80, 0.15); border: 1px solid rgba(255,80,80,0.35); color: #ff8080; }
.toast-success{ background: rgba(67, 217, 173, 0.15); border: 1px solid rgba(67,217,173,0.35); color: #43d9ad; }
.toast-icon   { font-size: 13px; font-weight: 700; }

.toast-slide-enter-active, .toast-slide-leave-active { transition: all 0.35s cubic-bezier(.4,0,.2,1); }
.toast-slide-enter { opacity: 0; transform: translateX(-50%) translateY(-20px); }
.toast-slide-leave-to { opacity: 0; transform: translateX(-50%) translateY(-12px); }

/* ─── Auth Card ──────────────────────────────────────────── */
.auth-card {
  position: relative;
  z-index: 10;
  width: 100%;
  max-width: 440px;
  background: rgba(255, 255, 255, 0.04);
  backdrop-filter: blur(24px);
  -webkit-backdrop-filter: blur(24px);
  border: 1px solid rgba(255, 255, 255, 0.08);
  border-radius: 24px;
  padding: 40px 40px 36px;
  box-shadow: 0 24px 80px rgba(0,0,0,0.5), 0 0 0 1px rgba(255,255,255,0.03);
  margin: 20px;
}

/* ─── Logo ───────────────────────────────────────────────── */
.auth-logo {
  text-align: center;
  margin-bottom: 32px;
}
.logo-gradient {
  font-size: 32px;
  font-weight: 700;
  letter-spacing: -1px;
  background: linear-gradient(135deg, #6c63ff, #a78bfa, #43d9ad);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}
.logo-tagline {
  margin-top: 4px;
  font-size: 13px;
  color: rgba(255,255,255,0.35);
  font-weight: 400;
  letter-spacing: 0.3px;
}

/* ─── Tabs ───────────────────────────────────────────────── */
.auth-tabs {
  position: relative;
  display: flex;
  background: rgba(255,255,255,0.05);
  border-radius: 12px;
  padding: 4px;
  margin-bottom: 28px;
  gap: 0;
}
.tab-btn {
  flex: 1;
  padding: 9px 0;
  background: none;
  border: none;
  color: rgba(255,255,255,0.4);
  font-family: 'Inter', sans-serif;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  position: relative;
  z-index: 2;
  transition: color 0.25s;
  border-radius: 9px;
}
.tab-active {
  color: #fff;
}
.tab-indicator {
  position: absolute;
  top: 4px; bottom: 4px;
  left: 4px;
  width: calc(50% - 4px);
  background: linear-gradient(135deg, #6c63ff, #a78bfa);
  border-radius: 9px;
  transition: transform 0.3s cubic-bezier(.4,0,.2,1);
  z-index: 1;
}

/* ─── Forms ──────────────────────────────────────────────── */
.auth-form { display: flex; flex-direction: column; gap: 16px; }

.field-group { display: flex; flex-direction: column; gap: 6px; flex: 1; }
.field-group label {
  font-size: 12px;
  font-weight: 500;
  color: rgba(255,255,255,0.45);
  text-transform: uppercase;
  letter-spacing: 0.7px;
}
.field-group input {
  background: rgba(255,255,255,0.06);
  border: 1px solid rgba(255,255,255,0.1);
  border-radius: 10px;
  padding: 11px 14px;
  font-family: 'Inter', sans-serif;
  font-size: 14px;
  color: #e2e2e2;
  outline: none;
  transition: border-color 0.2s, box-shadow 0.2s, background 0.2s;
  width: 100%;
}
.field-group input::placeholder { color: rgba(255,255,255,0.2); }
.field-group input:focus {
  border-color: rgba(108, 99, 255, 0.6);
  background: rgba(108, 99, 255, 0.06);
  box-shadow: 0 0 0 3px rgba(108, 99, 255, 0.15);
}

.field-row { display: flex; gap: 12px; }

/* ─── ToC ────────────────────────────────────────────────── */
.toc-row {
  display: flex;
  align-items: center;
  gap: 10px;
  font-size: 13px;
  color: rgba(255,255,255,0.35);
}
.toc-row input[type="checkbox"] {
  width: 16px; height: 16px;
  accent-color: #6c63ff;
  cursor: pointer;
}
.toc-link { color: #a78bfa; cursor: pointer; }

/* ─── Submit Button ──────────────────────────────────────── */
.auth-btn {
  width: 100%;
  padding: 13px;
  background: linear-gradient(135deg, #6c63ff, #a78bfa);
  border: none;
  border-radius: 12px;
  color: #fff;
  font-family: 'Inter', sans-serif;
  font-size: 15px;
  font-weight: 600;
  cursor: pointer;
  transition: transform 0.2s, box-shadow 0.2s, opacity 0.2s;
  box-shadow: 0 8px 24px rgba(108, 99, 255, 0.3);
  display: flex;
  align-items: center;
  justify-content: center;
  margin-top: 4px;
  min-height: 46px;
}
.auth-btn:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 12px 32px rgba(108, 99, 255, 0.45);
}
.auth-btn:active:not(:disabled) { transform: translateY(0); }
.auth-btn:disabled { opacity: 0.6; cursor: not-allowed; }

/* ─── Spinner ────────────────────────────────────────────── */
.btn-spinner {
  width: 18px; height: 18px;
  border: 2px solid rgba(255,255,255,0.3);
  border-top-color: #fff;
  border-radius: 50%;
  animation: spin 0.7s linear infinite;
  display: inline-block;
}
@keyframes spin { to { transform: rotate(360deg); } }

/* ─── Form Transition ────────────────────────────────────── */
.form-fade-enter-active, .form-fade-leave-active { transition: opacity 0.2s, transform 0.2s; }
.form-fade-enter { opacity: 0; transform: translateX(10px); }
.form-fade-leave-to { opacity: 0; transform: translateX(-10px); }
</style>
