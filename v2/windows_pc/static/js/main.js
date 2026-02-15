// 通用 AJAX 请求函数
async function apiRequest(url, method = 'GET', data = null) {
    const options = {
        method: method,
        headers: {
            'Content-Type': 'application/json'
        }
    };
    if (data) {
        options.body = JSON.stringify(data);
    }
    const response = await fetch(url, options);
    return response.json();
}

// ---------- 主页面功能 ----------
if (document.getElementById('recent-results')) {
    // 页面元素
    const plateDisplay = document.getElementById('plate-display');
    const confidenceDisplay = document.getElementById('confidence-display');
    const statusDisplay = document.getElementById('status-display');
    const statusBadge = document.getElementById('status-badge');
    const recentList = document.getElementById('recent-list');

    // 获取最近识别结果（示例：从服务器轮询）
    async function fetchRecentResults() {
        try {
            // 假设有一个 API 返回最近的识别记录，如果没有，可以省略
            // const data = await apiRequest('/api/recent');
            // 更新 recentList...
        } catch (error) {
            console.error('获取最近结果失败:', error);
        }
    }

    // 每 2 秒轮询一次最新结果（如果服务器支持推送，可以用 WebSocket 或 Server-Sent Events）
    setInterval(fetchRecentResults, 2000);
}

// ---------- 管理页面功能 ----------
if (document.getElementById('vehicle-table')) {
    const vehicleTable = document.getElementById('vehicle-table');
    const addForm = document.getElementById('add-form');

    // 加载所有车辆
    async function loadVehicles() {
        try {
            const vehicles = await apiRequest('/api/vehicles');
            renderVehicleTable(vehicles);
        } catch (error) {
            console.error('加载车辆失败:', error);
        }
    }

    // 渲染表格
    function renderVehicleTable(vehicles) {
        const tbody = vehicleTable.querySelector('tbody');
        tbody.innerHTML = '';
        vehicles.forEach(v => {
            const row = document.createElement('tr');
            row.innerHTML = `
                <td>${v.plate}</td>
                <td>${v.note || ''}</td>
                <td>
                    <button class="btn btn-danger btn-sm" onclick="deleteVehicle('${v.plate}')">删除</button>
                </td>
            `;
            tbody.appendChild(row);
        });
    }

    // 添加车辆
    addForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        const plate = document.getElementById('plate').value.trim();
        const note = document.getElementById('note').value.trim();
        if (!plate) return;

        try {
            const result = await apiRequest('/api/vehicles', 'POST', { plate, note });
            if (result.message) {
                alert(result.message);
                loadVehicles();
                addForm.reset();
            } else if (result.error) {
                alert(result.error);
            }
        } catch (error) {
            alert('添加失败');
        }
    });

    // 删除车辆（全局函数，供按钮调用）
    window.deleteVehicle = async function(plate) {
        if (!confirm(`确定删除车牌 ${plate} 吗？`)) return;
        try {
            const result = await apiRequest(`/api/vehicles/${encodeURIComponent(plate)}`, 'DELETE');
            if (result.message) {
                alert(result.message);
                loadVehicles();
            } else if (result.error) {
                alert(result.error);
            }
        } catch (error) {
            alert('删除失败');
        }
    };

    // 初始化加载
    loadVehicles();
}