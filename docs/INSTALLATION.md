# دليل التثبيت والاستخدام

هذا الدليل يشرح تثبيت حزمة الوكلاء في مشروع OpenCode قائم، وليس تثبيت OpenCode نفسه.

## المتطلبات

- OpenCode **v2** مثبت ومتاح في `PATH` أو `~/.opencode/bin/opencode` عند التثبيت والتحقق.
- Bash و`curl` و`tar` وPython 3.9 أو أحدث، إضافة إلى الأدوات القياسية `find` و`grep` و`mktemp`.
- اتصال بالإنترنت لتنزيل الحزمة من GitHub.
- التشغيل من جذر المشروع المقصود، أو تمرير `--project` لمسار مشروع موجود.

لا يحتاج التثبيت إلى مفتاح API أو بيانات اعتماد مزود نموذج. وقد يحتاج تشغيل الوكلاء لاحقاً إلى تهيئة مزود ونموذج في OpenCode.

## أوامر curl الموحدة

من داخل مجلد المشروع:

```bash
curl -fsSL https://raw.githubusercontent.com/Alqudimi/ather-agents/main/install.sh | bash -s -- install
```

تحقق من التثبيت:

```bash
curl -fsSL https://raw.githubusercontent.com/Alqudimi/ather-agents/main/install.sh | bash -s -- verify
```

إزالة الحزمة:

```bash
curl -fsSL https://raw.githubusercontent.com/Alqudimi/ather-agents/main/install.sh | bash -s -- uninstall
```

يفحص `install` و`verify` إصدار CLI ويشترطان v2. أما `uninstall` فيعمل حتى لو أزيل OpenCode لاحقاً. لا يثبت هذا المشروع OpenCode أو يستبدله أو يزيله.

## استهداف مشروع مختلف

```bash
curl -fsSL https://raw.githubusercontent.com/Alqudimi/ather-agents/main/install.sh | bash -s -- install --project /absolute/path/to/project
```

يجب أن يكون المسار لمجلد موجود. لا يثبت السكربت في جذر نظام الملفات أو مجلد المنزل. إذا مررت `--project` فسيستخدمه السكربت بدلاً من مجلد الطرفية الحالي.

## إعداد عمق التفويض

افتراضياً يضبط التثبيت `experimental.subagent_depth` على `2` لتفعيل التسلسل المقصود:

```text
orchestrator → قائد الفريق → الاختصاصي
```

لتثبيت ملفات الوكلاء دون تعديل إعداد OpenCode:

```bash
curl -fsSL https://raw.githubusercontent.com/Alqudimi/ather-agents/main/install.sh | bash -s -- install --no-depth-2
```

الخيار لا يغير عمق التفويض الحالي. إذا كان ملف الإعداد JSONC أو كان اختيار الإعداد الفعّال ملتبساً، قد يرفض المثبّت تعديل الإعداد؛ استخدم `--no-depth-2` ثم ادمج المفتاح يدوياً. لا يستبدل السكربت إعدادات المشروع العامة أو `default_agent`.

## ملفات المشروع التي ينشئها

- ملفات الوكلاء تحت `<project>/.opencode/agents/`.
- `opencode.json` عند عدم وجود ملف إعداد فعّال، أو تعديل ملف JSON صارم موجود لإضافة الإعداد، إلا مع `--no-depth-2`.
- سجل ملكية ونسخة إعداد احتياطية في `${XDG_STATE_HOME:-$HOME/.local/state}/opencode-agent-pack/<project-key>/`.

إذا كانت ملفات وكيل موجودة ومطابقة تماماً، يتركها السكربت كما هي ولا يعتبرها ملكاً له؛ لذلك لن يحذفها أثناء الإزالة. وإذا اختلفت الملفات الموجودة، يتوقف ويرفض الكتابة فوقها.

## ما الذي يتغير وما لا يتغير

المثبت لا يحدد الوكيل الافتراضي، ولا يوسع الصلاحيات العامة، ولا يثبت الأطر البرمجية المذكورة في ملفات الوكلاء، ولا يضيف مزود نماذج أو مفاتيح، ولا يحرر ملفات بدء الصدفة، ولا يعدل CLI أو بيانات المستخدم خارج إعداد المشروع ذي الصلة.

## الإزالة والتراجع

شغّل `uninstall` من مجلد المشروع نفسه، أو حدد المسار صراحة:

```bash
curl -fsSL https://raw.githubusercontent.com/Alqudimi/ather-agents/main/install.sh | bash -s -- uninstall --project /absolute/path/to/project
```

يحذف فقط ملفات الوكلاء التي أضافها المثبت وما زالت مطابقة لبصماتها المسجلة. إذا عدلت ملفاً بعد التثبيت، يحافظ عليه ويحتفظ بسجل الحالة ليوضح ما تعذر تنظيفه. الإعداد الذي أنشأه يحذف فقط إذا لم يتغير؛ والإعداد السابق الذي عدله يستعاد من نسخة احتياطية إذا أمكن التحقق منها. لا يحذف `uninstall` برنامج OpenCode نفسه.

## تشغيل السكربت من نسخة محلية

بعد استنساخ المستودع أو تنزيله:

```bash
python3 scripts/install-opencode-v2.py install --project /absolute/path/to/project
python3 scripts/install-opencode-v2.py verify --project /absolute/path/to/project
python3 scripts/install-opencode-v2.py uninstall --project /absolute/path/to/project
```

يجب أن يكون OpenCode v2 موجوداً عند التثبيت والتحقق. ويمكن إزالة ملفات الوكلاء من دون CLI باستخدام أمر `uninstall`.

## التحقق اليدوي

- نفّذ `opencode --version` وتأكد أن الإصدار يبدأ بـ `2.`.
- نفّذ `opencode debug agents` من جذر المشروع وتأكد من ظهور `orchestrator` والوكلاء المقصودين.
- راجع `.opencode/agents/` و`opencode.json` أو إعداد المشروع الفعّال.
- إذا غيّرت ملفات الوكلاء يدوياً، لا تتوقع أن يطابقها فحص سلامة الحزمة حرفياً.
