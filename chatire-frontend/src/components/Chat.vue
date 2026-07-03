<template>
  <div class="chat-app">

    <!-- Inline toast -->
    <transition name="toast-slide">
      <div v-if="toast.visible" :class="['toast-bar', `toast-${toast.type}`]">
        <span class="toast-icon">{{ toast.type === 'error' ? '✕' : '✓' }}</span>
        {{ toast.message }}
      </div>
    </transition>

    <!-- ── Active chat session ──────────────────────────────── -->
    <div v-if="sessionStarted" class="chat-window">

      <!-- Header -->
      <div class="chat-header">
        <div class="header-left">
          <div class="app-logo-text">Chatire</div>
          <div class="room-chip">
            <span class="online-dot"></span>
            {{ $route.params.uri ? $route.params.uri.substring(0, 10) + '…' : 'Room' }}
          </div>
        </div>
        <button class="copy-btn" @click="copyInviteLink" :class="{ copied: linkCopied }">
          <svg v-if="!linkCopied" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><path d="M10 13a5 5 0 0 0 7.54.54l3-3a5 5 0 0 0-7.07-7.07l-1.72 1.71"/><path d="M14 11a5 5 0 0 0-7.54-.54l-3 3a5 5 0 0 0 7.07 7.07l1.71-1.71"/></svg>
          <span>{{ linkCopied ? '✓ Copied!' : 'Copy Invite Link' }}</span>
        </button>
      </div>

      <!-- Messages area -->
      <div class="messages-area" ref="chatBody">
        <div
          v-for="(msg, idx) in messages"
          :key="idx"
          class="message-row"
          :class="username === msg.user.username ? 'own-row' : 'peer-row'"
        >
          <!-- Peer message -->
          <template v-if="username !== msg.user.username">
            <div class="avatar" :style="{ background: getAvatarColor(msg.user.username) }">
              {{ msg.user.username[0].toUpperCase() }}
            </div>
            <div class="bubble-group">
              <div class="sender-name">{{ msg.user.username }}</div>
              <div class="bubble peer-bubble">{{ msg.message }}</div>
            </div>
          </template>

          <!-- Own message -->
          <template v-else>
            <div class="bubble-group own-group">
              <div class="bubble own-bubble">{{ msg.message }}</div>
            </div>
            <div class="avatar own-avatar" :style="{ background: getAvatarColor(msg.user.username) }">
              {{ msg.user.username[0].toUpperCase() }}
            </div>
          </template>
        </div>

        <!-- Empty state -->
        <div v-if="messages.length === 0" class="empty-messages">
          <div class="empty-icon">💬</div>
          <p>No messages yet. Say hello!</p>
        </div>
      </div>

      <!-- Input footer -->
      <div class="input-area">
        <form @submit.prevent="postMessage" class="input-form">
          <input
            v-model="message"
            type="text"
            placeholder="Type a message…"
            class="message-input"
            autocomplete="off"
          />
          <button type="submit" class="send-btn" :disabled="!message.trim()">
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2">
              <line x1="22" y1="2" x2="11" y2="13"/>
              <polygon points="22 2 15 22 11 13 2 9 22 2"/>
            </svg>
          </button>
        </form>
      </div>
    </div>

    <!-- ── Welcome screen ──────────────────────────────────── -->
    <div v-else class="welcome-screen">
      <div class="blob blob-1"></div>
      <div class="blob blob-2"></div>
      <div class="blob blob-3"></div>

      <div class="welcome-card">
        <div class="welcome-logo">Chatire</div>
        <div class="welcome-icon">🚀</div>
        <h2 class="welcome-title">Ready to Connect?</h2>
        <p class="welcome-sub">
          Start a new chat session and share the link to chat in real-time with anyone, anywhere.
        </p>
        <button @click="startChatSession" class="start-btn">
          <span>Start Chatting</span>
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5">
            <line x1="5" y1="12" x2="19" y2="12"/>
            <polyline points="12 5 19 12 12 19"/>
          </svg>
        </button>
      </div>
    </div>

  </div>
