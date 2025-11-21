// Countdown timer for quinceañera date - uses Django template variable
let countdownDate
let timerInterval
// The template will set window.invitacionFecha (timestamp in ms). We intentionally do NOT
// declare a local `invitacionFecha` here so the global value set by the template is used.
let handleAudioFade // Declare the variable
let handleFloralAnimation // Declare the variable
let handleTimelineAnimation // Declare the variable

// Initialize countdown date from Django template
document.addEventListener("DOMContentLoaded", () => {
  // Get date from Django template variable (set in HTML). Prefer the global window value.
  if (typeof window.invitacionFecha !== "undefined") {
    countdownDate = window.invitacionFecha
  } else if (typeof invitacionFecha !== "undefined") {
    // fallback if some other script defined it in scope
    countdownDate = invitacionFecha
  } else {
    // Fallback date
    countdownDate = new Date("March 20, 2025 15:00:00").getTime()
  }

  // Start countdown
  timerInterval = setInterval(updateCountdown, 1000)
  updateCountdown()

  // Add scroll listeners
  window.addEventListener("scroll", () => {
    // Keep audio playing uninterrupted on scroll: do not call handleAudioFade here.
    handleFloralAnimation()
    handleTimelineAnimation()
  })

  // Initial animation check
  handleTimelineAnimation()

  // Auto-play audio (with user interaction requirement)
  const audio = document.getElementById("celebration-song")
  if (audio) {
    document.addEventListener(
      "click",
      () => {
        audio.play().catch((e) => {
          console.log("Audio autoplay prevented by browser")
        })
      },
      { once: true },
    )
  }

  // Add fade-in animation to sections
  const sections = document.querySelectorAll(".section-content")
  const observerOptions = {
    threshold: 0.1,
    rootMargin: "0px 0px -100px 0px",
  }

  const observer = new IntersectionObserver((entries) => {
    entries.forEach((entry) => {
      if (entry.isIntersecting) {
        entry.target.classList.add("fade-in-up")
      }
    })
  }, observerOptions)

  sections.forEach((section) => {
    observer.observe(section)
  })

  // Add multiple song suggestions dynamically
  document.getElementById("addSong").addEventListener("click", () => {
    const songSuggestions = document.getElementById("songSuggestions")
    const newSongIndex = songSuggestions.children.length + 1
    const newSongDiv = document.createElement("div")
    newSongDiv.classList.add("song-suggestion", "mb-3")
    newSongDiv.innerHTML = `
      <label for="songName${newSongIndex}" class="form-label">Sugerir una canción</label>
      <input type="text" class="form-control" id="songName${newSongIndex}" name="song_name[]" placeholder="Nombre de la canción">
      <label for="artistName${newSongIndex}" class="form-label mt-2">Artista</label>
      <input type="text" class="form-control" id="artistName${newSongIndex}" name="artist_name[]" placeholder="Nombre del artista (opcional)">
    `
    songSuggestions.appendChild(newSongDiv)
  })
})

function updateCountdown() {
  const now = new Date().getTime()
  const distance = countdownDate - now

  if (distance < 0) {
    document.getElementById("dias").innerText = "00"
    document.getElementById("horas").innerText = "00"
    document.getElementById("minutos").innerText = "00"
    document.getElementById("segundos").innerText = "00"
    clearInterval(timerInterval)
    return
  }

  const days = Math.floor(distance / (1000 * 60 * 60 * 24))
  const hours = Math.floor((distance % (1000 * 60 * 60 * 24)) / (1000 * 60 * 60))
  const minutes = Math.floor((distance % (1000 * 60 * 60)) / (1000 * 60))
  const seconds = Math.floor((distance % (1000 * 60)) / 1000)

  document.getElementById("dias").innerText = days.toString().padStart(2, "0")
  document.getElementById("horas").innerText = hours.toString().padStart(2, "0")
  document.getElementById("minutos").innerText = minutes.toString().padStart(2, "0")
  document.getElementById("segundos").innerText = seconds.toString().padStart(2, "0")
}

// Keep audio playing at a steady volume regardless of scroll.
handleAudioFade = () => {
  const audio = document.getElementById("celebration-song")
  if (!audio) return
  // Ensure a comfortable default volume and do not reduce it on scroll.
  audio.volume = 0.3
}

handleFloralAnimation = () => {
  const scrollPosition = window.scrollY
  const florals = document.querySelectorAll(".floral-decoration")

  florals.forEach((floral) => {
    if (scrollPosition > 100) {
      floral.classList.add("visible")
    } else {
      floral.classList.remove("visible")
    }
  })
}

handleTimelineAnimation = () => {
  const timelineItems = document.querySelectorAll(".timeline-item")
  const windowHeight = window.innerHeight

  timelineItems.forEach((item, index) => {
    const itemTop = item.getBoundingClientRect().top

    if (itemTop < windowHeight * 0.8) {
      setTimeout(() => {
        item.classList.add("visible")
      }, index * 150)
    }
  })
}
