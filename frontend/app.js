// ====== Global State ======
let appState = {
    role: null,
    timetable: []
};

// Start Empty! dynamic input
const INPUT_DATA = {
    numDays: 5,
    numSlotsPerDay: 8,
    teachers: [],
    rooms: [],
    sections: [],
    subjects: []
};

const API_BASE = 'http://localhost:8000';

// ====== DOM Elements ======
const authForm = document.getElementById('auth-form');
const roleSelect = document.getElementById('role-select');
const loginView = document.getElementById('login-view');
const dashView = document.getElementById('dashboard-view');
const roleBadge = document.getElementById('role-badge');
const navTimetable = document.getElementById('nav-timetable');
const navInput = document.getElementById('nav-input');
const inputPanel = document.getElementById('input-panel');
const timetableWrapper = document.getElementById('timetable-wrapper');
const actGenerate = document.getElementById('act-generate');
const gridContainer = document.getElementById('grid-container');
const loader = document.getElementById('loader');

// ====== Auth & Navigation ======
authForm.addEventListener('submit', (e) => {
    e.preventDefault();
    appState.role = roleSelect.value;
    roleBadge.textContent = appState.role.toUpperCase();
    
    document.querySelectorAll('.admin-only').forEach(el => {
        el.style.display = appState.role === 'admin' ? '' : 'none';
    });
    
    // Toggle main generate button only if admin
    actGenerate.style.display = appState.role === 'admin' ? 'block' : 'none';

    loginView.classList.remove('active');
    dashView.classList.add('active');
    renderGrid();
});

document.getElementById('act-logout').addEventListener('click', () => {
    dashView.classList.remove('active');
    loginView.classList.add('active');
    appState.role = null;
});

if(navTimetable && navInput) {
    navTimetable.addEventListener('click', (e) => {
        e.preventDefault();
        navTimetable.parentElement.classList.add('active');
        navInput.parentElement.classList.remove('active');
        timetableWrapper.classList.remove('hidden');
        inputPanel.classList.add('hidden');
    });

    navInput.addEventListener('click', (e) => {
        e.preventDefault();
        navInput.parentElement.classList.add('active');
        navTimetable.parentElement.classList.remove('active');
        inputPanel.classList.remove('hidden');
        timetableWrapper.classList.add('hidden');
    });
}

// ====== Form Inputs Logic ======
document.getElementById('form-teacher').addEventListener('submit', (e) => {
    e.preventDefault();
    const t = {
        id: document.getElementById('t-id').value,
        name: document.getElementById('t-name').value,
        maxHoursPerDay: parseInt(document.getElementById('t-hours').value)
    };
    INPUT_DATA.teachers.push(t);
    updateLists();
    
    // Update subject dropdown
    const sel = document.getElementById('sub-teacher');
    const opt = document.createElement('option');
    opt.value = t.id; opt.textContent = t.name;
    sel.appendChild(opt);
    
    e.target.reset();
});

document.getElementById('form-room').addEventListener('submit', (e) => {
    e.preventDefault();
    const r = {
        id: document.getElementById('r-id').value,
        name: document.getElementById('r-name').value,
        capacity: parseInt(document.getElementById('r-cap').value)
    };
    INPUT_DATA.rooms.push(r);
    updateLists();
    e.target.reset();
});

document.getElementById('form-section').addEventListener('submit', (e) => {
    e.preventDefault();
    const s = {
        id: document.getElementById('sec-id').value,
        name: document.getElementById('sec-name').value,
        department: document.getElementById('sec-dept').value,
        year: parseInt(document.getElementById('sec-year').value),
        strength: parseInt(document.getElementById('sec-str').value)
    };
    INPUT_DATA.sections.push(s);
    updateLists();
    e.target.reset();
});