</template>

<script>
const $ = window.jQuery

export default {
  data () {
    return {
      loading: true,
      notification: new Audio('../../static/plucky.ogg'),
      sessionStarted: false,
      messages: [],
      message: '',
      linkCopied: false,
      toast: { message: '', type: 'error', visible: false }
    }
  },

  created () {
    this.username = sessionStorage.getItem('username')

    // Setup headers for all requests
    $.ajaxSetup({
      beforeSend: function (xhr) {
        xhr.setRequestHeader('Authorization', `JWT ${sessionStorage.getItem('authToken')}`)
      }
    })

    if (this.$route.params.uri) {
      this.joinChatSession()
      this.connectToWebSocket()
    }
    // Simulate loading delay
    setTimeout(() => { this.loading = false }, 2000)
    // Refresh JWT every 4 minutes
    setInterval(this.refreshToken, 240000)
  },

  updated () {
    // Scroll to bottom of Chat window
    const chatBody = this.$refs.chatBody
    if (chatBody) {
      chatBody.scrollTop = chatBody.scrollHeight
    }
  },

  watch: {
    '$route' (to, from) {
      if (to.params.uri && to.params.uri !== from.params.uri) {
        this.joinChatSession()
        this.connectToWebSocket()
      }
    }
  },

  methods: {
    showToast (message, type = 'error') {
      this.toast = { message, type, visible: true }
      setTimeout(() => { this.toast.visible = false }, 3500)
    },

    getAvatarColor (username) {
      const colors = [
        '#6c63ff', '#ff6584', '#43d9ad', '#ff9f43',
        '#5f27cd', '#00d2d3', '#ff6b6b', '#48dbfb',
        '#ff9ff3', '#54a0ff'
      ]
      let hash = 0
      for (let i = 0; i < username.length; i++) {
        hash = username.charCodeAt(i) + ((hash << 5) - hash)
      }
      return colors[Math.abs(hash) % colors.length]
    },

    copyInviteLink () {
      navigator.clipboard.writeText(window.location.href).then(() => {
        this.linkCopied = true
        setTimeout(() => { this.linkCopied = false }, 2500)
      }).catch(() => {
        this.showToast('Could not copy to clipboard', 'error')
      })
    },

    refreshToken () {
      const data = { refresh: sessionStorage.getItem('refreshToken') }
      $.post('http://localhost:8000/this/is/hard/to/find/', data, (response) => {
        sessionStorage.setItem('authToken', response.access)
        if (response.refresh) {
          sessionStorage.setItem('refreshToken', response.refresh)
        }
      })
    },

    startChatSession () {
      $.post('http://localhost:8000/api/chats/', (data) => {
        this.sessionStarted = true
        this.$router.push(`/chats/${data.uri}/`)
      })
      .fail((response) => {
        this.showToast('Failed to create session. Please try again.', 'error')
      })
    },

    postMessage (event) {
      const data = { message: this.message }

      $.post(`http://localhost:8000/api/chats/${this.$route.params.uri}/messages/`, data, (data) => {
        this.message = '' // clear the message after sending
      })
      .fail((response) => {
        this.showToast('Failed to send message.', 'error')
      })
    },

    joinChatSession () {
      const uri = this.$route.params.uri

      $.ajax({
        url: `http://localhost:8000/api/chats/${uri}/`,
        data: { username: this.username },
        type: 'PATCH',
        success: (data) => {
          const user = data.members.find((member) => member.username === this.username)

          if (user) {
            // The user belongs/has joined the session
            this.sessionStarted = true
            this.fetchChatSessionHistory()
          }
        }
      })
    },

    fetchChatSessionHistory () {
      $.get(`http://localhost:8000/api/chats/${this.$route.params.uri}/messages/`, (data) => {
        this.messages = data.messages
        setTimeout(() => { this.loading = false }, 2000)
      })
    },

    connectToWebSocket () {
      const websocket = new WebSocket(`ws://localhost:8081/${this.$route.params.uri}`)
      websocket.onopen = this.onOpen
      websocket.onclose = this.onClose
      websocket.onmessage = this.onMessage
      websocket.onerror = this.onError
    },

    onOpen (event) {
      console.log('Connection opened.', event.data)
    },

    onClose (event) {
      console.log('Connection closed.', event.data)
      // Try and Reconnect after five seconds
      setTimeout(this.connectToWebSocket, 5000)
    },

    onMessage (event) {
      const message = JSON.parse(event.data)
      this.messages.push(message)
      if (!document.hasFocus()) {
        this.notification.play()
      }
    },

    onError (event) {
      console.error('WebSocket error:', event)
    }
  }
}
</script>

