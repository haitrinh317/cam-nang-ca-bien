/**
 * admin.js — Xử lý logic đăng nhập và dashboard quản trị
 */
import { db } from '../lib/supabase.js'

// Elements
const authSection = document.getElementById('authSection')
const adminSection = document.getElementById('adminSection')
const loginForm = document.getElementById('loginForm')
const loginBtn = document.getElementById('loginBtn')
const authError = document.getElementById('authError')
const logoutBtn = document.getElementById('logoutBtn')
const userInfo = document.getElementById('userInfo')

const speciesTableBody = document.getElementById('speciesTableBody')
const searchAdmin = document.getElementById('searchAdmin')
const filterVol = document.getElementById('filterVol')
const prevPage = document.getElementById('prevPage')
const nextPage = document.getElementById('nextPage')
const pageInfo = document.getElementById('pageInfo')

// State
let currentPage = 1
const PAGE_SIZE = 20
let currentSearch = ''
let currentVol = ''

// Initialize
async function init() {
    const { data: { session }, error } = await db.auth.getSession()
    if (error) console.error('Lỗi lấy session:', error)

    if (session) {
        showAdmin(session.user)
    } else {
        showAuth()
    }

    // Lắng nghe thay đổi Auth state
    db.auth.onAuthStateChange((event, session) => {
        if (event === 'SIGNED_IN' && session) {
            showAdmin(session.user)
        } else if (event === 'SIGNED_OUT') {
            showAuth()
        }
    })
}

function showAuth() {
    authSection.classList.remove('hidden')
    adminSection.classList.add('hidden')
}

async function showAdmin(user) {
    authSection.classList.add('hidden')
    adminSection.classList.remove('hidden')
    userInfo.textContent = `Đăng nhập với email: ${user.email}`
    loadData()
}

// Login
loginForm?.addEventListener('submit', async (e) => {
    e.preventDefault()
    const email = document.getElementById('email').value
    const password = document.getElementById('password').value
    
    loginBtn.textContent = 'Đang đăng nhập...'
    loginBtn.disabled = true
    authError.style.display = 'none'

    const { data, error } = await db.auth.signInWithPassword({
        email,
        password
    })

    if (error) {
        authError.textContent = error.message === 'Invalid login credentials' ? 'Email hoặc mật khẩu không đúng.' : error.message
        authError.style.display = 'block'
        loginBtn.textContent = 'Đăng nhập'
        loginBtn.disabled = false
    } else {
        loginBtn.textContent = 'Đăng nhập'
        loginBtn.disabled = false
        // onAuthStateChange sẽ tự chuyển sang trang Admin
    }
})

// Logout
logoutBtn?.addEventListener('click', async () => {
    await db.auth.signOut()
})

// Load data
async function loadData() {
    speciesTableBody.innerHTML = '<tr><td colspan="5" style="text-align:center;">Đang tải dữ liệu...</td></tr>'
    
    let query = db.from('species').select('id, volume, vn_name, scientific_name, tax_family_latin', { count: 'exact' })
    
    if (currentVol) {
        query = query.eq('volume', parseInt(currentVol))
    }
    
    if (currentSearch) {
        // Tạm dùng ilike cho đơn giản, nếu có FTS (Full text search) thì dùng .textSearch
        query = query.or(`vn_name.ilike.%${currentSearch}%,scientific_name.ilike.%${currentSearch}%`)
    }
    
    const from = (currentPage - 1) * PAGE_SIZE
    const to = from + PAGE_SIZE - 1
    
    query = query.range(from, to).order('volume', { ascending: true }).order('species_index', { ascending: true })
    
    const { data, error, count } = await query
    
    if (error) {
        console.error('Lỗi lấy danh sách loài:', error)
        speciesTableBody.innerHTML = `<tr><td colspan="5" style="color:#ef4444;text-align:center;">Lỗi tải dữ liệu: ${error.message}</td></tr>`
        return
    }

    renderTable(data)
    updatePagination(count)
}

function renderTable(data) {
    if (!data || data.length === 0) {
        speciesTableBody.innerHTML = '<tr><td colspan="5" style="text-align:center;color:#94a3b8;">Không tìm thấy kết quả.</td></tr>'
        return
    }

    speciesTableBody.innerHTML = data.map(item => `
        <tr>
            <td>
                <span style="color:#94a3b8;font-size:0.875rem;">Vol ${item.volume}</span><br>
                ${item.id}
            </td>
            <td style="font-weight:500;">${item.vn_name || '—'}</td>
            <td style="font-style:italic;color:#93c5fd;">${item.scientific_name || '—'}</td>
            <td>${item.tax_family_latin || '—'}</td>
            <td>
                <button class="btn btn-outline" style="padding: 0.25rem 0.5rem; font-size: 0.875rem;" onclick="alert('Chức năng sửa đang hoàn thiện!')">Sửa</button>
            </td>
        </tr>
    `).join('')
}

function updatePagination(total) {
    const totalPages = Math.ceil(total / PAGE_SIZE) || 1
    pageInfo.textContent = `Trang ${currentPage} / ${totalPages} (Tổng ${total} loài)`
    
    prevPage.disabled = currentPage <= 1
    nextPage.disabled = currentPage >= totalPages
}

prevPage?.addEventListener('click', () => {
    if (currentPage > 1) {
        currentPage--
        loadData()
    }
})

nextPage?.addEventListener('click', () => {
    currentPage++
    loadData()
})

let searchTimeout;
searchAdmin?.addEventListener('input', (e) => {
    clearTimeout(searchTimeout)
    searchTimeout = setTimeout(() => {
        currentSearch = e.target.value.trim()
        currentPage = 1
        loadData()
    }, 500)
})

filterVol?.addEventListener('change', (e) => {
    currentVol = e.target.value
    currentPage = 1
    loadData()
})

// Chạy khởi tạo
init()