document.getElementById('form-subject').addEventListener('submit', (e) => {
    e.preventDefault();
    const sub = {
        id: document.getElementById('sub-id').value,
        name: document.getElementById('sub-name').value,
        teacherId: document.getElementById('sub-teacher').value,
        lecturesPerWeek: parseInt(document.getElementById('sub-lec').value),
        isPlacement: document.getElementById('sub-placement').checked
    };
    INPUT_DATA.subjects.push(sub);
    updateLists();
    e.target.reset();
});

function updateLists() {
    const tl = document.getElementById('list-teachers'); tl.innerHTML = '';
    INPUT_DATA.teachers.forEach(t => tl.innerHTML += `<li>${t.id}: ${t.name} (Max ${t.maxHoursPerDay} hrs)</li>`);
    
    const rl = document.getElementById('list-rooms'); rl.innerHTML = '';
    INPUT_DATA.rooms.forEach(r => rl.innerHTML += `<li>${r.id}: ${r.name} (Cap ${r.capacity})</li>`);
    
    const sl = document.getElementById('list-sections'); sl.innerHTML = '';
    INPUT_DATA.sections.forEach(s => sl.innerHTML += `<li>${s.id}: ${s.name} (Str ${s.strength})</li>`);
    
    const bl = document.getElementById('list-subjects'); bl.innerHTML = '';
    INPUT_DATA.subjects.forEach(b => bl.innerHTML += `<li>${b.id}: ${b.name} (${b.teacherId}) ${b.isPlacement ? '🔥' : ''}</li>`);
}

// ====== Generator Logic ======
actGenerate.addEventListener('click', async () => {
    if(!INPUT_DATA.sections.length || !INPUT_DATA.subjects.length || !INPUT_DATA.teachers.length || !INPUT_DATA.rooms.length) {
        showToast('Please add at least one Teacher, Room, Section, and Subject before generating.', 'error');
        return;
    }

    try {
        loader.classList.remove('hidden');
        const response = await fetch(`${API_BASE}/generate-timetable`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(INPUT_DATA)
        });
        
        const data = await response.json();
        if (!response.ok) throw new Error(data.detail);
        
        appState.timetable = data.assignedLectures;
        showToast('Timetable Generated Successfully using Graph & Heap algorithms!', 'success');
        
        if (data.errors && data.errors.length) {
            showToast(`${data.errors.length} lectures could not be scheduled due to constraints.`, 'error');
        }
        
        // Auto switch to grid
        navTimetable.click();
        renderGrid();
    } catch (err) {
        showToast(err.message || 'Server connection failed', 'error');
    } finally {
        loader.classList.add('hidden');
    }
});

// ====== Grid Rendering Engine ======
function renderGrid() {
    gridContainer.innerHTML = '';
    
    if (appState.timetable.length === 0) {
        gridContainer.innerHTML = `<div class="empty-state"><h3>No Schedule Generated</h3><p>Ensure you have input valid data, then hit "Generate Strategy".</p></div>`;
        return;
    }

    const days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday'];
    const times = ['8:00 AM', '9:00 AM', '10:00 AM', '11:00 AM', '1:00 PM', '2:00 PM', '3:00 PM', '4:00 PM'];

    // Headers
    gridContainer.appendChild(createDiv('grid-header', 'Timeslot'));
    days.forEach(d => gridContainer.appendChild(createDiv('grid-header', d)));

    // Matrix
    for (let slot = 0; slot < INPUT_DATA.numSlotsPerDay; slot++) {
        gridContainer.appendChild(createDiv('grid-time', times[slot]));
        
        for (let day = 0; day < INPUT_DATA.numDays; day++) {
            const cell = document.createElement('div');
            cell.className = `grid-cell ${appState.role === 'admin' ? 'editable' : ''}`;
            
            let lecturesInSlot = appState.timetable.filter(l => l.day === day && l.timeSlot === slot);
            
            // View filtering (demo logic for student view showing only one section)
            if (appState.role === 'student' && INPUT_DATA.sections.length > 0) {
                // assume view for first section
                lecturesInSlot = lecturesInSlot.filter(l => l.sectionId === INPUT_DATA.sections[0].id);
            }

            lecturesInSlot.forEach(lec => {
                const card = document.createElement('div');
                card.className = `lecture-card ${lec.isPlacement ? 'placement' : ''}`;
                card.innerHTML = `
                    <strong>${lec.subjectId}</strong>
                    <span>Sec: ${lec.sectionId} | Rm: ${lec.roomId}</span>
                    <span>Prof: ${lec.teacherId}</span>
                `;
                
                if (appState.role === 'admin') {
                    card.addEventListener('click', (e) => {
                        e.stopPropagation();
                        openSwapModal(lec);
                    });
                }
                cell.appendChild(card);
            });
            gridContainer.appendChild(cell);
        }
    }
}