<style scoped>
/* ─── Root ───────────────────────────────────────────────── */
.chat-app {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
  background: #0a0a0f;
  position: relative;
}

/* ─── Toast ──────────────────────────────────────────────── */
.toast-bar {
  position: fixed;
  top: 20px;
  left: 50%;
  transform: translateX(-50%);
  z-index: 9999;
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 12px 22px;
  border-radius: 12px;
  font-size: 14px;
  font-weight: 500;
  backdrop-filter: blur(20px);
  box-shadow: 0 8px 32px rgba(0,0,0,0.4);
  white-space: nowrap;
}
.toast-error   { background: rgba(255,80,80,0.15);  border: 1px solid rgba(255,80,80,0.3);  color: #ff8080; }
.toast-success { background: rgba(67,217,173,0.15); border: 1px solid rgba(67,217,173,0.3); color: #43d9ad; }
.toast-icon    { font-size: 12px; font-weight: 700; }
.toast-slide-enter-active, .toast-slide-leave-active { transition: all 0.3s cubic-bezier(.4,0,.2,1); }
.toast-slide-enter { opacity: 0; transform: translateX(-50%) translateY(-16px); }
.toast-slide-leave-to { opacity: 0; transform: translateX(-50%) translateY(-10px); }

/* ─── Chat Window ────────────────────────────────────────── */
.chat-window {
  display: flex;
  flex-direction: column;
  height: 100vh;
  max-width: 860px;
  width: 100%;
  margin: 0 auto;
}

/* ─── Header ─────────────────────────────────────────────── */
.chat-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 14px 24px;
  background: rgba(255,255,255,0.03);
  border-bottom: 1px solid rgba(255,255,255,0.07);
  backdrop-filter: blur(12px);
  flex-shrink: 0;
}
.header-left {
  display: flex;
  align-items: center;
  gap: 16px;
}
.app-logo-text {
  font-size: 20px;
  font-weight: 700;
  letter-spacing: -0.5px;
  background: linear-gradient(135deg, #6c63ff, #a78bfa, #43d9ad);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}
.room-chip {
  display: flex;
  align-items: center;
  gap: 7px;
  background: rgba(108,99,255,0.12);
  border: 1px solid rgba(108,99,255,0.25);
  border-radius: 20px;
  padding: 4px 12px;
  font-size: 12px;
  color: rgba(255,255,255,0.55);
  font-weight: 500;
}
.online-dot {
  width: 7px; height: 7px;
  background: #43d9ad;
  border-radius: 50%;
  box-shadow: 0 0 6px #43d9ad;
  animation: pulse 2s ease-in-out infinite;
}
@keyframes pulse {
  0%, 100% { opacity: 1; }
  50%       { opacity: 0.5; }
}
.copy-btn {
  display: flex;
  align-items: center;
  gap: 8px;
  background: rgba(255,255,255,0.06);
  border: 1px solid rgba(255,255,255,0.1);
  border-radius: 10px;
  padding: 8px 14px;
  font-family: 'Inter', sans-serif;
  font-size: 13px;
  font-weight: 500;
  color: rgba(255,255,255,0.55);
  cursor: pointer;
  transition: all 0.2s;
}
.copy-btn:hover {
  background: rgba(108,99,255,0.15);
  border-color: rgba(108,99,255,0.35);
  color: #a78bfa;
}
.copy-btn.copied {
  background: rgba(67,217,173,0.12);
  border-color: rgba(67,217,173,0.3);
  color: #43d9ad;
}

/* ─── Messages Area ──────────────────────────────────────── */
.messages-area {
  flex: 1;
  overflow-y: auto;
  padding: 24px 20px;
  display: flex;
  flex-direction: column;
  gap: 16px;
  background: #0d0d16;
  scrollbar-width: thin;
  scrollbar-color: rgba(255,255,255,0.1) transparent;
}
.messages-area::-webkit-scrollbar        { width: 4px; }
.messages-area::-webkit-scrollbar-track  { background: transparent; }
.messages-area::-webkit-scrollbar-thumb  { background: rgba(255,255,255,0.12); border-radius: 4px; }

/* ─── Message Rows ───────────────────────────────────────── */
.message-row {
  display: flex;
  align-items: flex-end;
  gap: 10px;
  animation: msgSlideIn 0.3s cubic-bezier(.4,0,.2,1) both;
}
@keyframes msgSlideIn {
  from { opacity: 0; transform: translateY(12px); }
  to   { opacity: 1; transform: translateY(0); }
}
.own-row  { flex-direction: row-reverse; }
.peer-row { flex-direction: row; }

/* ─── Avatar ─────────────────────────────────────────────── */
.avatar {
  width: 36px; height: 36px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 14px;
  font-weight: 600;
  color: #fff;
  flex-shrink: 0;
  box-shadow: 0 4px 12px rgba(0,0,0,0.3);
}

/* ─── Bubble Groups ──────────────────────────────────────── */
.bubble-group {
  display: flex;
  flex-direction: column;
  gap: 4px;
  max-width: 65%;
}
.own-group { align-items: flex-end; }

.sender-name {
  font-size: 11px;
  font-weight: 500;
  color: rgba(255,255,255,0.35);
  padding: 0 4px;
}

/* ─── Bubbles ────────────────────────────────────────────── */
.bubble {
  padding: 11px 15px;
  border-radius: 18px;
  font-size: 14px;
  line-height: 1.5;
  word-break: break-word;
  position: relative;
}
.own-bubble {
  background: linear-gradient(135deg, #6c63ff, #a78bfa);
  color: #fff;
  border-bottom-right-radius: 4px;
  box-shadow: 0 4px 16px rgba(108,99,255,0.3);
}
.peer-bubble {
  background: rgba(255,255,255,0.07);
  border: 1px solid rgba(255,255,255,0.08);
  color: #e2e2e2;
  border-bottom-left-radius: 4px;
  backdrop-filter: blur(8px);
}

/* ─── Empty State ────────────────────────────────────────── */
.empty-messages {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  color: rgba(255,255,255,0.2);
  gap: 10px;
  font-size: 14px;
  padding-top: 60px;
}
.empty-icon { font-size: 40px; opacity: 0.5; }

/* ─── Input Area ─────────────────────────────────────────── */
.input-area {
  padding: 16px 20px;
  background: rgba(255,255,255,0.02);
  border-top: 1px solid rgba(255,255,255,0.06);
  flex-shrink: 0;
}
.input-form {
  display: flex;
  align-items: center;
  gap: 10px;
  background: rgba(255,255,255,0.05);
  border: 1px solid rgba(255,255,255,0.09);
  border-radius: 14px;
  padding: 6px 6px 6px 16px;
  transition: border-color 0.2s, box-shadow 0.2s;
}
.input-form:focus-within {
  border-color: rgba(108,99,255,0.5);
  box-shadow: 0 0 0 3px rgba(108,99,255,0.1);
}
.message-input {
  flex: 1;
  background: none;
  border: none;
  outline: none;
  color: #e2e2e2;
  font-family: 'Inter', sans-serif;
  font-size: 14px;
  padding: 6px 0;
}
.message-input::placeholder { color: rgba(255,255,255,0.2); }
.send-btn {
  width: 38px; height: 38px;
  background: linear-gradient(135deg, #6c63ff, #a78bfa);
  border: none;
  border-radius: 10px;
  color: #fff;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: transform 0.15s, box-shadow 0.15s, opacity 0.15s;
  flex-shrink: 0;
  box-shadow: 0 4px 12px rgba(108,99,255,0.35);
}
.send-btn:hover:not(:disabled) {
  transform: translateY(-1px);
  box-shadow: 0 6px 16px rgba(108,99,255,0.5);
}
.send-btn:disabled { opacity: 0.4; cursor: not-allowed; }

/* ─── Welcome Screen ─────────────────────────────────────── */
.welcome-screen {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  position: relative;
  overflow: hidden;
}

/* Blobs */
.blob {
  position: absolute;
  border-radius: 50%;
  filter: blur(90px);
  opacity: 0.16;
  animation: blobFloat linear infinite;
}
.blob-1 { width: 550px; height: 550px; background: #6c63ff; top: -180px; left: -180px; animation-duration: 18s; }
.blob-2 { width: 400px; height: 400px; background: #ff6584; bottom: -100px; right: -80px; animation-duration: 14s; animation-direction: reverse; }
.blob-3 { width: 300px; height: 300px; background: #43d9ad; top: 40%; left: 55%; animation-duration: 22s; }
@keyframes blobFloat {
  0%   { transform: translate(0,0) scale(1); }
  33%  { transform: translate(30px,-40px) scale(1.04); }
  66%  { transform: translate(-20px,20px) scale(0.96); }
  100% { transform: translate(0,0) scale(1); }
}

.welcome-card {
  position: relative;
  z-index: 10;
  background: rgba(255,255,255,0.04);
  backdrop-filter: blur(24px);
  -webkit-backdrop-filter: blur(24px);
  border: 1px solid rgba(255,255,255,0.08);
  border-radius: 28px;
  padding: 52px 48px;
  text-align: center;
  max-width: 440px;
  width: 90%;
  box-shadow: 0 24px 80px rgba(0,0,0,0.5);
}
.welcome-logo {
  font-size: 28px;
  font-weight: 700;
  letter-spacing: -0.5px;
  background: linear-gradient(135deg, #6c63ff, #a78bfa, #43d9ad);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  margin-bottom: 12px;
}
.welcome-icon { font-size: 48px; margin-bottom: 16px; }
.welcome-title {
  font-size: 26px;
  font-weight: 700;
  color: #fff;
  margin-bottom: 14px;
  letter-spacing: -0.5px;
}
.welcome-sub {
  font-size: 15px;
  color: rgba(255,255,255,0.4);
  line-height: 1.7;
  margin-bottom: 36px;
}
.start-btn {
  display: inline-flex;
  align-items: center;
  gap: 10px;
  background: linear-gradient(135deg, #6c63ff, #a78bfa);
  border: none;
  border-radius: 14px;
  padding: 15px 32px;
  font-family: 'Inter', sans-serif;
  font-size: 15px;
  font-weight: 600;
  color: #fff;
  cursor: pointer;
  transition: transform 0.2s, box-shadow 0.2s;
  box-shadow: 0 8px 28px rgba(108,99,255,0.4);
}
.start-btn:hover {
  transform: translateY(-3px);
  box-shadow: 0 14px 40px rgba(108,99,255,0.55);
}
.start-btn:active { transform: translateY(0); }
</style>
