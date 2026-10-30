const $ = id => document.getElementById(id);
let current = null, busy = false;
function message(text, error = false) { $('message').textContent = text; $('message').classList.toggle('error', error); }
function controls() {
  $('choose').disabled = $('detect').disabled = busy;
  $('install').disabled = busy || !current || current.installed;
  $('uninstall').disabled = busy || !current?.installed || current.changed;
}
function showState(state) {
  current = state; $('path').textContent = state.root; $('path').dir = 'ltr';
  $('state').textContent = state.installed ? (state.changed ? 'الملفات معدّلة' : `مثبّت · ${state.version}`) : 'جاهز للتثبيت';
  $('state').classList.toggle('installed', state.installed && !state.changed);
  $('step2').classList.toggle('active', !state.installed); $('step3').classList.toggle('active', state.installed && !state.changed);
  $('success').hidden = !state.installed || state.changed;
  message(state.changed ? 'بعض الملفات تغيّرت بعد التثبيت. لن تُستبدل أو تُحذف تلقائيًا.' : state.installed ? 'التعريب مثبّت. يمكنك استعادة الملفات السابقة بزر الإزالة.' : 'المجلد صحيح. أغلق اللعبة ثم اضغط «تثبيت التعريب».', state.changed);
}
async function select(method) {
  busy = true; controls(); message(method === 'detect' ? 'البحث في مكتبات Steam…' : 'اختر مجلد اللعبة من النافذة…');
  try { const result = await window.installer[method](); if (result.error) message(result.error, true); else if (result.data) showState(result.data); else message('أُلغي اختيار المجلد.'); }
  catch { message('تعذّر التواصل مع التطبيق. أعد تشغيله وحاول مجددًا.', true); }
  finally { busy = false; controls(); }
}
async function operate(action) {
  busy = true; controls(); $('success').hidden = true; $('progress-area').hidden = false; $('progress').value = 0; message('بانتظار تأكيدك…');
  try {
    const result = await window.installer.operate(action);
    if (result.error) message(result.error, true);
    else if (result.data.canceled) message('أُلغيت العملية؛ لم تتغيّر الملفات.');
    else { showState(result.data.state); message(action === 'install' ? 'اكتمل التثبيت بنجاح. اختر Français داخل اللعبة.' : 'أُزيل التعريب واستُعيدت الملفات السابقة.'); }
  } catch { message('توقف الاتصال بالتطبيق. تحقق من حالة الملفات قبل إعادة المحاولة.', true); }
  finally { busy = false; $('progress-area').hidden = true; controls(); }
}
$('choose').addEventListener('click', () => select('choose')); $('detect').addEventListener('click', () => select('detect'));
$('install').addEventListener('click', () => operate('install')); $('uninstall').addEventListener('click', () => operate('uninstall'));
window.installer.onProgress(value => { if (value.percent !== null) $('progress').value = value.percent; message(value.message); }); controls();