function createDiv(className, text) {
    const el = document.createElement('div');
    el.className = className;
    el.textContent = text;
    return el;
}

// ====== Smart Swap Engine ======
const swapModal = document.getElementById('swap-modal');
const swapForm = document.getElementById('swap-form');

function openSwapModal(lecture) {
    document.getElementById('edit-lec-id').value = lecture.id;
    document.getElementById('edit-day').value = lecture.day;
    document.getElementById('edit-slot').value = lecture.timeSlot;
    
    const roomSelect = document.getElementById('edit-room');
    roomSelect.innerHTML = '';
    INPUT_DATA.rooms.forEach(r => {
        const opt = document.createElement('option');
        opt.value = r.id; opt.textContent = r.name;
        if (r.id === lecture.roomId) opt.selected = true;
        roomSelect.appendChild(opt);
    });
    
    swapModal.classList.remove('hidden');
}

document.getElementById('close-modal').addEventListener('click', () => swapModal.classList.add('hidden'));

swapForm.addEventListener('submit', async (e) => {
    e.preventDefault();
    
    const payload = {
        lectureId: document.getElementById('edit-lec-id').value,
        newDay: parseInt(document.getElementById('edit-day').value),
        newSlot: parseInt(document.getElementById('edit-slot').value),
        newRoomId: document.getElementById('edit-room').value,
        currentTimetable: appState.timetable,
        inputData: INPUT_DATA
    };

    try {
        const res = await fetch(`${API_BASE}/edit-slot`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        });
        
        const data = await res.json();
        if (!res.ok) throw new Error(data.detail || 'Swap failed!');
        
        appState.timetable = data.assignedLectures;
        showToast(data.message, 'success');
        renderGrid();
        swapModal.classList.add('hidden');
    } catch (err) {
        showToast(err.message, 'error');
    }
});

// ====== PDF Export ======
document.getElementById('export-btn').addEventListener('click', () => {
    if(appState.timetable.length === 0) {
        showToast('No timetable to export.', 'error');
        return;
    }
    const element = document.getElementById('grid-container');
    const opt = {
      margin:       0.5,
      filename:     'timetable.pdf',
      image:        { type: 'jpeg', quality: 0.98 },
      html2canvas:  { scale: 2, useCORS: true },
      jsPDF:        { unit: 'in', format: 'a3', orientation: 'landscape' }
    };
    
    // We add a class temporary to fix grid for PDF if needed
    element.style.overflow = 'visible';
    element.style.height = 'auto';
    
    html2pdf().set(opt).from(element).save().then(() => {
        showToast('Timetable Exported as PDF!', 'success');
        element.style.overflow = 'auto';
        element.style.height = '';
    });
});

function showToast(msg, type) {
    const toast = document.createElement('div');
    toast.className = `toast ${type}`;
    toast.textContent = msg;
    document.getElementById('toast-hub').appendChild(toast);
    setTimeout(() => {
        toast.style.opacity = '0';
        setTimeout(() => toast.remove(), 300);
    }, 4000);
}