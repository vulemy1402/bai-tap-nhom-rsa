const $ = (id) => document.getElementById(id);
const notice = $('notice');
const getKeys = () => ({ p: $('p').value.trim(), q: $('q').value.trim(), e: $('e').value.trim() });

function say(message, kind = '') {
  notice.textContent = message;
  notice.className = `notice ${kind}`;
  notice.hidden = !message;
}
function ms(value) {
  return Number(value).toFixed(4) + ' ms';
}
function timing(id, parts) {
  const node = $(id);
  node.replaceChildren();
  parts.forEach(([name, value]) => {
    const card = document.createElement('div');
    card.className = 'timing-stat';
    const label = document.createElement('div');
    label.className = 'timing-label';
    label.textContent = name;
    const number = document.createElement('div');
    number.className = 'timing-value';
    number.textContent = Number(value).toFixed(4);
    const unit = document.createElement('span');
    unit.textContent = 'ms';
    number.append(unit);
    card.append(label, number);
    node.append(card);
  });
  const note = document.createElement('p');
  note.className = 'timing-note';
  note.textContent = 'Đo thời gian xử lý bằng perf_counter · Không tính chờ nhập hoặc đọc/ghi tệp.';
  node.append(note);
  node.hidden = false;
}
async function request(path, payload) {
  const response = await fetch(path, { method: 'POST', headers: {'Content-Type': 'application/json'}, body: JSON.stringify(payload) });
  let data;
  try { data = await response.json(); }
  catch (_) { throw new Error('Không nhận được kết quả từ chương trình. Hãy kiểm tra Terminal.'); }
  if (!response.ok) throw new Error(data.error || 'Không thực hiện được yêu cầu.');
  return data;
}
async function run(button, callback) {
  const original = button.innerHTML;
  button.disabled = true;
  button.textContent = 'Đang xử lý…';
  say('Đang xử lý, vui lòng đợi…', 'busy');
  try { await callback(); }
  catch (error) { say(error.message || 'Đã xảy ra lỗi.', 'error'); }
  finally { button.disabled = false; button.innerHTML = original; }
}

document.querySelectorAll('.tab').forEach((button) => {
  button.addEventListener('click', () => {
    document.querySelectorAll('.tab').forEach((item) => {
      const selected = item === button;
      item.classList.toggle('active', selected);
      item.setAttribute('aria-selected', String(selected));
    });
    document.querySelectorAll('.tab-content').forEach((panel) => {
      const selected = panel.id === 'tab-' + button.dataset.tab;
      panel.classList.toggle('active', selected);
      panel.hidden = !selected;
    });
    $('current-page').textContent = button.querySelector('span').textContent;
    say('');
  });
});

function setPreset(p, q, e, target) {
  $('p').value = p; $('q').value = q; $('e').value = e;
  document.querySelectorAll('.preset').forEach((item) => item.classList.toggle('selected', item.id === target));
  clearNumber();
  say('Đã cập nhật khoá. Các chức năng sẽ dùng p, q, e hiện tại.');
}
$('slide-preset').addEventListener('click', () => { setPreset('17', '11', '7', 'slide-preset'); $('message').value = '88'; });
$('text-preset').addEventListener('click', () => setPreset('61', '53', '17', 'text-preset'));
function clearNumber() {
  $('number-result').hidden = true;
  $('number-empty').hidden = false;
}
['p', 'q', 'e'].forEach((id) => $(id).addEventListener('input', () => {
  document.querySelectorAll('.preset').forEach((item) => item.classList.remove('selected'));
  clearNumber();
}));
$('message').addEventListener('input', clearNumber);
document.querySelectorAll('.use-text-key').forEach((button) => button.addEventListener('click', () => setPreset('61', '53', '17', 'text-preset')));
$('generate-key').addEventListener('click', (event) => run(event.currentTarget, async () => {
  const data = await request('/api/generate', {bits: '512'});
  setPreset(data.p, data.q, data.e, '');
  say(`Đã sinh khoá 512 bit trong ${ms(data.time_ms)}. Hãy giữ lại p, q, e để giải mã sau.`);
}));

$('run-number').addEventListener('click', (event) => run(event.currentTarget, async () => {
  const data = await request('/api/number', {...getKeys(), message: $('message').value.trim()});
  $('num-m').textContent = data.m; $('num-c').textContent = data.c; $('num-r').textContent = data.recovered;
  $('num-n').textContent = data.n; $('num-phi').textContent = data.phi;
  $('num-public').textContent = `(${data.e}, ${data.n})`; $('num-private').textContent = `d = ${data.d}`;
  const lines = (title, rows, formatter) => title + '\n' + rows.map(formatter).join('\n');
  $('trace').textContent = [
    lines('EUCLID MỞ RỘNG', data.euclid, (r) => `${r.r0} = ${r.q} × ${r.r1} + ${r.remainder}`),
    lines('MÃ HOÁ — BÌNH PHƯƠNG VÀ NHÂN', data.enc_trace, (r) => `Bước ${r.step}: bit=${r.bit}; bình phương=${r.squared}; kết quả=${r.result}`),
    lines('GIẢI MÃ — BÌNH PHƯƠNG VÀ NHÂN', data.dec_trace, (r) => `Bước ${r.step}: bit=${r.bit}; bình phương=${r.squared}; kết quả=${r.result}`)
  ].join('\n\n');
  timing('number-timing', [['Tạo khoá', data.key_ms], ['Mã hoá', data.enc_ms], ['Giải mã', data.dec_ms]]);
  $('number-empty').hidden = true; $('number-result').hidden = false;
  const success = document.querySelector('#number-result .success');
  success.textContent = data.valid ? 'Khôi phục thành công' : 'Không khớp';
  say('');
}));

