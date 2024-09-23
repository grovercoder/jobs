function get_gui() {
    return {
        detail_overview : document.getElementById('detail-overview'),
        detail_resume: document.getElementById('detail-resume'),
        resume_text: document.getElementById('resume-content'),
        keyword_text: document.getElementById('keyword-content'),
        report: document.getElementById("report"),
    }
}

function get_resume_text() {
    const gui = get_gui()
    const resume = localStorage.getItem('resume')
    const keywords = localStorage.getItem('keywords')

    
    if (gui.keyword_text) {
        keyword_data = JSON.parse(keywords)
        let keylist = document.createElement('ul')
        
        for (const key in keyword_data) {
            let item = document.createElement('li')
            item.textContent = `${key}: ${keyword_data[key]}`
            keylist.appendChild(item)
        }
        
        gui.keyword_text.innerHTML = keylist.outerHTML
    }

    if (gui.resume_text) {
        gui.resume_text.innerText = resume
        gui.detail_overview.open = false
        gui.detail_resume.open = false

        get_report()
    }
}

function submit_resume(event) {
    event.preventDefault(); // Prevent default form submission behavior
    
    const fileInput = document.getElementById('resume-file');
    const formData = new FormData();
    formData.append('file', fileInput.files[0]);

    fetch('/resume', {
        method: 'POST',
        body: formData
    })
    .then(response => response.json())
    .then(data => {
        const gui = get_gui()
        localStorage.setItem('resume', data.resume_content)
        localStorage.setItem('keywords', JSON.stringify(data.resume_keywords))
        get_report()
        gui.detail_overview.open = false
        gui.detail_resume.open = false
    })
    .catch(error => {
        console.error('Error:', error);
    });
}

function get_report() {
    const resumeContent = localStorage.getItem('resume');

    if (resumeContent) {
      fetch('/report', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ resume: resumeContent })
      })
      .then(response => response.text())
      .then(data => {
        // Handle the response data
        const gui = get_gui()
        gui.report.innerHTML = data
      })
      .catch(error => {
        console.error('Error:', error);
      });
    }
}

function rememberDetailsState() {
    gui = get_gui()
    if (gui.detail_overview) {
      const isDetailsOpen = gui.detail_overview.open;
      localStorage.setItem('detail_overview', isDetailsOpen);
    }
  }
  
  function restoreDetailsState() {
    gui = get_gui()    
    if (gui.detail_overview) {
      const storedState = localStorage.getItem('detail_overview');
      console.log({storedState})
  
      if (storedState !== null) {
        gui.detail_overview.open = storedState === 'true';
      }
      else {
        gui.detail_overview.open = true
        gui.detail_resume.open = true
      }
    }
  }


document.addEventListener("DOMContentLoaded", (evt) => {
    const gui = get_gui()

    get_resume_text()
    const form = document.getElementById('resume-form');
    form.addEventListener('submit', submit_resume);

    gui.detail_overview.addEventListener('toggle', rememberDetailsState)
    restoreDetailsState()
})