$('encrypt-text').addEventListener('click', (event) => run(event.currentTarget, async () => {
  const data = await request('/api/text/encrypt', {...getKeys(), text: $('plaintext').value});
  $('ciphertext').value = data.data; $('restored-text').value = '';
  timing('text-timing', [['Tạo khoá', data.key_ms], ['Mã hoá', data.time_ms]]);
  say(`Đã mã hoá ${data.input_bytes} byte. Nhấn “Giải mã bản mã” để khôi phục.`);
}));
$('decrypt-text').addEventListener('click', (event) => run(event.currentTarget, async () => {
  if (!$('ciphertext').value.trim()) throw new Error('Hãy mã hoá hoặc dán bản mã trước.');
  const data = await request('/api/text/decrypt', {...getKeys(), data: $('ciphertext').value.trim()});
  $('restored-text').value = data.text;
  timing('text-timing', [['Tạo khoá', data.key_ms], ['Giải mã', data.time_ms]]);
  const matches = data.text === $('plaintext').value;
  say(matches ? 'Giải mã thành công: nội dung khớp bản rõ đang nhập.' : 'Đã giải mã. Nội dung khác bản rõ đang nhập; hãy kiểm tra bản mã và khoá.');
}));

$('file-input').addEventListener('change', () => {
  const file = $('file-input').files[0];
  $('file-name').textContent = file ? `${file.name} · ${file.size.toLocaleString('vi-VN')} byte` : 'Nhấn để chọn tệp · tối đa 1 MB';
});
function fileToBase64(file) {
  return new Promise((resolve, reject) => {
    const reader = new FileReader();
    reader.onload = () => resolve(String(reader.result).split(',')[1]);
    reader.onerror = () => reject(new Error('Không đọc được tệp.'));
    reader.readAsDataURL(file);
  });
}
function downloadBase64(data, name) {
  const raw = atob(data);
  const bytes = new Uint8Array(raw.length);
  for (let i = 0; i < raw.length; i++) bytes[i] = raw.charCodeAt(i);
  const url = URL.createObjectURL(new Blob([bytes], {type: 'application/octet-stream'}));
  const link = document.createElement('a'); link.href = url; link.download = name;
  document.body.appendChild(link); link.click(); link.remove();
  setTimeout(() => URL.revokeObjectURL(url), 1000);
}
async function fileAction(encrypt) {
  const file = $('file-input').files[0];
  if (!file) throw new Error('Hãy chọn tệp trước.');
  const limit = encrypt ? 1024 * 1024 : 2 * 1024 * 1024 + 2048;
  if (file.size > limit) throw new Error(encrypt ? 'Tệp gốc tối đa 1 MB.' : 'Tệp mã quá lớn.');
  const data = await request('/api/file/' + (encrypt ? 'encrypt' : 'decrypt'), {...getKeys(), data: await fileToBase64(file)});
  const name = encrypt ? file.name + '.rsa' : (file.name.endsWith('.rsa') ? file.name.slice(0, -4) : file.name + '.decoded');
  downloadBase64(data.data, name || 'tep_da_giai_ma');
  timing('file-timing', [['Tạo khoá', data.key_ms], [encrypt ? 'Mã hoá' : 'Giải mã', data.time_ms]]);
  say(`Đã ${encrypt ? 'mã hoá' : 'giải mã'} ${data.input_bytes} byte. Tệp kết quả đang được tải xuống.`);
}
$('encrypt-file').addEventListener('click', (event) => run(event.currentTarget, () => fileAction(true)));
$('decrypt-file').addEventListener('click', (event) => run(event.currentTarget, () => fileAction(false)));
$('run-tests').addEventListener('click', (event) => run(event.currentTarget, async () => {
  const data = await request('/api/tests', {});
  $('tests-result').hidden = false;
  $('test-status').textContent = data.ok ? '●  3 CA KIỂM THỬ VÀ ĐỐI CHIẾU: THÀNH CÔNG' : '●  CÓ KIỂM THỬ THẤT BẠI';
  $('test-status').style.color = data.ok ? '#19946d' : '#c35a43';
  $('test-log').textContent = data.output;
  timing('tests-timing', [['Chạy kiểm thử và đối chiếu', data.time_ms]]);
  say(data.ok ? 'Các kiểm thử và đối chiếu đều hoàn tất.' : 'Có lỗi kiểm thử. Xem chi tiết bên dưới.', data.ok ? '' : 'error');
}));
